# 📁 D&D Initiative Tracker - Project Structure

## 🏗️ Organized Folder Structure

```
D-D-Initiative/
├── 📁 backend/                 # FastAPI backend application
├── 📁 frontend/                # React frontend application
├── 📁 scripts/                 # All automation scripts
│   ├── 📁 deployment/          # Deployment scripts
│   │   ├── one-click-deploy.bat
│   │   └── deploy-production.bat
│   ├── 📁 mobile/              # Mobile hosting scripts
│   │   ├── start-mobile-tunnel.bat
│   │   ├── stop-mobile-tunnel.bat
│   │   └── setup-mobile-deployment.bat
│   ├── 📁 security/            # Security and firewall scripts
│   │   ├── setup-firewall.bat
│   │   ├── setup-security.bat
│   │   └── setup-scheduled-tasks.bat
│   ├── backup-database.bat     # Database backup
│   ├── check-status.bat        # Status monitoring
│   ├── launcher.bat            # Main launcher
│   └── monitor-security.bat    # Security monitoring
├── 📁 cloudflare-tools/        # Cloudflare tunnel tools
│   ├── cloudflared.exe         # Cloudflare daemon
│   ├── cloudflared.bat         # Wrapper script
│   └── tunnel-config.yml       # Tunnel configuration
├── 📁 docs/                    # Documentation files
│   ├── CLOUDFLARE_SETUP.md
│   ├── CLOUD_DEPLOYMENT_GUIDE.md
│   ├── DEPLOYMENT_GUIDE.md
│   ├── DNS_SETUP_INSTRUCTIONS.md
│   ├── DOMAIN_MIGRATION_COMPLETE.md
│   ├── MOBILE_AUTH_FIXED.md
│   ├── MOBILE_HOSTING_COMPLETE.md
│   ├── MOBILE_HOSTING_GUIDE.md
│   ├── PRODUCTION_SETUP.md
│   ├── ROUTER_SETUP.md
│   └── SSL_SETUP_INSTRUCTIONS.txt
├── 📁 config/                  # Configuration files (empty after organization)
├── 📁 tools/                   # Utility tools
│   └── manage_images.py        # Image management utility
├── 📁 nginx/                   # Nginx configuration (if needed)
├── 📁 database-images/         # Creature image database
├── 📁 backups/                 # Database backups (gitignored)
├── 📁 uploads/                 # User uploads (gitignored)
├── 🐳 docker-compose.yml       # Development containers
├── 🐳 docker-compose.prod.yml  # Production containers
├── 📄 creature_database.json   # Creature data
├── 🚀 quick-deploy.bat         # Quick deployment launcher
├── 🌐 start-tunnel.bat         # Quick tunnel starter
├── 📖 README.md                # Main project documentation
└── 🚫 .gitignore               # Git exclusions
```

## 🚀 Quick Access Commands

### Main Operations
- **`quick-deploy.bat`** - One-click deployment of the entire application
- **`start-tunnel.bat`** - Start Cloudflare tunnel for worldwide access

### Organized Scripts
- **Deployment**: `scripts/deployment/` - All deployment-related scripts
- **Mobile Hosting**: `scripts/mobile/` - Mobile tunnel and hosting scripts  
- **Security**: `scripts/security/` - Firewall and security setup scripts

### Documentation
- **Setup Guides**: `docs/` - All setup and configuration guides
- **Migration Docs**: Complete documentation of domain and mobile setup

## 🔒 Security & Privacy

### Files Excluded from GitHub (.gitignore):
- ✅ **Environment files** (`.env`, `.env.production`)
- ✅ **Cloudflare credentials** (`*.json`, `*.pem`)
- ✅ **Database backups** (`backups/`)
- ✅ **User uploads** (`uploads/`)
- ✅ **SSL certificates** (`*.key`, `*.crt`)
- ✅ **Docker runtime data** 
- ✅ **Node modules and build artifacts**

### Safe to Commit:
- ✅ Source code (`backend/`, `frontend/`)
- ✅ Scripts (`scripts/`)
- ✅ Documentation (`docs/`)
- ✅ Docker configurations
- ✅ Database schema and creature data

## 🎯 Benefits of This Organization

1. **Clean Root Directory** - Easy to navigate and understand
2. **Logical Grouping** - Related files are together
3. **Security-First** - Sensitive files properly excluded
4. **Easy Access** - Quick launchers for common operations
5. **Maintainable** - Clear separation of concerns
6. **GitHub-Ready** - Proper gitignore for open source sharing

---

**Your D&D Initiative Tracker is now properly organized and secure! 🐉⚔️**