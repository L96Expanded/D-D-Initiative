# D&D Initiative Tracker - One-Click Deployment

## 🎲 Quick Start

**For the fastest deployment, simply double-click the desktop shortcut:**
- **"Deploy DnD Initiative Tracker"** (created on your desktop)

Or run from the project directory:
```batch
.\one-click-deploy.bat
```

## 📋 Available Scripts

### 🚀 Deployment & Management
- **`one-click-deploy.bat`** - Complete deployment with all services
- **`launcher.bat`** - Interactive control panel for all operations
- **`check-status.bat`** - Quick status check of all services

### 🛡️ Security & Maintenance
- **`backup-database.bat`** - Create database backup
- **`monitor-security.bat`** - Security status monitoring
- **`setup-firewall.bat`** - Configure Windows Firewall (Admin required)

### 🖥️ Shortcuts & Utilities
- **`create-desktop-shortcut.bat`** - Create desktop shortcut for deployment

## 🌐 Access URLs

### Local Access (Available Now)
- **Frontend:** http://localhost
- **API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

### Internet Access (After Router Setup)
- **Frontend:** http://karsusinitiative.com
- **API:** http://karsusinitiative.com:8000

## 🔧 Router Configuration

To make your app accessible from the internet:

1. **Port Forwarding:** Configure your router to forward these ports to your computer:
   - Port 80 (HTTP) → Your computer's local IP
   - Port 8000 (API) → Your computer's local IP

2. **Find Your Local IP:**
   ```batch
   ipconfig
   ```
   Look for "IPv4 Address" under your active network adapter

3. **Router Access:** Usually accessible at:
   - http://192.168.1.1 or http://192.168.0.1
   - Check your router's documentation for specific instructions

## 📊 Container Overview

The deployment creates these containers:
- **dnd_postgres_prod** - PostgreSQL database
- **dnd_backend_prod** - FastAPI backend (port 8000)
- **dnd_frontend_prod** - React frontend (ports 80, 443)

## 🛡️ Security Features

- **Production Environment:** Secure credentials and configurations
- **CORS Protection:** Configured for internet access
- **Rate Limiting:** Protection against abuse
- **JWT Authentication:** Secure user sessions
- **Automated Backups:** Database backup system
- **Security Monitoring:** System health checks

## 🔧 Troubleshooting

### If deployment fails:
1. Make sure Docker Desktop is running
2. Check if ports 80 and 8000 are available
3. Run `.\check-status.bat` to diagnose issues

### If services aren't accessible:
1. Run `.\check-status.bat` to verify container status
2. Check Windows Firewall settings
3. Verify router port forwarding configuration

### For database issues:
1. Run `.\backup-database.bat` to ensure data is safe
2. Check container logs: `docker logs dnd_postgres_prod`

## 📝 Environment Configuration

The deployment uses `.env.production` for configuration:
- Database credentials
- JWT secrets
- Domain settings
- Security configurations

## 🎮 Ready to Play!

Once deployed and router is configured, share these URLs with your players:
- **Main App:** http://karsusinitiative.com
- **Direct API:** http://karsusinitiative.com:8000

## 🆘 Support

If you encounter issues:
1. Run `.\check-status.bat` for diagnostics
2. Check the `ROUTER_SETUP.md` file for detailed router instructions
3. Review container logs: `docker logs [container_name]`

Happy gaming! 🎲