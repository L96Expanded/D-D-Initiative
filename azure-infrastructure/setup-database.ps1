#!/usr/bin/env pwsh
# ============================================================================
# Database Setup Script
# ============================================================================
# Creates a PostgreSQL database for D&D Initiative Tracker
# ============================================================================

param(
    [Parameter(Mandatory=$false)]
    [string]$ServerName = "",
    
    [Parameter(Mandatory=$false)]
    [string]$DatabaseName = "dnd_initiative",
    
    [Parameter(Mandatory=$false)]
    [string]$AdminUser = "dbadmin",
    
    [Parameter(Mandatory=$false)]
    [string]$AdminPassword = ""
)

$ErrorActionPreference = 'Stop'
$env:PYTHONWARNINGS = 'ignore'

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   PostgreSQL Database Setup" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$resourceGroup = "BCSAI2025-DEVOPS-STUDENTS-A"

# ============================================================================
# Select PostgreSQL Server
# ============================================================================

if ([string]::IsNullOrEmpty($ServerName)) {
    Write-Host "Available PostgreSQL Servers:" -ForegroundColor Cyan
    Write-Host ""
    
    $servers = az postgres flexible-server list --resource-group $resourceGroup --output json | ConvertFrom-Json
    
    for ($i = 0; $i -lt $servers.Count; $i++) {
        $server = $servers[$i]
        Write-Host "  [$i] $($server.name)" -ForegroundColor White
        Write-Host "      Location: $($server.location)" -ForegroundColor Gray
        Write-Host "      Tier: $($server.sku.tier) / $($server.sku.name)" -ForegroundColor Gray
        Write-Host ""
    }
    
    $selection = Read-Host "Select server number (or press Enter to create new)"
    
    if ([string]::IsNullOrEmpty($selection)) {
        Write-Host ""
        Write-Host "[OPTION] Create New PostgreSQL Server" -ForegroundColor Yellow
        Write-Host ""
        
        $ServerName = Read-Host "Enter server name (e.g., dnd-initiative-db)"
        $createNew = $true
    } else {
        $ServerName = $servers[[int]$selection].name
        $createNew = $false
    }
}

Write-Host ""
Write-Host "Selected Server: $ServerName" -ForegroundColor Cyan

# ============================================================================
# Create New Server (if needed)
# ============================================================================

if ($createNew) {
    Write-Host ""
    Write-Host "Creating new PostgreSQL server..." -ForegroundColor Yellow
    Write-Host ""
    
    if ([string]::IsNullOrEmpty($AdminPassword)) {
        Write-Host "Enter administrator password (min 8 chars):" -ForegroundColor Cyan
        $securePassword = Read-Host -AsSecureString
        $AdminPassword = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword))
    }
    
    try {
        az postgres flexible-server create `
            --name $ServerName `
            --resource-group $resourceGroup `
            --location "West Europe" `
            --admin-user $AdminUser `
            --admin-password $AdminPassword `
            --sku-name Standard_B1ms `
            --tier Burstable `
            --storage-size 32 `
            --version 17 `
            --public-access All `
            --output none
        
        Write-Host "[OK] PostgreSQL server created!" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Failed to create server!" -ForegroundColor Red
        Write-Host "Error: $_" -ForegroundColor Red
        exit 1
    }
}

# ============================================================================
# Create Database
# ============================================================================

Write-Host ""
Write-Host "Creating database: $DatabaseName..." -ForegroundColor Yellow
Write-Host ""

try {
    # Check if database exists
    $existingDbs = az postgres flexible-server db list `
        --resource-group $resourceGroup `
        --server-name $ServerName `
        --output json | ConvertFrom-Json
    
    $dbExists = $existingDbs | Where-Object { $_.name -eq $DatabaseName }
    
    if ($dbExists) {
        Write-Host "[INFO] Database already exists: $DatabaseName" -ForegroundColor Yellow
        $overwrite = Read-Host "Drop and recreate? (yes/no)"
        
        if ($overwrite -eq "yes") {
            az postgres flexible-server db delete `
                --resource-group $resourceGroup `
                --server-name $ServerName `
                --database-name $DatabaseName `
                --yes `
                --output none
            
            Write-Host "[OK] Database dropped" -ForegroundColor Green
        } else {
            Write-Host "[INFO] Using existing database" -ForegroundColor Cyan
            $dbExists = $false  # Skip creation
        }
    }
    
    if (-not $dbExists -or $overwrite -eq "yes") {
        az postgres flexible-server db create `
            --resource-group $resourceGroup `
            --server-name $ServerName `
            --database-name $DatabaseName `
            --output none
        
        Write-Host "[OK] Database created!" -ForegroundColor Green
    }
} catch {
    Write-Host "[ERROR] Failed to create database!" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}

# ============================================================================
# Configure Firewall
# ============================================================================

Write-Host ""
Write-Host "Configuring firewall rules..." -ForegroundColor Yellow
Write-Host ""

try {
    # Allow Azure services
    az postgres flexible-server firewall-rule create `
        --resource-group $resourceGroup `
        --name $ServerName `
        --rule-name AllowAzureServices `
        --start-ip-address 0.0.0.0 `
        --end-ip-address 0.0.0.0 `
        --output none 2>$null
    
    Write-Host "[OK] Firewall configured" -ForegroundColor Green
} catch {
    Write-Host "[INFO] Firewall rule may already exist" -ForegroundColor Yellow
}

# ============================================================================
# Get Connection Info
# ============================================================================

Write-Host ""
Write-Host "Retrieving connection information..." -ForegroundColor Yellow
Write-Host ""

$server = az postgres flexible-server show `
    --resource-group $resourceGroup `
    --name $ServerName `
    --output json | ConvertFrom-Json

$host = $server.fullyQualifiedDomainName

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "              DATABASE READY" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  CONNECTION DETAILS:" -ForegroundColor Yellow
Write-Host "  ------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host "  Host: " -NoNewline
Write-Host $host -ForegroundColor White
Write-Host "  Database: " -NoNewline
Write-Host $DatabaseName -ForegroundColor White
Write-Host "  Admin User: " -NoNewline
Write-Host $AdminUser -ForegroundColor White
Write-Host "  Port: " -NoNewline
Write-Host "5432" -ForegroundColor White
Write-Host ""
Write-Host "  CONNECTION STRING:" -ForegroundColor Yellow
Write-Host "  ------------------------------------------------------------" -ForegroundColor DarkGray
$connectionString = "postgresql://${AdminUser}:YOUR_PASSWORD@${host}/${DatabaseName}?sslmode=require"
Write-Host "  $connectionString" -ForegroundColor Cyan
Write-Host ""
Write-Host "  FOR GITHUB SECRETS (DATABASE_URL):" -ForegroundColor Yellow
Write-Host "  ------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host "  postgresql://${AdminUser}:YOUR_PASSWORD@${host}/${DatabaseName}?sslmode=require" -ForegroundColor White
Write-Host ""
Write-Host "  Replace YOUR_PASSWORD with the actual admin password" -ForegroundColor Gray
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan

# Save to file
@{
    host = $host
    database = $DatabaseName
    adminUser = $AdminUser
    port = 5432
    connectionString = "postgresql://${AdminUser}:PASSWORD@${host}/${DatabaseName}?sslmode=require"
} | ConvertTo-Json | Out-File -FilePath "database-connection.json"

Write-Host ""
Write-Host "[OK] Connection details saved to: database-connection.json" -ForegroundColor Green
Write-Host ""
