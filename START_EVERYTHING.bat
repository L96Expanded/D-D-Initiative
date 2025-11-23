@echo off
REM ============================================================================
REM  D&D Initiative Tracker - ONE-CLICK MASTER LAUNCHER
REM ============================================================================
REM  This script does EVERYTHING:
REM  - Builds and starts Docker containers
REM  - Starts Cloudflare tunnel for worldwide access  
REM  - Opens the application in browser
REM  - Provides all access URLs
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
echo   [1/4] Build and start Docker containers
echo   [2/4] Start Cloudflare tunnel for worldwide access
echo   [3/4] Open application in browser
echo   [4/4] Display all access URLs
echo.
echo   After this completes, your D&D tracker will be accessible worldwide!
echo.
pause

REM ============================================================================
echo.
echo [1/4] Starting Docker containers...
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

echo ✓ Docker containers started successfully!

REM ============================================================================
echo.
echo [2/4] Starting Cloudflare tunnel...
echo ================================================================================

REM Wait a moment for containers to fully start
echo Waiting for containers to initialize...
timeout /t 10 /nobreak >nul

REM Test local services before starting tunnel
echo Testing local services...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost' -UseBasicParsing -TimeoutSec 5; Write-Host '✓ Frontend ready' } catch { Write-Host '⚠ Frontend starting...' }"
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/health' -UseBasicParsing -TimeoutSec 5; Write-Host '✓ Backend ready' } catch { Write-Host '⚠ Backend starting...' }"

echo Starting Cloudflare tunnel for worldwide access...
echo.
echo ================================================================================
echo   TUNNEL STARTING - Your D&D tracker will be accessible at:
echo   
echo    Frontend: https://karsusinitiative.com
echo    API: https://api.karsusinitiative.com
echo    API Docs: https://api.karsusinitiative.com/docs
echo.
echo   Press Ctrl+C to stop the tunnel when you're done gaming!
echo ================================================================================
echo.

REM Start tunnel (this will run in foreground)
start "Cloudflare Tunnel" /min cloudflare-tools\cloudflared.exe tunnel --config cloudflare-tools\tunnel-config.yml run

REM Wait a moment for tunnel to establish
timeout /t 5 /nobreak >nul

REM ============================================================================
echo.
echo [3/4] Opening application in browser...
echo ================================================================================

REM Open the application in default browser
echo Opening https://karsusinitiative.com in your browser...
start https://karsusinitiative.com

REM ============================================================================
echo.
echo [4/4] Setup complete!
echo ================================================================================
echo.
echo     YOUR D&D INITIATIVE TRACKER IS NOW LIVE! 
echo.
echo ================================================================================ 
echo   LOCAL ACCESS (for testing):
echo   • Frontend: http://localhost
echo   • Backend: http://localhost:8000
echo   • API Docs: http://localhost:8000/docs
echo.
echo   WORLDWIDE ACCESS (share with players):
echo   •  Main App: https://karsusinitiative.com
echo   •  API: https://api.karsusinitiative.com  
echo   •  API Documentation: https://api.karsusinitiative.com/docs
echo.
echo   PLAYER INSTRUCTIONS:
echo   Tell your players to visit: https://karsusinitiative.com
echo   They can access your D&D tracker from anywhere in the world!
echo.
echo   MANAGEMENT:
echo   • Tunnel runs in minimized window
echo   • Close tunnel window to stop worldwide access
echo   • Docker containers will keep running locally
echo   • Use 'docker-compose -f docker-compose.prod.yml down' to stop everything
echo ================================================================================
echo.
echo   🐉 Ready for adventure! Press any key when done gaming... ⚔️
echo.
pause

REM ============================================================================
echo.
echo Shutting down tunnel...
taskkill /f /im cloudflared.exe >nul 2>&1

echo.
echo   Would you like to stop the Docker containers too? (Y/N)
set /p stopContainers="> "

if /i "%stopContainers%"=="Y" (
    echo Stopping Docker containers...
    docker-compose -f docker-compose.prod.yml down
    echo ✓ All services stopped
) else (
    echo ✓ Tunnel stopped, Docker containers still running locally
    echo   Access locally at: http://localhost
)

echo.
echo Thank you for using D&D Initiative Tracker! 🎲
pause