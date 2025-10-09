@echo off
cd /d "%~dp0"
powershell.exe -WindowStyle Normal -ExecutionPolicy Bypass -File "start-dnd-app.ps1"
pause