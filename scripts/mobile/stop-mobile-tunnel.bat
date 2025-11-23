@echo off
REM Stop Mobile D&D Initiative Tracker

title Stopping Mobile D&D Initiative Tracker

echo.
echo Stopping Cloudflare Tunnel and application...
echo.

REM Stop tunnel (if running)
taskkill /f /im cloudflared.exe 2>nul

REM Stop containers
docker-compose -f docker-compose.prod.yml down

echo.
echo Mobile D&D Initiative Tracker stopped successfully
echo.
pause