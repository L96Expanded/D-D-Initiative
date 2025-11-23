@echo off
REM D&D Initiative Tracker - Main Launcher

title D&D Initiative Tracker - Control Panel

:menu
cls
echo.
echo ================================================================================
echo   D and D Initiative Tracker - Control Panel
echo ================================================================================
echo.
echo Select an option:
echo.
echo   1. 🚀 One-Click Deploy (Start/Restart All Services)
echo   2. 📊 Check Status
echo   3. 🛡️  Create Database Backup
echo   4. 🔍 Monitor Security
echo   5. 🖥️  Create Desktop Shortcut
echo   6. ⏹️  Stop All Services
echo   7. 🌐 Open Frontend in Browser
echo   8. 📚 Open API Documentation
echo   9. 📱 Mobile Setup (Cloudflare Tunnel)
echo  10. 🚀 Start Mobile Tunnel
echo  11. ⏹️  Stop Mobile Tunnel
echo  12. ❌ Exit
echo.
set /p choice=Enter your choice (1-12): 

if "%choice%"=="1" goto deploy
if "%choice%"=="2" goto status
if "%choice%"=="3" goto backup
if "%choice%"=="4" goto monitor
if "%choice%"=="5" goto shortcut
if "%choice%"=="6" goto stop
if "%choice%"=="7" goto open_frontend
if "%choice%"=="8" goto open_docs
if "%choice%"=="9" goto mobile_setup
if "%choice%"=="10" goto start_mobile
if "%choice%"=="11" goto stop_mobile
if "%choice%"=="12" goto exit
goto menu

:deploy
echo.
echo 🚀 Starting deployment...
call one-click-deploy.bat
pause
goto menu

:status
echo.
echo 📊 Checking status...
call check-status.bat
goto menu

:backup
echo.
echo 🛡️  Creating backup...
if exist "backup-database.bat" (
    call backup-database.bat
) else (
    echo ❌ Backup script not found. Run deployment first.
    pause
)
goto menu

:monitor
echo.
echo 🔍 Running security monitor...
if exist "monitor-security.bat" (
    call monitor-security.bat
) else (
    echo ❌ Security monitor not found. Run deployment first.
    pause
)
goto menu

:shortcut
echo.
echo 🖥️  Creating desktop shortcut...
call create-desktop-shortcut.bat
goto menu

:stop
echo.
echo ⏹️  Stopping all services...
docker-compose down >nul 2>&1
docker-compose -f docker-compose.prod.yml down >nul 2>&1
echo ✅ All services stopped
pause
goto menu

:open_frontend
echo.
echo 🌐 Opening frontend in browser...
start http://localhost
goto menu

:open_docs
echo.
echo 📚 Opening API documentation...
start http://localhost:8000/docs
goto menu

:mobile_setup
echo.
echo 📱 Setting up mobile deployment...
call setup-mobile-deployment.bat
goto menu

:start_mobile
echo.
echo 🚀 Starting mobile tunnel...
call start-mobile-tunnel.bat
goto menu

:stop_mobile
echo.
echo ⏹️  Stopping mobile tunnel...
call stop-mobile-tunnel.bat
goto menu

:exit
echo.
echo 👋 Thanks for using D&D Initiative Tracker!
exit /b 0