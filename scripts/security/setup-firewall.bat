@echo off
REM Windows Firewall configuration for D and D Initiative Tracker

echo Configuring Windows Firewall for karsusinitiative.com

REM Allow HTTP traffic (port 80)
netsh advfirewall firewall add rule name="D and D Initiative HTTP" dir=in action=allow protocol=TCP localport=80

REM Allow API traffic (port 8000)
netsh advfirewall firewall add rule name="D and D Initiative API" dir=in action=allow protocol=TCP localport=8000

REM Allow HTTPS traffic (port 443)
netsh advfirewall firewall add rule name="D and D Initiative HTTPS" dir=in action=allow protocol=TCP localport=443

if %errorlevel% equ 0 (
    echo Windows Firewall rules added successfully!
) else (
    echo Failed to add firewall rules. Please run as Administrator.
)

echo Current firewall rules for D and D Initiative:
netsh advfirewall firewall show rule name="D and D Initiative HTTP"
netsh advfirewall firewall show rule name="D and D Initiative API"
netsh advfirewall firewall show rule name="D and D Initiative HTTPS"

pause
