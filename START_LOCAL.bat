@echo off
REM ============================================================================
REM  D&D Initiative Tracker - LOCAL DEVELOPMENT LAUNCHER
REM ============================================================================
REM  Starts Docker containers for local development
REM  For worldwide access, deploy to Azure
REM ============================================================================

title D&D Initiative Tracker - Local Development

color 0A
echo.
echo ================================================================================
echo                     D&D INITIATIVE TRACKER - LOCAL MODE
echo ================================================================================
echo.
echo   Starting local development environment...
echo.
pause

REM ============================================================================
echo.
echo [1/3] Starting Docker containers...
echo ================================================================================

docker-compose -f docker-compose.prod.yml down >nul 2>&1
docker-compose -f docker-compose.prod.yml up -d --build

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to start Docker containers!
    pause
    exit /b 1
)

echo ✓ Docker containers started!

REM ============================================================================
echo.
echo [2/3] Waiting for services...
echo ================================================================================

timeout /t 30 /nobreak >nul

powershell -Command "try { Invoke-WebRequest -Uri 'http://localhost' -UseBasicParsing -TimeoutSec 5 | Out-Null; Write-Host '  ✓ Frontend ready' -ForegroundColor Green } catch { Write-Host '  ⚠ Frontend starting...' -ForegroundColor Yellow }"

powershell -Command "try { Invoke-WebRequest -Uri 'http://localhost:8000/api/health' -UseBasicParsing -TimeoutSec 5 | Out-Null; Write-Host '  ✓ Backend ready' -ForegroundColor Green } catch { Write-Host '  ⚠ Backend starting...' -ForegroundColor Yellow }"

REM ============================================================================
echo.
echo [3/3] Opening application...
echo ================================================================================

start http://localhost

echo.
echo ================================================================================
echo                            READY FOR DEVELOPMENT!
echo ================================================================================
echo.
echo   LOCAL ACCESS:
echo   • Frontend: http://localhost
echo   • Backend: http://localhost:8000
echo   • API Docs: http://localhost:8000/docs
echo   • Health: http://localhost:8000/api/health
echo.
echo   TO DEPLOY TO AZURE:
echo   1. cd azure-infrastructure
echo   2. .\deploy.ps1
echo   3. Push to GitHub for automatic deployment
echo.
echo   MANAGEMENT:
echo   • Use STOP_EVERYTHING.bat to stop containers
echo   • Push to 'main' branch triggers Azure CI/CD
echo ================================================================================
echo.
echo   🚀 Ready for development! Press any key to stop... 
echo.
pause

docker-compose -f docker-compose.prod.yml down
echo ✓ Containers stopped
pause
