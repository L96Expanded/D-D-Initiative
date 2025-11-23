@echo off
REM Cloudflare Tunnel Setup for Mobile D&D Initiative Tracker

title D&D Initiative Tracker - Mobile Deployment with Cloudflare Tunnel

echo.
echo ================================================================================
echo   D&D Initiative Tracker - Mobile Deployment Setup
echo ================================================================================
echo.
echo This script sets up Cloudflare Tunnel for mobile hosting without router config
echo Your app will be accessible from anywhere using karsusinitiative.com
echo.

REM Step 1: Check if cloudflared is installed
echo Step 1/5: Checking Cloudflare Tunnel (cloudflared)...
.\cloudflared.bat --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo Cloudflared not found. Downloading now...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile 'cloudflare-tools\cloudflared.exe'"
    echo Cloudflared downloaded successfully
) else (
    echo Cloudflared is ready
)

REM Step 2: Deploy local containers
echo.
echo Step 2/5: Deploying local containers...
docker-compose -f docker-compose.prod.yml up -d --build
if errorlevel 1 (
    echo Error: Failed to start containers
    pause
    exit /b 1
)
echo Containers deployed successfully

REM Step 3: Wait for services
echo.
echo Step 3/5: Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Step 4: Test local services
echo.
echo Step 4/5: Testing local services...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost' -UseBasicParsing -TimeoutSec 5; if ($response.StatusCode -eq 200) { Write-Host 'Frontend: OK' } } catch { Write-Host 'Frontend: Failed' }"
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/health' -UseBasicParsing -TimeoutSec 5; if ($response.StatusCode -eq 200) { Write-Host 'Backend: OK' } } catch { Write-Host 'Backend: Failed' }"

REM Step 5: Create tunnel configuration
echo.
echo Step 5/5: Setting up Cloudflare Tunnel...

REM Create tunnel config directory
if not exist "%USERPROFILE%\.cloudflared" mkdir "%USERPROFILE%\.cloudflared"

REM Create tunnel configuration
(
echo tunnel: dnd-initiative
echo credentials-file: %USERPROFILE%\.cloudflared\dnd-initiative.json
echo.
echo ingress:
echo   - hostname: karsusinitiative.com
echo     service: http://localhost:80
echo   - hostname: api.karsusinitiative.com  
echo     service: http://localhost:8000
echo   - service: http_status:404
) > "%USERPROFILE%\.cloudflared\config.yml"

echo.
echo ================================================================================
echo   MOBILE DEPLOYMENT READY!
echo ================================================================================
echo.
echo Your D&D Initiative Tracker is now running locally and ready for tunnel setup.
echo.
echo NEXT STEPS TO COMPLETE MOBILE SETUP:
echo.
echo 1. AUTHENTICATE WITH CLOUDFLARE:
echo    .\cloudflared.bat tunnel login
echo    (This will open a browser to authenticate)
echo.
echo 2. CREATE TUNNEL:
echo    .\cloudflared.bat tunnel create dnd-initiative
echo.
echo 3. CONFIGURE DNS IN CLOUDFLARE:
echo    - Go to Cloudflare DNS settings for karsusinitiative.com
echo    - Add CNAME record: @ -> [tunnel-id].cfargotunnel.com
echo    - Add CNAME record: api -> [tunnel-id].cfargotunnel.com
echo.
echo 4. START TUNNEL:
echo    .\start-mobile-tunnel.bat
echo.
echo 5. TEST ACCESS:
echo    https://karsusinitiative.com
echo    https://api.karsusinitiative.com
echo.
echo BENEFITS OF THIS SETUP:
echo - Works from any internet connection (WiFi, hotspot, etc.)
echo - No router configuration needed
echo - Automatic HTTPS with Cloudflare SSL
echo - DDoS protection included
echo - Works while moving between locations
echo.
echo MOBILE USAGE:
echo - Connect to any WiFi or use mobile hotspot
echo - Run: start-mobile-tunnel.bat
echo - Your app is instantly accessible worldwide
echo.
pause