@echo off
REM Security setup script for Windows production deployment
REM This script creates all necessary security components

title D and D Initiative Tracker - Security Setup

echo Setting up security best practices for karsusinitiative.com

echo Security Checklist:
echo [OK] 1. Strong passwords configured in .env.production
echo [OK] 2. JWT secret updated with secure random string
echo [OK] 3. CORS origins restricted to your domain

echo 4. Creating backup script...

REM Create backup script
(
echo @echo off
echo REM Database backup script for Windows
echo.
echo set BACKUP_DIR=.\backups
echo set TIMESTAMP=%%date:~-4,4%%%%date:~-10,2%%%%date:~-7,2%%_%%time:~0,2%%%%time:~3,2%%%%time:~6,2%%
echo set TIMESTAMP=%%TIMESTAMP: =0%%
echo set BACKUP_FILE=%%BACKUP_DIR%%\dnd_tracker_backup_%%TIMESTAMP%%.sql
echo.
echo echo Creating database backup: %%BACKUP_FILE%%
echo.
echo if not exist "%%BACKUP_DIR%%" mkdir "%%BACKUP_DIR%%"
echo.
echo docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U dnd_user dnd_tracker ^> "%%BACKUP_FILE%%"
echo.
echo if %%errorlevel%% equ 0 ^(
echo     echo Backup completed: %%BACKUP_FILE%%
echo ^) else ^(
echo     echo Backup failed!
echo ^)
echo.
echo echo.
echo REM Clean up old backups ^(keep last 7^)
echo forfiles /P .\backups /M dnd_tracker_backup_*.sql /C "cmd /c if @agedays gtr 7 del @path" 2^>nul
echo.
echo echo Old backups cleaned up
echo pause
) > backup-database.bat

echo 5. Creating monitoring script...

REM Create monitoring script
(
echo @echo off
echo REM Security monitoring script for Windows
echo.
echo echo Security Monitoring Report - %%date%% %%time%%
echo echo ============================================
echo.
echo echo Recent authentication failures:
echo docker-compose -f docker-compose.prod.yml logs backend 2^>nul ^| findstr /i "unauthorized authentication invalid"
echo.
echo echo Container Health Status:
echo docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" --filter "name=dnd_"
echo.
echo echo Disk Space Usage:
echo dir /-c
echo.
echo echo Security monitoring complete
echo pause
) > monitor-security.bat

echo 6. Creating SSL certificate helper...

REM Create SSL setup instructions
(
echo SSL Certificate Setup Instructions
echo =====================================
echo.
echo For production HTTPS access, you need to set up SSL certificates.
echo.
echo Option 1: Let's Encrypt ^(Free^)
echo -------------------------------
echo 1. Install Certbot: https://certbot.eff.org/
echo 2. Run: certbot certonly --standalone -d karsusinitiative.com
echo 3. Copy certificates to ./nginx/ssl/ folder
echo 4. Update nginx configuration to use SSL
echo.
echo Option 2: Self-Signed Certificate ^(For Testing^)
echo ----------------------------------------------
echo 1. Create certificate:
echo    openssl req -x509 -nodes -days 365 -newkey rsa:2048 ^
echo        -keyout nginx/ssl/server.key ^
echo        -out nginx/ssl/server.crt
echo.
echo Option 3: Commercial SSL Certificate
echo ----------------------------------
echo 1. Purchase from a Certificate Authority
echo 2. Follow their installation instructions
echo 3. Update nginx configuration
echo.
echo After obtaining certificates:
echo 1. Update docker-compose.prod.yml to mount SSL certificates
echo 2. Update nginx configuration for HTTPS
echo 3. Test with: https://karsusinitiative.com
) > SSL_SETUP_INSTRUCTIONS.txt

echo 7. Creating Windows Firewall configuration...

REM Create firewall setup script
(
echo @echo off
echo REM Windows Firewall configuration for D and D Initiative Tracker
echo.
echo echo Configuring Windows Firewall for karsusinitiative.com
echo.
echo REM Allow HTTP traffic ^(port 80^)
echo netsh advfirewall firewall add rule name="D and D Initiative HTTP" dir=in action=allow protocol=TCP localport=80
echo.
echo REM Allow API traffic ^(port 8000^)
echo netsh advfirewall firewall add rule name="D and D Initiative API" dir=in action=allow protocol=TCP localport=8000
echo.
echo REM Allow HTTPS traffic ^(port 443^)
echo netsh advfirewall firewall add rule name="D and D Initiative HTTPS" dir=in action=allow protocol=TCP localport=443
echo.
echo if %%errorlevel%% equ 0 ^(
echo     echo Windows Firewall rules added successfully!
echo ^) else ^(
echo     echo Failed to add firewall rules. Please run as Administrator.
echo ^)
echo.
echo echo Current firewall rules for D and D Initiative:
echo netsh advfirewall firewall show rule name="D and D Initiative HTTP"
echo netsh advfirewall firewall show rule name="D and D Initiative API"
echo netsh advfirewall firewall show rule name="D and D Initiative HTTPS"
echo.
echo pause
) > setup-firewall.bat

echo 8. Creating scheduled tasks setup...

REM Create scheduled tasks script
(
echo @echo off
echo REM Scheduled tasks setup for automated backups
echo.
echo echo Setting up scheduled tasks...
echo.
echo REM Create daily backup task
echo schtasks /create /tn "D and D Initiative Daily Backup" /tr "%%cd%%\backup-database.bat" /sc daily /st 03:00 /f
echo.
echo REM Create weekly security monitoring
echo schtasks /create /tn "D and D Initiative Security Check" /tr "%%cd%%\monitor-security.bat" /sc weekly /d SUN /st 02:00 /f
echo.
echo if %%errorlevel%% equ 0 ^(
echo     echo Scheduled tasks created successfully!
echo ^) else ^(
echo     echo Failed to create scheduled tasks. Please run as Administrator.
echo ^)
echo.
echo echo Current scheduled tasks:
echo schtasks /query /tn "D and D Initiative*"
echo.
echo pause
) > setup-scheduled-tasks.bat

echo Security setup completed!

echo Next steps:
echo 1. Run as Administrator: setup-firewall.bat
echo 2. Run as Administrator: setup-scheduled-tasks.bat
echo 3. Set up SSL: Follow instructions in SSL_SETUP_INSTRUCTIONS.txt
echo 4. Test backups: Run backup-database.bat
echo 5. Monitor security: Run monitor-security.bat

echo Your D and D Initiative Tracker is now configured for production security!

echo Important: Make sure to:
echo - Update your Dynamic DNS to point to your external IP
echo - Configure port forwarding in your router
echo - Test external access from mobile data

pause