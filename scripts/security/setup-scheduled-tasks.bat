@echo off
REM Scheduled tasks setup for automated backups

echo Setting up scheduled tasks...

REM Create daily backup task
schtasks /create /tn "D and D Initiative Daily Backup" /tr "%cd%\backup-database.bat" /sc daily /st 03:00 /f

REM Create weekly security monitoring
schtasks /create /tn "D and D Initiative Security Check" /tr "%cd%\monitor-security.bat" /sc weekly /d SUN /st 02:00 /f

if %errorlevel% equ 0 (
    echo Scheduled tasks created successfully!
) else (
    echo Failed to create scheduled tasks. Please run as Administrator.
)

echo Current scheduled tasks:
schtasks /query /tn "D and D Initiative*"

pause
