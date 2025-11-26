#!/usr/bin/env pwsh
# ============================================================================
# Azure App Service Deployment Script
# ============================================================================
# This script uses App Service credentials to deploy your application
# ============================================================================

param(
    [Parameter(Mandatory=$false)]
    [string]$CredentialsFile = "app-service-credentials.json",
    
    [Parameter(Mandatory=$false)]
    [string]$ConfigFile = "azure-config.json",
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipConfirmation
)

$ErrorActionPreference = 'Stop'

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   Azure App Service Deployment" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# Load Configuration Files
# ============================================================================

Write-Host "[1/5] Loading configuration..." -ForegroundColor Green
Write-Host ""

if (-not (Test-Path $CredentialsFile)) {
    Write-Host "  [ERROR] Credentials file not found: $CredentialsFile" -ForegroundColor Red
    Write-Host "  Please create the file and fill in your Azure credentials" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path $ConfigFile)) {
    Write-Host "  [ERROR] Config file not found: $ConfigFile" -ForegroundColor Red
    Write-Host "  Please create the file and fill in your configuration" -ForegroundColor Yellow
    exit 1
}

$credentials = Get-Content $CredentialsFile | ConvertFrom-Json
$config = Get-Content $ConfigFile | ConvertFrom-Json

# Validate config
if ($config.appServiceName -eq "YOUR_APP_SERVICE_NAME_HERE") {
    Write-Host "  [ERROR] Please fill in appServiceName in $ConfigFile" -ForegroundColor Red
    exit 1
}
if ($config.databaseAdminPassword -eq "YOUR_DB_PASSWORD_HERE") {
    Write-Host "  [ERROR] Please fill in databaseAdminPassword in $ConfigFile" -ForegroundColor Red
    exit 1
}
if ($config.secretKey -eq "YOUR_SECRET_KEY_HERE") {
    Write-Host "  [ERROR] Please fill in secretKey in $ConfigFile" -ForegroundColor Red
    exit 1
}

Write-Host "  [OK] Configuration loaded" -ForegroundColor Green
Write-Host "  App Service: $($config.appServiceName)" -ForegroundColor Cyan
Write-Host "  Location: $($config.location)" -ForegroundColor Cyan
Write-Host "  Environment: $($config.environment)" -ForegroundColor Cyan

# ============================================================================
# Login with Service Principal
# ============================================================================

Write-Host ""
Write-Host "[2/5] Logging in with service principal..." -ForegroundColor Green
Write-Host ""

try {
    az login --service-principal `
        --username $credentials.appId `
        --password $credentials.password `
        --tenant $credentials.tenant `
        --output none
    
    Write-Host "  [OK] Successfully authenticated" -ForegroundColor Green
} catch {
    Write-Host "  [ERROR] Login failed!" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Red
    exit 1
}

# ============================================================================
# Find or Create App Service
# ============================================================================

Write-Host ""
Write-Host "[3/5] Setting up App Service..." -ForegroundColor Green
Write-Host ""

$resourceGroupName = "BCSAI2025-DEVOPS-STUDENTS-A"
$appServicePlan = "DnD_Initiative"

# Use app name from config
$appName = $config.appServiceName

Write-Host "  App Name: $appName" -ForegroundColor Cyan
Write-Host "  Resource Group: $resourceGroupName" -ForegroundColor Cyan
Write-Host "  App Service Plan: $appServicePlan" -ForegroundColor Cyan

# Check if app exists
Write-Host "  Checking if App Service exists..." -ForegroundColor Yellow

# Completely suppress stderr and warnings
$env:PYTHONWARNINGS = "ignore"
$ErrorActionPreference = 'Continue'

$checkResult = az webapp show --name $appName --resource-group $resourceGroupName --output json 2>$null
$appExists = $LASTEXITCODE -eq 0

$ErrorActionPreference = 'Stop'

if (-not $appExists) {
    Write-Host "  App Service does not exist, creating..." -ForegroundColor Yellow
    
    # Capture both stdout and stderr for detailed error messages
    $ErrorActionPreference = 'Continue'
    $createOutput = az webapp create `
        --name $appName `
        --resource-group $resourceGroupName `
        --plan $appServicePlan `
        --runtime "PYTHON:3.11" `
        --output json 2>&1
    
    $createSuccess = $LASTEXITCODE -eq 0
    $ErrorActionPreference = 'Stop'
    
    if ($createSuccess) {
        Write-Host "  [OK] App Service created: $appName" -ForegroundColor Green
        # Filter out warnings and parse JSON
        $jsonOutput = $createOutput | Where-Object { $_ -notmatch "UserWarning|cryptography" } | Out-String
        $appService = $jsonOutput | ConvertFrom-Json
    } else {
        Write-Host "  [ERROR] Failed to create App Service!" -ForegroundColor Red
        Write-Host "" -ForegroundColor Red
        Write-Host "  Details:" -ForegroundColor Yellow
        Write-Host "  - App Name: $appName" -ForegroundColor White
        Write-Host "  - Resource Group: $resourceGroupName" -ForegroundColor White
        Write-Host "  - App Service Plan: $appServicePlan" -ForegroundColor White
        Write-Host "  - Runtime: PYTHON:3.11" -ForegroundColor White
        Write-Host "" -ForegroundColor Red
        Write-Host "  Error Output:" -ForegroundColor Yellow
        $createOutput | Where-Object { $_ -notmatch "UserWarning|cryptography|D:\\a\\_work" } | ForEach-Object {
            Write-Host "  $_" -ForegroundColor Red
        }
        Write-Host "" -ForegroundColor Red
        Write-Host "  Possible causes:" -ForegroundColor Yellow
        Write-Host "  - App name '$appName' may already be taken globally" -ForegroundColor White
        Write-Host "  - Insufficient permissions in resource group" -ForegroundColor White
        Write-Host "  - App Service Plan may not support the runtime" -ForegroundColor White
        exit 1
    }
} else {
    Write-Host "  [OK] App Service already exists: $appName" -ForegroundColor Green
    $jsonOutput = $checkResult | Out-String
    $appService = $jsonOutput | ConvertFrom-Json
}

# ============================================================================
# Build and Deploy Docker Images
# ============================================================================

Write-Host ""
Write-Host "[4/5] Building and deploying application..." -ForegroundColor Green
Write-Host ""

if (-not $SkipConfirmation) {
    $confirm = Read-Host "  Deploy application to $($config.appServiceName)? (yes/no)"
    if ($confirm -ne "yes") {
        Write-Host "  Deployment cancelled" -ForegroundColor Yellow
        exit 0
    }
}

Write-Host "  Building backend Docker image..." -ForegroundColor Yellow

# Navigate to backend directory
Push-Location "..\backend"

try {
    # Build backend
    docker build -t $config.appServiceName`:backend .
    
    Write-Host "  [OK] Backend image built" -ForegroundColor Green
} catch {
    Write-Host "  [ERROR] Failed to build backend!" -ForegroundColor Red
    Pop-Location
    exit 1
} finally {
    Pop-Location
}

Write-Host "  Building frontend Docker image..." -ForegroundColor Yellow

# Navigate to frontend directory
Push-Location "..\frontend"

try {
    # Build frontend
    docker build -t $config.appServiceName`:frontend .
    
    Write-Host "  [OK] Frontend image built" -ForegroundColor Green
} catch {
    Write-Host "  [ERROR] Failed to build frontend!" -ForegroundColor Red
    Pop-Location
    exit 1
} finally {
    Pop-Location
}

# Configure App Service environment variables
Write-Host "  Configuring App Service environment..." -ForegroundColor Yellow

try {
    az webapp config appsettings set `
        --name $config.appServiceName `
        --resource-group $resourceGroupName `
        --settings `
            DATABASE_URL="postgresql://dbadmin:$($config.databaseAdminPassword)@your-db-host/dnd_tracker?sslmode=require" `
            SECRET_KEY=$config.secretKey `
            ENVIRONMENT=$config.environment `
        --output none
    
    Write-Host "  [OK] Environment configured" -ForegroundColor Green
} catch {
    Write-Host "  [ERROR] Failed to configure environment!" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Red
    exit 1
}

# ============================================================================
# Display Summary
# ============================================================================

Write-Host ""
Write-Host "[5/5] Deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "              DEPLOYMENT SUCCESSFUL" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  APP SERVICE DETAILS:" -ForegroundColor Yellow
Write-Host "  ------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host "  App Service: " -NoNewline
Write-Host $config.appServiceName -ForegroundColor White
Write-Host "  Resource Group: " -NoNewline
Write-Host $resourceGroupName -ForegroundColor White
Write-Host "  URL: " -NoNewline
Write-Host "https://$($appService.defaultHostName)" -ForegroundColor Cyan
Write-Host ""
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
