#!/usr/bin/env pwsh
# ============================================================================
# Custom Domain Configuration Script
# ============================================================================
# Binds custom domain to Azure App Service and enables SSL
# ============================================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$DomainName,
    
    [Parameter(Mandatory=$false)]
    [string]$AppName = "dnd-initiative-prod",
    
    [Parameter(Mandatory=$false)]
    [string]$ResourceGroup = "BCSAI2025-DEVOPS-STUDENTS-A"
)

$ErrorActionPreference = 'Stop'
$env:PYTHONWARNINGS = 'ignore'

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   Custom Domain Configuration" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "App Service: $AppName" -ForegroundColor White
Write-Host "Domain: $DomainName" -ForegroundColor White
Write-Host ""

# ============================================================================
# Check DNS Propagation
# ============================================================================

Write-Host "Checking DNS configuration..." -ForegroundColor Yellow
Write-Host ""

try {
    $dnsResult = Resolve-DnsName $DomainName -Type A -ErrorAction SilentlyContinue
    
    if ($dnsResult) {
        Write-Host "[OK] DNS A record found: $($dnsResult.IPAddress)" -ForegroundColor Green
    } else {
        Write-Host "[WARNING] DNS A record not found yet. DNS may still be propagating." -ForegroundColor Yellow
        Write-Host "Expected IP: 20.48.204.5" -ForegroundColor Gray
    }
} catch {
    Write-Host "[WARNING] Could not resolve DNS. Continuing anyway..." -ForegroundColor Yellow
}

Write-Host ""

# ============================================================================
# Add Custom Domain
# ============================================================================

Write-Host "Adding custom domain to App Service..." -ForegroundColor Yellow
Write-Host ""

try {
    az webapp config hostname add `
        --webapp-name $AppName `
        --resource-group $ResourceGroup `
        --hostname $DomainName `
        --output none 2>$null
    
    Write-Host "[OK] Custom domain added!" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to add custom domain!" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Make sure DNS records are configured:" -ForegroundColor Yellow
    Write-Host "  A Record: @ -> 20.48.204.5" -ForegroundColor White
    Write-Host "  TXT Record: asuid -> 7E254F315B8F75E1B35D081436DC1C672F04856CE141D420D8785A4B6961579C" -ForegroundColor White
    Write-Host ""
    exit 1
}

# ============================================================================
# Enable HTTPS
# ============================================================================

Write-Host ""
Write-Host "Enabling HTTPS redirect..." -ForegroundColor Yellow
Write-Host ""

try {
    az webapp update `
        --name $AppName `
        --resource-group $ResourceGroup `
        --https-only true `
        --output none 2>$null
    
    Write-Host "[OK] HTTPS enabled!" -ForegroundColor Green
} catch {
    Write-Host "[WARNING] Could not enable HTTPS redirect" -ForegroundColor Yellow
}

# ============================================================================
# Create Managed SSL Certificate
# ============================================================================

Write-Host ""
Write-Host "Creating free managed SSL certificate..." -ForegroundColor Yellow
Write-Host "This may take 5-10 minutes..." -ForegroundColor Gray
Write-Host ""

try {
    az webapp config ssl create `
        --name $AppName `
        --resource-group $ResourceGroup `
        --hostname $DomainName `
        --output none 2>$null
    
    Write-Host "[OK] SSL certificate created!" -ForegroundColor Green
} catch {
    Write-Host "[WARNING] Could not create managed certificate automatically" -ForegroundColor Yellow
    Write-Host "You may need to create it manually in Azure Portal:" -ForegroundColor Gray
    Write-Host "  1. Go to App Service -> Certificates" -ForegroundColor Gray
    Write-Host "  2. Click 'Add managed certificate'" -ForegroundColor Gray
    Write-Host "  3. Select your domain: $DomainName" -ForegroundColor Gray
}

# ============================================================================
# Summary
# ============================================================================

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "              CONFIGURATION COMPLETE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Your domain is configured:" -ForegroundColor Yellow
Write-Host "  https://$DomainName" -ForegroundColor White
Write-Host ""
Write-Host "  Original URL still works:" -ForegroundColor Yellow
Write-Host "  https://$AppName.azurewebsites.net" -ForegroundColor White
Write-Host ""
Write-Host "  Note: SSL certificate may take a few minutes to provision" -ForegroundColor Gray
Write-Host "        Your site will be accessible after DNS propagates" -ForegroundColor Gray
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
