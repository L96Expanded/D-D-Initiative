@echo off
echo Creating D^&D Initiative Tracker shortcut...

rem Get the project root directory (go up 2 levels from setup folder)
set "projectPath=%~dp0..\..\\"
set "shortcutPath=%userprofile%\Desktop\DnD Initiative Tracker.lnk"
set "targetPath=%projectPath%desktop-app\launchers\start-dnd-app.vbs"

rem Create shortcut using PowerShell
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%shortcutPath%'); $Shortcut.TargetPath = '%targetPath%'; $Shortcut.WorkingDirectory = '%projectPath%'; $Shortcut.Description = 'D&D Initiative Tracker - Start Application'; $Shortcut.Save()"

echo.
echo Shortcut created on your Desktop!
echo.
echo You can now:
echo 1. Double-click the "DnD Initiative Tracker" shortcut on your desktop
echo 2. The app will automatically start Docker, build the project, and open the browser
echo.
echo To customize the icon:
echo 1. Right-click the shortcut on your desktop
echo 2. Select Properties
echo 3. Click "Change Icon..."
echo 4. Browse to: C:\Windows\System32\imageres.dll
echo 5. Choose icon #3 (games controller) or any other icon you like
echo.
echo Alternative icons locations:
echo - C:\Windows\System32\shell32.dll (classic Windows icons)
echo - C:\Windows\System32\ddores.dll (additional icons)
echo.
pause