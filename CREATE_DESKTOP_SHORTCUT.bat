@echo off
REM ============================================================================
REM  Create Desktop Shortcut for D&D Initiative Tracker
REM ============================================================================

echo Creating desktop shortcut for D&D Initiative Tracker...

set "currentDir=%~dp0"
set "shortcutPath=%USERPROFILE%\Desktop\🐉 Start D&D Tracker.lnk"

REM Create VBS script to make the shortcut
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%shortcutPath%" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%currentDir%START_EVERYTHING.bat" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%currentDir%" >> CreateShortcut.vbs
echo oLink.Description = "Start D&D Initiative Tracker with worldwide access" >> CreateShortcut.vbs
echo oLink.IconLocation = "shell32.dll,21" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs

REM Run the VBS script
cscript CreateShortcut.vbs >nul

REM Clean up
del CreateShortcut.vbs

echo ✓ Desktop shortcut created: "🐉 Start D&D Tracker"
echo.
echo You can now start your D&D tracker by double-clicking the desktop icon!
echo.
pause