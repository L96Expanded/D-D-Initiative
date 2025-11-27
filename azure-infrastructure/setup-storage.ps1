#!/usr/bin/env pwsh
# ============================================================================
# Azure Storage Account Setup for Image Uploads
# ============================================================================
# Creates Azure Storage Account and Blob Container for creature images
# ============================================================================

param(
    [Parameter(Mandatory=$false)]
    [string]$StorageAccountName = "",
    
    [Parameter(Mandatory=$false)]
    [string]$ResourceGroup = "BCSAI2025-DEVOPS-STUDENTS-A",
    
    [Parameter(Mandatory=$false)]
    [string]$Location = "canadacentral",
    
    [Parameter(Mandatory=$false)]
    [string]$ContainerName = "creature-images"
)

$ErrorActionPreference = 'Stop'
$env:PYTHONWARNINGS = 'ignore'

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   Azure Storage Setup for Image Uploads" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Generate storage account name if not provided
if ([string]::IsNullOrEmpty($StorageAccountName)) {
    $randomSuffix = Get-Random -Minimum 1000 -Maximum 9999
    $StorageAccountName = "dndinitiative$randomSuffix"
    Write-Host "Generated storage account name: $StorageAccountName" -ForegroundColor Yellow
}

Write-Host "Resource Group: $ResourceGroup" -ForegroundColor White
Write-Host "Storage Account: $StorageAccountName" -ForegroundColor White
Write-Host "Container: $ContainerName" -ForegroundColor White
Write-Host ""

# ============================================================================
# Create Storage Account
# ============================================================================

Write-Host "Checking if storage account exists..." -ForegroundColor Yellow
Write-Host ""

$existingAccount = az storage account show `
    --name $StorageAccountName `
    --resource-group $ResourceGroup `
    --output json 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "[INFO] Storage account already exists" -ForegroundColor Cyan
} else {
    Write-Host "Creating storage account..." -ForegroundColor Yellow
    Write-Host "This may take 1-2 minutes..." -ForegroundColor Gray
    Write-Host ""
    
    try {
        az storage account create `
            --name $StorageAccountName `
            --resource-group $ResourceGroup `
            --location $Location `
            --sku Standard_LRS `
            --kind StorageV2 `
            --access-tier Hot `
            --allow-blob-public-access true `
            --output none 2>$null
        
        Write-Host "[OK] Storage account created!" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Failed to create storage account!" -ForegroundColor Red
        Write-Host "Error: $_" -ForegroundColor Red
        exit 1
    }
}

# ============================================================================
# Get Connection String
# ============================================================================

Write-Host ""
Write-Host "Retrieving connection string..." -ForegroundColor Yellow
Write-Host ""

$connectionString = az storage account show-connection-string `
    --name $StorageAccountName `
    --resource-group $ResourceGroup `
    --output tsv 2>$null

if ([string]::IsNullOrEmpty($connectionString)) {
    Write-Host "[ERROR] Failed to retrieve connection string!" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Connection string retrieved" -ForegroundColor Green

# ============================================================================
# Create Blob Container
# ============================================================================

Write-Host ""
Write-Host "Creating blob container..." -ForegroundColor Yellow
Write-Host ""

try {
    az storage container create `
        --name $ContainerName `
        --account-name $StorageAccountName `
        --public-access blob `
        --connection-string $connectionString `
        --output none 2>$null
    
    Write-Host "[OK] Blob container created!" -ForegroundColor Green
} catch {
    Write-Host "[INFO] Container may already exist" -ForegroundColor Yellow
}

# ============================================================================
# Configure CORS (for web uploads)
# ============================================================================

Write-Host ""
Write-Host "Configuring CORS..." -ForegroundColor Yellow
Write-Host ""

try {
    az storage cors add `
        --services b `
        --methods GET POST PUT DELETE OPTIONS `
        --origins "*" `
        --allowed-headers "*" `
        --exposed-headers "*" `
        --max-age 3600 `
        --account-name $StorageAccountName `
        --connection-string $connectionString `
        --output none 2>$null
    
    Write-Host "[OK] CORS configured" -ForegroundColor Green
} catch {
    Write-Host "[INFO] CORS may already be configured" -ForegroundColor Yellow
}

# ============================================================================
# Summary
# ============================================================================

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "              SETUP COMPLETE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  STORAGE DETAILS:" -ForegroundColor Yellow
Write-Host "  ------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host "  Account Name: " -NoNewline
Write-Host $StorageAccountName -ForegroundColor White
Write-Host "  Container: " -NoNewline
Write-Host $ContainerName -ForegroundColor White
Write-Host "  Location: " -NoNewline
Write-Host $Location -ForegroundColor White
Write-Host ""
Write-Host "  CONNECTION STRING:" -ForegroundColor Yellow
Write-Host "  ------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host "  $connectionString" -ForegroundColor Cyan
Write-Host ""
Write-Host "  ADD TO GITHUB SECRETS:" -ForegroundColor Yellow
Write-Host "  ------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host "  Name: AZURE_STORAGE_CONNECTION_STRING" -ForegroundColor White
Write-Host "  Value: (connection string above)" -ForegroundColor White
Write-Host ""
Write-Host "  UPDATE APP SERVICE SETTINGS:" -ForegroundColor Yellow
Write-Host "  ------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host "  Run this command:" -ForegroundColor White
Write-Host ""
Write-Host "  az webapp config appsettings set \\" -ForegroundColor Cyan
Write-Host "    --name dnd-initiative-prod \\" -ForegroundColor Cyan
Write-Host "    --resource-group $ResourceGroup \\" -ForegroundColor Cyan
Write-Host "    --settings AZURE_STORAGE_CONNECTION_STRING=`"$connectionString`"" -ForegroundColor Cyan
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Save to file
@{
    storageAccountName = $StorageAccountName
    containerName = $ContainerName
    connectionString = $connectionString
} | ConvertTo-Json | Out-File -FilePath "storage-config.json"

Write-Host "[OK] Configuration saved to: storage-config.json" -ForegroundColor Green
Write-Host ""
