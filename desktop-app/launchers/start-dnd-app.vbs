Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Get the directory where this script is located and go up to project root
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
projectDir = fso.GetParentFolderName(fso.GetParentFolderName(scriptDir))

' Change to the project directory  
WshShell.CurrentDirectory = projectDir

' Run the PowerShell script from the launchers directory
WshShell.Run "powershell.exe -WindowStyle Normal -ExecutionPolicy Bypass -File """ & scriptDir & "\start-dnd-app.ps1""", 1, False