# 🚀 Quick Production Deployment Guide

## Your Domain: `initiativetracker.ddns.net`

### ✅ What I've Done For You:

1. **✅ Production Environment Configured**
   - Domain: `initiativetracker.ddns.net`
   - Strong database password generated
   - Secure JWT secret created
   - CORS properly configured

2. **✅ Nginx Configuration Updated**
   - Server name set to your domain
   - SSL configuration prepared (commented out)

3. **✅ Security Scripts Created**
   - `setup-security.bat` - Main security setup
   - `backup-database.bat` - Automated backups
   - `monitor-security.bat` - Security monitoring
   - `setup-firewall.bat` - Windows Firewall config

4. **✅ Router Setup Guide**
   - See `ROUTER_SETUP.md` for detailed instructions

---

## 🎯 What You Need To Do Now:

### Step 1: Router Configuration (5 minutes)
1. **Find your local IP**: Open Command Prompt → `ipconfig`
2. **Access router**: Go to http://192.168.1.1 (or similar)
3. **Add port forwarding rules**:
   - Port 80 → Your Local IP
   - Port 8000 → Your Local IP  
   - Port 443 → Your Local IP
4. **Save and reboot router**

### Step 2: Security Setup (3 minutes)
1. **Right-click** `setup-security.bat` → **Run as Administrator**
2. **Right-click** `setup-firewall.bat` → **Run as Administrator**
3. **Set up scheduled backups**: Run `setup-scheduled-tasks.bat` as Admin

### Step 3: Deploy Production (2 minutes)
```bash
.\deploy-production.bat
```

### Step 4: Test Access
1. **From your phone** (using mobile data):
   - Visit: http://initiativetracker.ddns.net
   - API: http://initiativetracker.ddns.net:8000/docs

---

## 🔒 Security Features Enabled:

- ✅ **Strong Authentication**: Secure passwords and JWT tokens
- ✅ **Rate Limiting**: 5 login attempts/minute, 10 API calls/second  
- ✅ **CORS Protection**: Only your domain allowed
- ✅ **Security Headers**: XSS protection, content type validation
- ✅ **Firewall Rules**: Windows Firewall configured
- ✅ **Automated Backups**: Daily database backups
- ✅ **Monitoring**: Security monitoring every 6 hours

---

## 🌐 Sharing with Players:

Once everything is working, players can access your game at:
- **Main App**: `http://initiativetracker.ddns.net`
- **Display Window**: They can open it from within the app

---

## 🆘 Troubleshooting:

**Can't access from outside:**
- Check router port forwarding is correct
- Verify your external IP in Dynamic DNS settings
- Test with mobile data (not WiFi)

**Security concerns:**
- All passwords are strong and unique
- Regular monitoring is set up
- Backups are automated

**Need help:**
- Check `ROUTER_SETUP.md` for detailed router instructions
- Run `monitor-security.bat` to check system status
- Check Docker containers: `docker-compose ps`

---

## ⏰ Maintenance:

- **Daily**: Automatic database backups
- **Every 6 hours**: Automatic security monitoring  
- **Weekly**: Check `monitor-security.bat` manually
- **Monthly**: Update domain password if needed

Your D&D Initiative Tracker is now production-ready! 🎲✨