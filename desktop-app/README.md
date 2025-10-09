# Desktop Application Structure

This folder contains all files related to the D&D Initiative desktop application shortcuts and setup.

## Folder Structure

### `/launchers/`
Contains the main application launcher scripts:
- `start-dnd-app.bat` - Windows batch file launcher
- `start-dnd-app.ps1` - PowerShell launcher with advanced features
- `start-dnd-app.vbs` - Visual Basic script launcher for silent execution

### `/setup/`
Contains setup and installation scripts:
- `create-shortcut.bat` - Creates a desktop shortcut to the application
- `setup-creature-api.bat` - Windows setup script for the creature API
- `setup-creature-api.sh` - Linux/macOS setup script for the creature API

### `/docs/`
Contains documentation related to the desktop application:
- `LAUNCHER_README.md` - Detailed documentation about the launcher scripts

## Usage

1. Use any of the launcher scripts in `/launchers/` to start the application
2. Run setup scripts from `/setup/` for initial configuration
3. Refer to documentation in `/docs/` for detailed instructions

## Recommended Launcher

For most users, we recommend using `start-dnd-app.ps1` as it provides:
- Better error handling
- Status messages
- Automatic dependency checking
- Graceful error recovery