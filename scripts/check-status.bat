@echo off
REM Quick Status Check for D&D Initiative Tracker

title D&D Initiative Tracker - Status Check

echo.
echo ================================================================================
echo   D and D Initiative Tracker - Status Check
echo ================================================================================
echo.

REM Check if Docker is running
echo 🔍 Checking Docker status...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running or not installed
    echo.
    pause
    exit /b 1
) else (
    echo ✅ Docker is running
)

echo.
echo 📊 Container Status:
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" --filter "name=dnd_"

echo.
echo 🌐 Service Accessibility Tests:

REM Test frontend
echo Testing frontend...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost' -UseBasicParsing -TimeoutSec 5; if ($response.StatusCode -eq 200) { Write-Host '✅ Frontend: http://localhost' } else { Write-Host '❌ Frontend: Not accessible' } } catch { Write-Host '❌ Frontend: Not responding' }"

REM Test backend health
echo Testing backend API...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/health' -UseBasicParsing -TimeoutSec 5; if ($response.StatusCode -eq 200) { Write-Host '✅ Backend API: http://localhost:8000' } else { Write-Host '❌ Backend API: Not accessible' } } catch { Write-Host '❌ Backend API: Not responding' }"

REM Test API docs
echo Testing API documentation...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/docs' -UseBasicParsing -TimeoutSec 5; if ($response.StatusCode -eq 200) { Write-Host '✅ API Docs: http://localhost:8000/docs' } else { Write-Host '❌ API Docs: Not accessible' } } catch { Write-Host '❌ API Docs: Not responding' }"

echo.
echo 🛡️  Security Status:
if exist "backups" (
    echo ✅ Backup system configured
    for /f %%i in ('dir /b backups\*.sql 2^>nul ^| find /c /v ""') do echo    📁 Backup files: %%i
) else (
    echo ⚠️  Backup system not configured
)

if exist "monitor-security.bat" (
    echo ✅ Security monitoring available
) else (
    echo ⚠️  Security monitoring not configured
)

echo.
echo 📍 Access Information:
echo    🏠 Local Access:
echo       Frontend: http://localhost
echo       API: http://localhost:8000
echo       API Docs: http://localhost:8000/docs
echo.
echo    🌍 Internet Access (after router setup):
echo       Frontend: http://karsusinitiative.com
echo       API: http://karsusinitiative.com:8000
echo.

REM Check if any containers are not running
set "containers_down=0"
for /f %%i in ('docker ps -q --filter "name=dnd_" ^| find /c /v ""') do set "running_containers=%%i"
if %running_containers% LSS 3 (
    echo ⚠️  WARNING: Not all containers are running
    echo    Expected: 3 containers (frontend, backend, database)
    echo    Running: %running_containers% containers
    echo.
    echo    Run .\one-click-deploy.bat to start all services
) else (
    echo ✅ All services are running properly
)

echo.
echo 🔧 Available Commands:
echo    .\one-click-deploy.bat    - Deploy/restart all services
echo    .\backup-database.bat     - Create database backup
echo    .\monitor-security.bat    - Security monitoring
echo    .\check-status.bat        - Run this status check again
echo.
pause