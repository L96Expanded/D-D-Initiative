# 🎲 D&D Initiative Tracker - One-Click Launcher

This folder contains scripts to automatically start your D&D Initiative Tracker with a single click!

## 🚀 Quick Setup

### Option 1: Create Desktop Shortcut (Recommended)
1. **Double-click** `create-shortcut.bat`
2. A shortcut will appear on your Desktop called "D&D Initiative Tracker"
3. **Double-click the shortcut** to start the app!

### Option 2: Run Scripts Directly
- **Double-click** `start-dnd-app.bat` to start the application
- Or **double-click** `start-dnd-app.vbs` for a cleaner experience

## ✨ What the scripts do automatically:

1. **🐳 Check Docker Status** - Starts Docker Desktop if not running
2. **🐍 Activate Environment** - Activates Python virtual environment if present
3. **🛑 Clean Slate** - Stops any existing containers
4. **🔨 Build & Start** - Runs `docker-compose up --build`
5. **⏳ Wait for Ready** - Waits for the application to be available
6. **🌐 Open Browser** - Opens http://localhost:3000 automatically
7. **✅ Ready to Play!** - Your D&D tracker is ready for use

## 🎯 Customizing the Icon

After creating the shortcut:

1. **Right-click** the "D&D Initiative Tracker" shortcut on your desktop
2. Select **Properties**
3. Click **Change Icon...**
4. Browse to one of these locations for cool icons:
   - `C:\Windows\System32\imageres.dll` (recommended - icon #3 is a game controller)
   - `C:\Windows\System32\shell32.dll` (classic Windows icons)
   - `C:\Windows\System32\ddores.dll` (additional modern icons)

## 🎮 Usage

### Starting the App:
- **Double-click** the desktop shortcut
- Wait for the PowerShell window to show "Ready for your D&D session!"
- Your browser will automatically open to the app

### Stopping the App:
- **Close the PowerShell window**, or
- **Press Ctrl+C** in the PowerShell window, or
- Run `docker-compose down` in the project folder

## 🔧 Troubleshooting

### Docker Issues:
- Make sure Docker Desktop is installed
- The script will try to start Docker automatically
- If it fails, start Docker Desktop manually first

### Permission Issues:
- If PowerShell blocks the script, run this once as Administrator:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

### Port Conflicts:
- Make sure ports 3000, 8000, and 5432 are available
- Close any other applications using these ports

## 📁 Files Explained

- `start-dnd-app.ps1` - Main PowerShell script with all the logic
- `start-dnd-app.bat` - Batch file wrapper for PowerShell script  
- `start-dnd-app.vbs` - VBScript launcher (runs more quietly)
- `create-shortcut.bat` - Creates a desktop shortcut
- `LAUNCHER_README.md` - This documentation

## 🎉 Happy Gaming!

Now you can start your D&D sessions with just one click! The app will be ready by the time you gather your party. 🗡️✨