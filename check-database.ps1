# Quick Database Status Check
# Run this in Azure Portal Cloud Shell or after installing Azure CLI

Write-Host "=== D&D Initiative Database Checker ===" -ForegroundColor Cyan
Write-Host ""

$resourceGroup = "BCSAI2025-DEVOPS-STUDENTS-A"
$appName = "dnd-initiative-prod"

# Check if logged in to Azure
try {
    az account show | Out-Null
    Write-Host "✓ Logged into Azure" -ForegroundColor Green
} catch {
    Write-Host "✗ Not logged into Azure. Run: az login" -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "Checking App Service configuration..." -ForegroundColor Yellow

# Check if DATABASE_URL is set
$databaseUrl = az webapp config appsettings list `
    --name $appName `
    --resource-group $resourceGroup `
    --query "[?name=='DATABASE_URL'].value" -o tsv

if ($databaseUrl) {
    Write-Host "✓ DATABASE_URL is configured" -ForegroundColor Green
    
    # Parse connection string (safely - don't show password)
    if ($databaseUrl -match "postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/([^?]+)") {
        $dbUser = $matches[1]
        $dbHost = $matches[3]
        $dbPort = $matches[4]
        $dbName = $matches[5]
        
        Write-Host "  Database User: $dbUser" -ForegroundColor Gray
        Write-Host "  Database Host: $dbHost" -ForegroundColor Gray
        Write-Host "  Database Port: $dbPort" -ForegroundColor Gray
        Write-Host "  Database Name: $dbName" -ForegroundColor Gray
        
        # Extract server name
        if ($dbHost -match "^([^.]+)\.postgres") {
            $serverName = $matches[1]
            Write-Host "  Server Name: $serverName" -ForegroundColor Gray
        }
    }
    
    # Check if it has SSL mode
    if ($databaseUrl -like "*sslmode=require*") {
        Write-Host "✓ SSL mode is configured" -ForegroundColor Green
    } else {
        Write-Host "✗ WARNING: Missing ?sslmode=require" -ForegroundColor Red
    }
} else {
    Write-Host "✗ DATABASE_URL is NOT configured!" -ForegroundColor Red
}

Write-Host ""
Write-Host "Checking for PostgreSQL servers..." -ForegroundColor Yellow

# List PostgreSQL servers
$servers = az postgres flexible-server list `
    --resource-group $resourceGroup `
    --query "[].{Name:name, State:state, Location:location}" -o json | ConvertFrom-Json

if ($servers.Count -eq 0) {
    Write-Host "✗ No PostgreSQL servers found in resource group!" -ForegroundColor Red
    Write-Host "  You need to create a database server first." -ForegroundColor Yellow
} else {
    Write-Host "✓ Found $($servers.Count) PostgreSQL server(s):" -ForegroundColor Green
    foreach ($server in $servers) {
        Write-Host "  - $($server.Name) [$($server.State)] in $($server.Location)" -ForegroundColor Gray
        
        # Check firewall rules
        $firewallRules = az postgres flexible-server firewall-rule list `
            --resource-group $resourceGroup `
            --server-name $server.Name `
            --query "[].{Name:name, Start:startIpAddress, End:endIpAddress}" -o json | ConvertFrom-Json
        
        if ($firewallRules) {
            $azureRule = $firewallRules | Where-Object { $_.Start -eq "0.0.0.0" -and $_.End -eq "0.0.0.0" }
            if ($azureRule) {
                Write-Host "    ✓ Azure services are allowed" -ForegroundColor Green
            } else {
                Write-Host "    ✗ Azure services NOT allowed (may block App Service)" -ForegroundColor Red
            }
        } else {
            Write-Host "    ✗ No firewall rules configured" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "Testing health endpoint..." -ForegroundColor Yellow

try {
    $health = Invoke-RestMethod -Uri "https://$appName.azurewebsites.net/api/health" -TimeoutSec 10
    
    if ($health.status -eq "healthy") {
        Write-Host "✓ Backend is HEALTHY" -ForegroundColor Green
        Write-Host "  Database status: $($health.database.status)" -ForegroundColor Gray
    } elseif ($health.status -eq "unhealthy") {
        Write-Host "✗ Backend is UNHEALTHY" -ForegroundColor Red
        Write-Host "  Database status: $($health.database.status)" -ForegroundColor Red
        Write-Host "  Error: $($health.database.message)" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Could not reach health endpoint" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Summary ===" -ForegroundColor Cyan

if (-not $databaseUrl) {
    Write-Host "ACTION REQUIRED: Set DATABASE_URL in App Service Configuration" -ForegroundColor Yellow
}

if ($servers.Count -eq 0) {
    Write-Host "ACTION REQUIRED: Create PostgreSQL server" -ForegroundColor Yellow
    Write-Host "  Option 1: Use Azure Portal to create Azure Database for PostgreSQL" -ForegroundColor Gray
    Write-Host "  Option 2: Deploy using Bicep: cd azure-infrastructure; az deployment group create..." -ForegroundColor Gray
}

Write-Host ""
Write-Host "For detailed help, see: FIX_503_DATABASE_ERROR.md" -ForegroundColor Cyan
