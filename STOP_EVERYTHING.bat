@echo off
REM ============================================================================
REM  D&D Initiative Tracker - STOP EVERYTHING
REM ============================================================================
REM  Stops all services: tunnel, Docker containers, everything
REM ============================================================================

title D&D Initiative Tracker - Stop Everything

color 0C
echo.
echo ================================================================================
echo                     D&D INITIATIVE TRACKER - STOP EVERYTHING  
echo ================================================================================
echo.
echo   This will stop all D&D Initiative Tracker services:
echo   • Cloudflare tunnel (worldwide access)
echo   • Docker containers (local services)
echo   • All background processes
echo.
set /p confirm="Continue? (Y/N): "

if /i not "%confirm%"=="Y" (
    echo Cancelled.
    pause
    exit /b 0
)

echo.
echo Stopping Cloudflare tunnel...
taskkill /f /im cloudflared.exe >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✓ Tunnel stopped
) else (
    echo ℹ No tunnel was running
)

echo.
echo Stopping Docker containers...
docker-compose -f docker-compose.prod.yml down
if %ERRORLEVEL% EQU 0 (
    echo ✓ Docker containers stopped
) else (
    echo ⚠ Error stopping containers
)

echo.
echo ================================================================================
echo   🛑 ALL SERVICES STOPPED
echo ================================================================================
echo.
echo   Your D&D Initiative Tracker is now offline.
echo   
echo   To start everything again, run: START_EVERYTHING.bat
echo   
echo   🎲 Thanks for using D&D Initiative Tracker!
echo.
pause