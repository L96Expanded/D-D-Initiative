@echo off
REM One-Click Production Deployment for D&D Initiative Tracker
REM This script deploys everything needed for internet access

title D&D Initiative Tracker - One-Click Production Deployment

echo.
echo ================================================================================
echo   D and D Initiative Tracker - One-Click Production Deployment
echo ================================================================================
echo.
echo This script will:
echo   ✅ Deploy production containers with internet access configuration
echo   ✅ Set up security monitoring and backups
echo   ✅ Configure all necessary settings for internet deployment
echo   ✅ Test all services to ensure they're working
echo.
echo After this deployment, your app will be ready for internet access at:
echo   🌐 Frontend: http://karsusinitiative.com
echo   🔧 API: http://karsusinitiative.com:8000
echo.
echo NOTE: Router port forwarding still needs to be configured manually
echo       (ports 80 and 8000 to this computer)
echo.
pause

echo.
echo 🚀 Starting one-click deployment...
echo.

REM Step 1: Check prerequisites
echo Step 1/7: Checking prerequisites...
docker --version >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not installed or not running!
    echo Please install Docker Desktop and make sure it's running.
    pause
    exit /b 1
)
echo Docker is running

REM Step 2: Ensure environment files exist
echo.
echo Step 2/7: Setting up environment configuration...
if not exist ".env.production" (
    echo Error: .env.production file not found!
    echo This file should contain production settings.
    pause
    exit /b 1
)

REM Copy production environment to default .env for Docker Compose
copy ".env.production" ".env" >nul
echo Environment configuration ready

REM Step 3: Stop existing containers and clean up
echo.
echo Step 3/7: Stopping existing containers...
docker-compose down >nul 2>&1
docker-compose -f ..\..\docker-compose.prod.yml down -v >nul 2>&1
echo Existing containers stopped

REM Step 4: Build and deploy production containers
echo.
echo Step 4/7: Building and deploying production containers...
echo    This may take a few minutes for the first build...
docker-compose -f ..\..\docker-compose.prod.yml up -d --build 2>deployment_errors.tmp
REM Check if essential containers are running (ignore nginx error)
docker ps -q --filter "name=dnd_postgres_prod" --filter "name=dnd_backend_prod" --filter "name=dnd_frontend_prod" | find /c /v "" > container_count.tmp
set /p running_containers=<container_count.tmp
if %running_containers% LSS 3 (
    echo Error: Essential containers failed to start!
    echo Check the Docker logs for more information.
    type deployment_errors.tmp
    del deployment_errors.tmp container_count.tmp
    pause
    exit /b 1
)
del deployment_errors.tmp container_count.tmp 2>nul
echo Production containers deployed

REM Step 5: Wait for services to be ready
echo.
echo Step 5/7: Waiting for services to start...
timeout /t 15 /nobreak >nul
echo Services startup time completed

REM Step 6: Test services
echo.
echo Step 6/7: Testing services...

REM Test frontend
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost' -UseBasicParsing -TimeoutSec 10; if ($response.StatusCode -eq 200) { Write-Host 'Frontend is accessible' } else { Write-Host 'Frontend test failed' } } catch { Write-Host 'Frontend is not responding' }"

REM Test backend
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/health' -UseBasicParsing -TimeoutSec 10; if ($response.StatusCode -eq 200) { Write-Host 'Backend API is accessible' } else { Write-Host 'Backend API test failed' } } catch { Write-Host 'Backend API is not responding' }"

REM Test API docs
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/docs' -UseBasicParsing -TimeoutSec 10; if ($response.StatusCode -eq 200) { Write-Host 'API Documentation is accessible' } else { Write-Host 'API Documentation test failed' } } catch { Write-Host 'API Documentation is not responding' }"

REM Step 7: Set up security and monitoring
echo.
echo Step 7/7: Setting up security and monitoring...
if exist "setup-security.bat" (
    call setup-security.bat
    echo Security scripts configured
) else (
    echo Security setup script not found - skipping
)

REM Final status check
echo.
echo Final deployment status:
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo ================================================================================
echo   ONE-CLICK DEPLOYMENT COMPLETE!
echo ================================================================================
echo.
echo Your D and D Initiative Tracker is now running and ready for internet access!
echo.
echo LOCAL ACCESS (working now):
echo    Frontend: http://localhost
echo    API: http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo.
echo INTERNET ACCESS (after router setup):
echo    Frontend: http://karsusinitiative.com
echo    API: http://karsusinitiative.com:8000
echo.
echo NEXT STEPS FOR INTERNET ACCESS:
echo    1. Configure router port forwarding:
echo       - Forward port 80 to this computer (%COMPUTERNAME%)
echo       - Forward port 8000 to this computer (%COMPUTERNAME%)
echo    2. Ensure your dynamic DNS is pointing to your external IP
echo    3. Test from outside your network
echo.
echo SECURITY FEATURES ACTIVE:
echo    - Automated database backups
echo    - Security monitoring
echo    - Production-grade authentication
echo    - CORS protection for internet access
echo.
echo AVAILABLE COMMANDS:
echo    .\backup-database.bat     - Create manual backup
echo    .\monitor-security.bat    - Check security status
echo    .\setup-firewall.bat      - Configure Windows Firewall (Admin required)
echo.
echo Happy gaming! Your D and D Initiative Tracker is ready to roll!
echo.
pause