@echo off
REM Start Mobile D&D Initiative Tracker with Cloudflare Tunnel

title D&D Initiative Tracker - Mobile Tunnel Startup

echo.
echo ================================================================================
echo   Starting Mobile D&D Initiative Tracker
echo ================================================================================
echo.

REM Check if containers are running
echo Checking application status...
docker ps -q --filter "name=dnd_" | find /c /v "" > container_count.tmp
set /p running_containers=<container_count.tmp
del container_count.tmp

if %running_containers% LSS 3 (
    echo Starting application containers...
    docker-compose -f ..\..\docker-compose.prod.yml up -d
    echo Waiting for services to start...
    timeout /t 15 /nobreak >nul
) else (
    echo Application containers are already running
)

REM Test local services
echo.
echo Testing local services...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost' -UseBasicParsing -TimeoutSec 5; if ($response.StatusCode -eq 200) { Write-Host 'Frontend: Ready' } else { Write-Host 'Frontend: Not ready' } } catch { Write-Host 'Frontend: Failed to start' }"
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/health' -UseBasicParsing -TimeoutSec 5; if ($response.StatusCode -eq 200) { Write-Host 'Backend: Ready' } else { Write-Host 'Backend: Not ready' } } catch { Write-Host 'Backend: Failed to start' }"

echo.
echo ================================================================================
echo   Starting Cloudflare Tunnel...
echo ================================================================================
echo.
echo Your D&D Initiative Tracker will be accessible at:
echo   Frontend: https://karsusinitiative.com
echo   API: https://api.karsusinitiative.com
echo.
echo Press Ctrl+C to stop the tunnel and close application
echo.

REM Start the tunnel (this will run until stopped)
..\..\cloudflare-tools\cloudflared.bat tunnel run dnd-initiative