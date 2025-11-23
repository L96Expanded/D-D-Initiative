@echo off
REM Production Deployment Script for D&D Initiative Tracker (Windows)

echo 🚀 Starting production deployment...

REM Check if .env.production exists
if not exist ".env.production" (
    echo ❌ Error: .env.production file not found!
    echo Please copy .env.production to a new file and configure it.
    pause
    exit /b 1
)

REM Check if domain is configured
findstr "your-domain.com" .env.production >nul
if %errorlevel% equ 0 (
    echo ⚠️  Warning: Please update DOMAIN_NAME in .env.production
    set /p choice="Continue anyway? (y/N): "
    if /i not "%choice%"=="y" exit /b 1
)

REM Stop existing containers
echo 🛑 Stopping existing containers...
docker-compose -f docker-compose.prod.yml --env-file .env.production down

REM Build and start production containers
echo 🔨 Building and starting production containers...
docker-compose -f docker-compose.prod.yml --env-file .env.production up --build -d

REM Check if containers are running
echo 📋 Checking container status...
docker-compose -f docker-compose.prod.yml --env-file .env.production ps

echo ✅ Deployment complete!
echo 🌐 Your D&D Initiative Tracker should be available at:

for /f "tokens=2 delims==" %%i in ('findstr "DOMAIN_NAME" .env.production') do (
    echo    Frontend: http://%%i
    echo    API: http://%%i:8000
)

echo.
echo 📝 Next steps for internet access:
echo 1. Configure your router to forward ports 80 and 8000 to this machine
echo 2. Set up a domain name or use dynamic DNS
echo 3. Configure SSL certificates for HTTPS (recommended)
echo 4. Update firewall rules if necessary
pause