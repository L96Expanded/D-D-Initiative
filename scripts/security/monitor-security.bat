@echo off
REM Security monitoring script for Windows

echo Security Monitoring Report - %date% %time%
echo ============================================

echo Recent authentication failures:
docker-compose -f docker-compose.prod.yml logs backend 2>nul | findstr /i "unauthorized authentication invalid"

echo Container Health Status:
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" --filter "name=dnd_"

echo Disk Space Usage:
dir /-c

echo Security monitoring complete
pause
