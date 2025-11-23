@echo off
REM ============================================================================
REM  D&D Initiative Tracker - ONE-CLICK MASTER LAUNCHER
REM ============================================================================
REM  This script does EVERYTHING:
REM  - Builds and starts Docker containers
REM  - Starts Cloudflare tunnel for worldwide access  
REM  - Opens the application in browser
REM  - Provides all access URLs and troubleshooting
REM ============================================================================

title D&D Initiative Tracker - Master Launcher

color 0A
echo.
echo ================================================================================
echo                     D&D INITIATIVE TRACKER - MASTER LAUNCHER
echo ================================================================================
echo.
echo   This will start your complete D&D hosting environment:
echo   
echo   [1/5] Pre-flight checks
echo   [2/5] Build and start Docker containers
echo   [3/5] Verify services are running
echo   [4/5] Start Cloudflare tunnel for worldwide access
echo   [5/5] Open application and display access URLs
echo.
echo   After this completes, your D&D tracker will be accessible worldwide!
echo.
pause

REM ============================================================================
echo.
echo [1/5] Running pre-flight checks...
echo ================================================================================

REM Check if Docker is running
docker info >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)
echo  Docker is running

REM Note: Azure deployment handles public access
echo ✓ Ready for Azure deployment

REM ============================================================================
echo.
echo [2/5] Starting Docker containers...
echo ================================================================================

REM Stop any existing containers first
echo Stopping existing containers...
docker-compose -f docker-compose.prod.yml down >nul 2>&1

REM Start production containers
echo Building and starting production containers...
docker-compose -f docker-compose.prod.yml up -d --build

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to start Docker containers!
    echo Please check Docker Desktop is running and try again.
    pause
    exit /b 1
)

echo  Docker containers started successfully!

REM ============================================================================
echo.
echo [3/5] Verifying services are running...
echo ================================================================================

:verify_services
REM Wait for containers to fully start
echo Waiting for containers to initialize (30 seconds)...
timeout /t 30 /nobreak >nul

REM Test local services
echo.
echo Testing local services:
set SERVICES_READY=true

powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost' -UseBasicParsing -TimeoutSec 5; Write-Host '   Frontend ready (localhost)' -ForegroundColor Green } catch { Write-Host '  ❌ Frontend not responding' -ForegroundColor Red; exit 1 }"
if %ERRORLEVEL% NEQ 0 set SERVICES_READY=false

powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/api/health' -UseBasicParsing -TimeoutSec 5; Write-Host '   Backend ready (localhost:8000)' -ForegroundColor Green } catch { Write-Host '  ❌ Backend not responding' -ForegroundColor Red; exit 1 }"
if %ERRORLEVEL% NEQ 0 set SERVICES_READY=false

if "%SERVICES_READY%"=="false" (
    echo.
    echo WARNING: Some services are not ready yet
    echo This might cause issues with the tunnel
    echo.
    echo Would you like to:
    echo   [1] Continue anyway
    echo   [2] Wait 30 more seconds
    echo   [3] Exit and check Docker logs
    set /p choice="> "
    
    if "%choice%"=="2" (
        echo Waiting 30 more seconds...
        timeout /t 30 /nobreak >nul
        goto verify_services
    )
    if "%choice%"=="3" (
        echo.
        echo Run this command to check logs:
        echo   docker-compose -f docker-compose.prod.yml logs
        pause
        exit /b 1
    )
)

echo.
echo  All services are ready!

REM ============================================================================
echo.
echo [4/5] Local development ready...
echo ================================================================================
echo.
echo   For worldwide access, deploy to Azure using:
echo   cd azure-infrastructure
echo   .\deploy.ps1
echo.

REM ============================================================================
echo.
echo [5/5] Opening application and displaying URLs...
echo ================================================================================
echo.

REM Test remote access if tunnel is available
if "%TUNNEL_AVAILABLE%"=="true" (
    echo Testing remote access...
    powershell -Command "try { $response = Invoke-WebRequest -Uri 'https://karsusinitiative.com' -UseBasicParsing -TimeoutSec 10; Write-Host '   Remote access working!' -ForegroundColor Green; exit 0 } catch { Write-Host '  ⚠ Remote access not working yet' -ForegroundColor Yellow; Write-Host '  Check Cloudflare dashboard for tunnel configuration' -ForegroundColor Yellow; exit 1 }"
    set REMOTE_WORKING=%ERRORLEVEL%
    echo.
)

REM Open the appropriate URL
if "%TUNNEL_AVAILABLE%"=="true" (
    if %REMOTE_WORKING% EQU 0 (
        echo Opening https://karsusinitiative.com in your browser...
        start https://karsusinitiative.com
    ) else (
        echo Opening http://localhost in your browser...
        echo (Remote access needs configuration - see troubleshooting below^)
        start http://localhost
    )
) else (
    echo Opening http://localhost in your browser...
    start http://localhost
)

REM ============================================================================
echo.
echo ================================================================================
echo                            SETUP COMPLETE!
echo ================================================================================
echo.
echo     YOUR D&D INITIATIVE TRACKER IS NOW RUNNING! 
echo.
echo ================================================================================ 
echo   LOCAL ACCESS (always works):
echo   • Frontend: http://localhost
echo   • Backend: http://localhost:8000
echo   • API Docs: http://localhost:8000/docs
echo   • Health Check: http://localhost:8000/api/health
echo.

if "%TUNNEL_AVAILABLE%"=="true" (
    if %REMOTE_WORKING% EQU 0 (
        echo   WORLDWIDE ACCESS ( working - share with players^):
        echo   •  Main App: https://karsusinitiative.com
        echo   •  API: https://api.karsusinitiative.com  
        echo   •  API Documentation: https://api.karsusinitiative.com/docs
        echo.
        echo   PLAYER INSTRUCTIONS:
        echo   Tell your players to visit: https://karsusinitiative.com
        echo   They can access your D&D tracker from anywhere in the world!
    ) else (
        echo   WORLDWIDE ACCESS (⚠ needs configuration^):
        echo   • URL: https://karsusinitiative.com
        echo   • Status: Tunnel running but hostname not configured
        echo.
        echo   TROUBLESHOOTING:
        echo   1. Go to: https://one.dash.cloudflare.com/
        echo   2. Navigate: Zero Trust  Networks  Tunnels
        echo   3. Find tunnel: 80cf609e-e89a-47c4-a759-315191f4e841
        echo   4. If it says "locally configured", click MIGRATE
        echo   5. After migration, click Configure  Public Hostname
        echo   6. Add hostname:
        echo      - Domain: karsusinitiative.com
        echo      - Service Type: HTTP
        echo      - URL: 127.0.0.1:80
        echo   7. Save and wait 1 minute
        echo.
        echo   See docs\CLOUDFLARE_SETUP.md for detailed instructions
    )
)

echo.
echo   MANAGEMENT:
echo   • Tunnel runs in minimized window (if available^)
echo   • Close tunnel window to stop worldwide access
echo   • Docker containers will keep running locally
echo   • Use STOP_EVERYTHING.bat to stop all services
echo ================================================================================
echo.
echo   🐉 Ready for adventure! Press any key when done gaming... ⚔️
echo.
pause

REM ============================================================================
echo.
echo   Would you like to stop the Docker containers too? (Y/N)
set /p stopContainers="> "

if /i "%stopContainers%"=="Y" (
    echo Stopping Docker containers...
    docker-compose -f docker-compose.prod.yml down
    echo  All services stopped
) else (
    echo  Tunnel stopped, Docker containers still running locally
    echo   Access locally at: http://localhost
)

echo.
echo Thank you for using D&D Initiative Tracker! 
pause