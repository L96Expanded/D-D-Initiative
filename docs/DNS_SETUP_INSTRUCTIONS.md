# Cloudflare DNS Configuration Guide

## 🎯 **Your Tunnel Information**

**Tunnel ID:** `80cf609e-e89a-47c4-a759-315191f4e841`
**Tunnel Domain:** `80cf609e-e89a-47c4-a759-315191f4e841.cfargotunnel.com`

## 🔧 **DNS Records to Add in Cloudflare**

Go to your Cloudflare dashboard → DNS settings for `karsusinitiative.com` and add these records:

### **Record 1: Main Domain**
- **Type:** CNAME
- **Name:** `@` (or leave blank for root domain)
- **Target:** `80cf609e-e89a-47c4-a759-315191f4e841.cfargotunnel.com`
- **Proxy Status:** 🟠 Proxied
- **TTL:** Auto

### **Record 2: API Subdomain**
- **Type:** CNAME  
- **Name:** `api`
- **Target:** `80cf609e-e89a-47c4-a759-315191f4e841.cfargotunnel.com`
- **Proxy Status:** 🟠 Proxied
- **TTL:** Auto

### **Record 3: WWW Subdomain (Optional)**
- **Type:** CNAME
- **Name:** `www`
- **Target:** `80cf609e-e89a-47c4-a759-315191f4e841.cfargotunnel.com`
- **Proxy Status:** 🟠 Proxied
- **TTL:** Auto

## 🌐 **Final Access URLs**

After DNS configuration, your app will be accessible at:
- **Main App:** https://karsusinitiative.com
- **API:** https://api.karsusinitiative.com
- **WWW:** https://www.karsusinitiative.com

## ✅ **Quick Setup Steps**

1. **Go to:** https://dash.cloudflare.com
2. **Select:** Your domain `karsusinitiative.com`
3. **Click:** DNS tab
4. **Add the three CNAME records above**
5. **Wait:** 1-5 minutes for DNS propagation
6. **Test:** Run `.\start-mobile-tunnel.bat`

## 🚀 **Ready to Test!**

Once DNS is configured, run:
```
.\start-mobile-tunnel.bat
```

Then visit: https://karsusinitiative.com

Your D&D Initiative Tracker will be live! 🎲