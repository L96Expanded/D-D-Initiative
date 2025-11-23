#!/usr/bin/env pwsh
# ============================================================================
# Azure Infrastructure Deployment Script
# ============================================================================
# This script deploys all Azure infrastructure using Bicep templates
# Run this ONCE to set up your Azure environment
# ============================================================================

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('dev', 'staging', 'prod')]
    [string]$Environment = 'prod',
    
    [Parameter(Mandatory=$false)]
    [string]$Location = 'eastus',
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipConfirmation
)

# Set error action preference
$ErrorActionPreference = 'Stop'

# ============================================================================
# Configuration
# ============================================================================

$ProjectName = "dnd-initiative"
$SubscriptionName = "" # Will be set interactively

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Azure Infrastructure Deployment for D&D Initiative       ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Environment: " -NoNewline
Write-Host $Environment -ForegroundColor Yellow
Write-Host "  Location: " -NoNewline
Write-Host $Location -ForegroundColor Yellow
Write-Host ""

# ============================================================================
# Pre-flight Checks
# ============================================================================

Write-Host "[1/8] Running pre-flight checks..." -ForegroundColor Green
Write-Host ""

# Check if Azure CLI is installed
try {
    $azCheck = Get-Command az -ErrorAction Stop
    Write-Host "  ✓ Azure CLI installed" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Azure CLI not installed!" -ForegroundColor Red
    Write-Host "    Install from: https://aka.ms/installazurecliwindows" -ForegroundColor Yellow
    Write-Host "    After installing, RESTART PowerShell and run this script again" -ForegroundColor Yellow
    exit 1
}

# Check if logged in
try {
    $account = az account show --output json | ConvertFrom-Json
    Write-Host "  ✓ Logged in as: $($account.user.name)" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Not logged in to Azure" -ForegroundColor Red
    Write-Host "    Running 'az login'..." -ForegroundColor Yellow
    az login
}

# ============================================================================
# Select Subscription
# ============================================================================

Write-Host ""
Write-Host "[2/8] Selecting Azure subscription..." -ForegroundColor Green
Write-Host ""

$subscriptions = az account list --output json | ConvertFrom-Json

if ($subscriptions.Count -eq 1) {
    $SubscriptionName = $subscriptions[0].name
    Write-Host "  Using subscription: $SubscriptionName" -ForegroundColor Cyan
} else {
    Write-Host "  Available subscriptions:" -ForegroundColor Cyan
    for ($i = 0; $i -lt $subscriptions.Count; $i++) {
        Write-Host "    [$i] $($subscriptions[$i].name)" -ForegroundColor White
    }
    Write-Host ""
    $selection = Read-Host "  Select subscription number"
    $SubscriptionName = $subscriptions[[int]$selection].name
}

az account set --subscription $SubscriptionName
Write-Host "  ✓ Active subscription: $SubscriptionName" -ForegroundColor Green

# ============================================================================
# Gather Secrets
# ============================================================================

Write-Host ""
Write-Host "[3/8] Gathering secrets..." -ForegroundColor Green
Write-Host ""

Write-Host "  Enter database administrator password (min 8 chars, must include uppercase, lowercase, numbers):" -ForegroundColor Cyan
$dbPassword = Read-Host -AsSecureString
$dbPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($dbPassword))

Write-Host "  Enter FastAPI SECRET_KEY (or press Enter to generate):" -ForegroundColor Cyan
$secretKey = Read-Host
if ([string]::IsNullOrEmpty($secretKey)) {
    $secretKey = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 64 | ForEach-Object {[char]$_})
    Write-Host "    Generated secret key: $($secretKey.Substring(0, 20))..." -ForegroundColor Yellow
}

# ============================================================================
# Confirm Deployment
# ============================================================================

Write-Host ""
Write-Host "[4/8] Deployment summary..." -ForegroundColor Green
Write-Host ""
Write-Host "  Subscription: $SubscriptionName" -ForegroundColor White
Write-Host "  Environment: $Environment" -ForegroundColor White
Write-Host "  Location: $Location" -ForegroundColor White
Write-Host "  Resource Group: rg-$ProjectName-$Environment" -ForegroundColor White
Write-Host ""
Write-Host "  Resources to be created:" -ForegroundColor Cyan
Write-Host "    • Container Registry (SKU: Basic)" -ForegroundColor White
Write-Host "    • App Service Plan (SKU: B1)" -ForegroundColor White
Write-Host "    • Web App (Frontend)" -ForegroundColor White
Write-Host "    • Web App (Backend)" -ForegroundColor White
Write-Host "    • PostgreSQL Server (SKU: B1ms)" -ForegroundColor White
Write-Host "    • Application Insights" -ForegroundColor White
Write-Host "    • Log Analytics Workspace" -ForegroundColor White
Write-Host ""
Write-Host "  Estimated cost: ~`$35-40/month" -ForegroundColor Yellow
Write-Host ""

if (-not $SkipConfirmation) {
    $confirm = Read-Host "  Continue with deployment? (yes/no)"
    if ($confirm -ne "yes") {
        Write-Host "  Deployment cancelled" -ForegroundColor Yellow
        exit 0
    }
}

# ============================================================================
# Deploy Infrastructure
# ============================================================================

Write-Host ""
Write-Host "[5/8] Deploying infrastructure..." -ForegroundColor Green
Write-Host ""
Write-Host "  This may take 10-15 minutes..." -ForegroundColor Yellow
Write-Host ""

$deploymentName = "dnd-initiative-$Environment-$(Get-Date -Format 'yyyyMMdd-HHmmss')"

try {
    $deployment = az deployment sub create `
        --name $deploymentName `
        --location $Location `
        --template-file "azure-infrastructure/main.bicep" `
        --parameters environment=$Environment `
        --parameters dbAdminPassword=$dbPasswordPlain `
        --parameters secretKey=$secretKey `
        --output json | ConvertFrom-Json
    
    Write-Host "  ✓ Infrastructure deployed successfully!" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Deployment failed!" -ForegroundColor Red
    Write-Host "    Error: $_" -ForegroundColor Red
    exit 1
}

# ============================================================================
# Get Deployment Outputs
# ============================================================================

Write-Host ""
Write-Host "[6/8] Retrieving deployment outputs..." -ForegroundColor Green
Write-Host ""

$outputs = $deployment.properties.outputs

$resourceGroupName = $outputs.resourceGroupName.value
$acrLoginServer = $outputs.containerRegistryLoginServer.value
$frontendUrl = $outputs.frontendAppUrl.value
$backendUrl = $outputs.backendAppUrl.value
$dbHost = $outputs.databaseHost.value
$appInsightsKey = $outputs.appInsightsInstrumentationKey.value

Write-Host "  ✓ Retrieved deployment details" -ForegroundColor Green

# ============================================================================
# Configure Container Registry Access
# ============================================================================

Write-Host ""
Write-Host "[7/8] Configuring Container Registry access..." -ForegroundColor Green
Write-Host ""

# Enable admin user on ACR
$acrName = $acrLoginServer.Split('.')[0]
az acr update --name $acrName --admin-enabled true --output none

# Get ACR credentials
$acrCredentials = az acr credential show --name $acrName --output json | ConvertFrom-Json
$acrUsername = $acrCredentials.username
$acrPassword = $acrCredentials.passwords[0].value

Write-Host "  ✓ Container Registry configured" -ForegroundColor Green

# ============================================================================
# Display Summary
# ============================================================================

Write-Host ""
Write-Host "[8/8] Deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║              DEPLOYMENT SUCCESSFUL                          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "  RESOURCE DETAILS:" -ForegroundColor Yellow
Write-Host "  ────────────────────────────────────────────────────────" -ForegroundColor DarkGray
Write-Host "  Resource Group: " -NoNewline
Write-Host $resourceGroupName -ForegroundColor White
Write-Host "  Container Registry: " -NoNewline
Write-Host $acrLoginServer -ForegroundColor White
Write-Host "  Frontend URL: " -NoNewline
Write-Host "https://$frontendUrl" -ForegroundColor Cyan
Write-Host "  Backend URL: " -NoNewline
Write-Host "https://$backendUrl" -ForegroundColor Cyan
Write-Host "  Database Host: " -NoNewline
Write-Host $dbHost -ForegroundColor White
Write-Host ""
Write-Host "  GITHUB SECRETS (add these to your repository):" -ForegroundColor Yellow
Write-Host "  ────────────────────────────────────────────────────────" -ForegroundColor DarkGray
Write-Host "  AZURE_REGISTRY_NAME: " -NoNewline
Write-Host $acrName -ForegroundColor White
Write-Host "  AZURE_REGISTRY_USERNAME: " -NoNewline
Write-Host $acrUsername -ForegroundColor White
Write-Host "  AZURE_REGISTRY_PASSWORD: " -NoNewline
Write-Host $acrPassword.Substring(0, 20) -NoNewline -ForegroundColor White
Write-Host "..." -ForegroundColor White
Write-Host "  DATABASE_URL: " -NoNewline
Write-Host "postgresql://dbadmin:***@$dbHost/dnd_tracker?sslmode=require" -ForegroundColor White
Write-Host "  SECRET_KEY: " -NoNewline
Write-Host $secretKey.Substring(0, 20) -NoNewline -ForegroundColor White
Write-Host "..." -ForegroundColor White
Write-Host ""
Write-Host "  NEXT STEPS:" -ForegroundColor Yellow
Write-Host "  ────────────────────────────────────────────────────────" -ForegroundColor DarkGray
Write-Host "  1. Add GitHub secrets (see above)" -ForegroundColor White
Write-Host "  2. Create Azure service principal:" -ForegroundColor White
Write-Host "     az ad sp create-for-rbac --name 'github-actions-dnd' --role contributor --scopes /subscriptions/SUBSCRIPTION_ID/resourceGroups/$resourceGroupName --sdk-auth" -ForegroundColor Cyan
Write-Host "  3. Add AZURE_CREDENTIALS secret with the JSON output" -ForegroundColor White
Write-Host "  4. Push code to GitHub to trigger deployment" -ForegroundColor White
Write-Host "  5. Configure custom domain (see docs/AZURE_MIGRATION_GUIDE.md)" -ForegroundColor White
Write-Host ""
Write-Host "  📚 Full guide: docs/AZURE_MIGRATION_GUIDE.md" -ForegroundColor Cyan
Write-Host ""

# Save outputs to file
$outputFile = "azure-deployment-outputs.json"
@{
    resourceGroupName = $resourceGroupName
    acrLoginServer = $acrLoginServer
    acrName = $acrName
    acrUsername = $acrUsername
    frontendUrl = $frontendUrl
    backendUrl = $backendUrl
    databaseHost = $dbHost
    appInsightsKey = $appInsightsKey
    environment = $Environment
    deploymentDate = (Get-Date).ToString()
} | ConvertTo-Json | Out-File -FilePath $outputFile

Write-Host "  Deployment details saved to: $outputFile" -ForegroundColor Green
Write-Host ""
