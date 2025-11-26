#!/usr/bin/env pwsh
# ============================================================================
# Get Database Connection Info
# ============================================================================
# Retrieves connection information for existing PostgreSQL databases
# ============================================================================

param(
    [Parameter(Mandatory=$false)]
    [string]$ServerName = "",
    
    [Parameter(Mandatory=$false)]
    [string]$DatabaseName = "dnd_initiative",
    
    [Parameter(Mandatory=$false)]
    [string]$AdminUser = "dbadmin"
)

$ErrorActionPreference = 'Stop'
$env:PYTHONWARNINGS = 'ignore'

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   PostgreSQL Connection Information" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$resourceGroup = "BCSAI2025-DEVOPS-STUDENTS-A"

# ============================================================================
# Select PostgreSQL Server
# ============================================================================

if ([string]::IsNullOrEmpty($ServerName)) {
    Write-Host "Available PostgreSQL Servers:" -ForegroundColor Cyan
    Write-Host ""
    
    $servers = az postgres flexible-server list --resource-group $resourceGroup --output json 2>$null | ConvertFrom-Json
    
    for ($i = 0; $i -lt $servers.Count; $i++) {
        $server = $servers[$i]
        Write-Host "  [$i] $($server.name)" -ForegroundColor White
        Write-Host "      Location: $($server.location)" -ForegroundColor Gray
        Write-Host "      Tier: $($server.sku.tier) / $($server.sku.name)" -ForegroundColor Gray
        Write-Host ""
    }
    
    $selection = Read-Host "Select server number"
    $ServerName = $servers[[int]$selection].name
}

Write-Host ""
Write-Host "Selected Server: $ServerName" -ForegroundColor Cyan

# ============================================================================
# List Existing Databases
# ============================================================================

Write-Host ""
Write-Host "Retrieving databases..." -ForegroundColor Yellow
Write-Host ""

try {
    $existingDbs = az postgres flexible-server db list `
        --resource-group $resourceGroup `
        --server-name $ServerName `
        --output json 2>$null | ConvertFrom-Json
    
    Write-Host "Existing databases on ${ServerName}:" -ForegroundColor Cyan
    foreach ($db in $existingDbs) {
        Write-Host "  - $($db.name)" -ForegroundColor White
    }
    Write-Host ""
    
    $dbExists = $existingDbs | Where-Object { $_.name -eq $DatabaseName }
    
    if (-not $dbExists) {
        Write-Host "[INFO] Database '$DatabaseName' does not exist yet" -ForegroundColor Yellow
        Write-Host "[INFO] You can create it manually or use setup-database.ps1" -ForegroundColor Yellow
        Write-Host ""
    }
} catch {
    Write-Host "[WARNING] Could not list databases" -ForegroundColor Yellow
}

# ============================================================================
# Get Connection Info
# ============================================================================

Write-Host "Retrieving connection information..." -ForegroundColor Yellow
Write-Host ""

try {
    $server = az postgres flexible-server show `
        --resource-group $resourceGroup `
        --name $ServerName `
        --output json 2>$null | ConvertFrom-Json

    $serverHost = $server.fullyQualifiedDomainName

    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "              CONNECTION DETAILS" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Server Name: " -NoNewline
    Write-Host $ServerName -ForegroundColor White
    Write-Host "  Host: " -NoNewline
    Write-Host $serverHost -ForegroundColor White
    Write-Host "  Database: " -NoNewline
    Write-Host $DatabaseName -ForegroundColor White
    Write-Host "  Admin User: " -NoNewline
    Write-Host $AdminUser -ForegroundColor White
    Write-Host "  Port: " -NoNewline
    Write-Host "5432" -ForegroundColor White
    Write-Host ""
    Write-Host "  CONNECTION STRING:" -ForegroundColor Yellow
    Write-Host "  ------------------------------------------------------------" -ForegroundColor DarkGray
    $connectionString = "postgresql://${AdminUser}:YOUR_PASSWORD@${serverHost}/${DatabaseName}?sslmode=require"
    Write-Host "  $connectionString" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  FOR GITHUB SECRETS (DATABASE_URL):" -ForegroundColor Yellow
    Write-Host "  ------------------------------------------------------------" -ForegroundColor DarkGray
    Write-Host "  postgresql://${AdminUser}:YOUR_PASSWORD@${serverHost}/${DatabaseName}?sslmode=require" -ForegroundColor White
    Write-Host ""
    Write-Host "  Replace YOUR_PASSWORD with the actual admin password" -ForegroundColor Gray
    Write-Host "  Replace '$DatabaseName' if using a different database name" -ForegroundColor Gray
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan

    # Save to file
    @{
        serverName = $ServerName
        host = $serverHost
        database = $DatabaseName
        adminUser = $AdminUser
        port = 5432
        connectionString = "postgresql://${AdminUser}:PASSWORD@${serverHost}/${DatabaseName}?sslmode=require"
    } | ConvertTo-Json | Out-File -FilePath "database-connection.json"

    Write-Host ""
    Write-Host "[OK] Connection details saved to: database-connection.json" -ForegroundColor Green
    Write-Host ""
    
} catch {
    Write-Host "[ERROR] Failed to retrieve server information!" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}
