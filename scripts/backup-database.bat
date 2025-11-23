@echo off
REM Database backup script for Windows

set BACKUP_DIR=.\backups
set TIMESTAMP=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set BACKUP_FILE=%BACKUP_DIR%\dnd_tracker_backup_%TIMESTAMP%.sql

echo Creating database backup: %BACKUP_FILE%

if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U dnd_user dnd_tracker > "%BACKUP_FILE%"

if %errorlevel% equ 0 (
    echo Backup completed: %BACKUP_FILE%
) else (
    echo Backup failed!
)

echo.
REM Clean up old backups (keep last 7)
forfiles /P .\backups /M dnd_tracker_backup_*.sql /C "cmd /c if @agedays gtr 7 del @path" 2>nul

echo Old backups cleaned up
pause
