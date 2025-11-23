@echo off
REM Create Desktop Shortcut for One-Click Deployment

echo Creating desktop shortcut for D and D Initiative Tracker deployment...

set "shortcutPath=%USERPROFILE%\Desktop\Deploy DnD Initiative Tracker.lnk"
set "targetPath=%~dp0one-click-deploy.bat"
set "workingDir=%~dp0"

REM Create VBS script to create shortcut
echo Set WshShell = WScript.CreateObject("WScript.Shell") > temp_shortcut.vbs
echo Set Shortcut = WshShell.CreateShortcut("%shortcutPath%") >> temp_shortcut.vbs
echo Shortcut.TargetPath = "%targetPath%" >> temp_shortcut.vbs
echo Shortcut.WorkingDirectory = "%workingDir%" >> temp_shortcut.vbs
echo Shortcut.Description = "Deploy D and D Initiative Tracker for Internet Access" >> temp_shortcut.vbs
echo Shortcut.IconLocation = "shell32.dll,21" >> temp_shortcut.vbs
echo Shortcut.Save >> temp_shortcut.vbs

REM Execute VBS script
cscript //nologo temp_shortcut.vbs

REM Clean up
del temp_shortcut.vbs

echo.
echo Desktop shortcut created successfully!
echo You can now deploy your D and D Initiative Tracker by double-clicking:
echo "Deploy DnD Initiative Tracker" on your desktop
echo.
pause