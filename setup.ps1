# D&D Initiative Tracker - Automated Setup Script for Windows
# This script automates the entire setup process

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🎲 D&D Initiative Tracker - Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if a command exists
function Test-CommandExists {
    param($command)
    $null = Get-Command $command -ErrorAction SilentlyContinue
    return $?
}

# Function to generate secure random string
function New-SecureSecret {
    param([int]$Length = 64)
    $bytes = New-Object byte[] $Length
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    $rng.GetBytes($bytes)
    return [Convert]::ToBase64String($bytes)
}

# Step 1: Check prerequisites
Write-Host "Step 1: Checking prerequisites..." -ForegroundColor Yellow

# Check Docker
if (Test-CommandExists docker) {
    Write-Host "✅ Docker is installed" -ForegroundColor Green
    
    # Check if Docker is running
    try {
        docker ps | Out-Null
        Write-Host "✅ Docker is running" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Docker is installed but not running" -ForegroundColor Yellow
        Write-Host "   Starting Docker Desktop..." -ForegroundColor Yellow
        Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe" -ErrorAction SilentlyContinue
        Write-Host "   Please wait for Docker to start (this may take a minute)..." -ForegroundColor Yellow
        Start-Sleep -Seconds 30
    }
} else {
    Write-Host "❌ Docker is not installed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop/" -ForegroundColor Red
    Write-Host "After installation, run this script again." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Step 2: Setup environment file
Write-Host "Step 2: Setting up environment configuration..." -ForegroundColor Yellow

if (Test-Path ".env") {
    Write-Host "⚠️  .env file already exists" -ForegroundColor Yellow
    $overwrite = Read-Host "Do you want to overwrite it? (y/N)"
    if ($overwrite -ne "y") {
        Write-Host "Keeping existing .env file" -ForegroundColor Green
    } else {
        $setupEnv = $true
    }
} else {
    $setupEnv = $true
}

if ($setupEnv) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    
    # Copy template
    Copy-Item ".env.example" ".env"
    
    # Generate secure secrets
    Write-Host "Generating secure passwords and secrets..." -ForegroundColor Yellow
    $dbPassword = New-SecureSecret -Length 32
    $jwtSecret = New-SecureSecret -Length 64
    
    # Read and replace values
    $envContent = Get-Content ".env" -Raw
    $envContent = $envContent -replace "changeme_to_secure_password", $dbPassword
    $envContent = $envContent -replace "changeme_to_long_random_secret_key", $jwtSecret
    $envContent | Set-Content ".env"
    
    Write-Host "✅ Created .env file with secure credentials" -ForegroundColor Green
    Write-Host "   Database password: $($dbPassword.Substring(0, 10))..." -ForegroundColor Gray
    Write-Host "   JWT secret: $($jwtSecret.Substring(0, 10))..." -ForegroundColor Gray
}

Write-Host ""

# Step 3: Ask about production deployment
Write-Host "Step 3: Deployment configuration..." -ForegroundColor Yellow
$deployType = Read-Host "Are you setting up for (L)ocal development or (P)roduction? [L/P]"

if ($deployType -eq "P" -or $deployType -eq "p") {
    Write-Host ""
    Write-Host "Production Setup" -ForegroundColor Cyan
    Write-Host "================" -ForegroundColor Cyan
    $domain = Read-Host "Enter your domain name (e.g., mydomain.com)"
    
    if ($domain) {
        # Update .env file with production settings
        $envContent = Get-Content ".env" -Raw
        $envContent = $envContent -replace "ENVIRONMENT=development", "ENVIRONMENT=production"
        $envContent = $envContent -replace "SECURE_COOKIES=false", "SECURE_COOKIES=true"
        $envContent = $envContent -replace "DOMAIN_NAME=", "DOMAIN_NAME=$domain"
        $envContent = $envContent -replace 'CORS_ORIGINS=\["http://localhost:3000","http://127\.0\.0\.1:3000"\]', "CORS_ORIGINS=[`"http://localhost:3000`",`"https://$domain`",`"http://$domain`"]"
        $envContent = $envContent -replace 'ALLOWED_HOSTS=\["localhost","127\.0\.0\.1"\]', "ALLOWED_HOSTS=[`"localhost`",`"127.0.0.1`",`"$domain`"]"
        $envContent = $envContent -replace 'VITE_API_URL=http://localhost:8000', "VITE_API_URL=https://$domain/api"
        $envContent | Set-Content ".env"
        
        Write-Host "✅ Configured for production deployment at $domain" -ForegroundColor Green
    }
}

Write-Host ""

# Step 4: Build and start containers
Write-Host "Step 4: Building and starting Docker containers..." -ForegroundColor Yellow
Write-Host "   This may take 5-10 minutes on first run..." -ForegroundColor Gray
Write-Host ""

docker-compose up --build -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Docker containers started successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to start Docker containers" -ForegroundColor Red
    Write-Host "   Check the error messages above" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Step 5: Wait for services to be healthy
Write-Host "Step 5: Waiting for services to be ready..." -ForegroundColor Yellow

$maxAttempts = 30
$attempt = 0
$allHealthy = $false

while (-not $allHealthy -and $attempt -lt $maxAttempts) {
    $attempt++
    Write-Host "   Checking... (attempt $attempt/$maxAttempts)" -ForegroundColor Gray
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $allHealthy = $true
        }
    } catch {
        Start-Sleep -Seconds 2
    }
}

if ($allHealthy) {
    Write-Host "✅ All services are healthy and ready" -ForegroundColor Green
} else {
    Write-Host "⚠️  Services are starting but may need more time" -ForegroundColor Yellow
    Write-Host "   You can check status with: docker-compose ps" -ForegroundColor Yellow
}

Write-Host ""

# Step 6: Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✨ Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your D&D Initiative Tracker is now running!" -ForegroundColor Green
Write-Host ""
Write-Host "Access the application at:" -ForegroundColor Cyan
Write-Host "  Frontend:    http://localhost:3000" -ForegroundColor White
Write-Host "  Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs:    http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Cyan
Write-Host "  View logs:        docker-compose logs -f" -ForegroundColor White
Write-Host "  Stop services:    docker-compose down" -ForegroundColor White
Write-Host "  Restart services: docker-compose restart" -ForegroundColor White
Write-Host "  Check status:     docker-compose ps" -ForegroundColor White
Write-Host ""

# Ask to open browser
$openBrowser = Read-Host "Open the application in your browser now? (Y/n)"
if ($openBrowser -ne "n") {
    Start-Process "http://localhost:3000"
}

Write-Host ""
Write-Host "Happy adventuring! 🗡️✨" -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter to exit"
