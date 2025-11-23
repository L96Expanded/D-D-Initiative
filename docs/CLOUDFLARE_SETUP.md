# Cloudflare Setup Guide for karsusinitiative.com

## ⚠️ CRITICAL: Dashboard Configuration Required

**Your tunnel is running but NOT linked to the domain!**

### Quick Fix (5 minutes)

1. **Go to:** https://one.dash.cloudflare.com/
2. **Navigate:** Zero Trust → Networks → Tunnels
3. **Find tunnel:** `80cf609e-e89a-47c4-a759-315191f4e841`
4. **Click:** Configure → Public Hostname tab
5. **Add public hostname:**
   - Subdomain: *(leave empty)*
   - Domain: `karsusinitiative.com`
   - Service Type: `HTTP`
   - URL: `127.0.0.1:80`
6. **Save** and wait 30-60 seconds
7. **Test:** https://karsusinitiative.com

---

## 🌟 Overview

This guide will help you set up your D&D Initiative Tracker with your Cloudflare domain `karsusinitiative.com`. Cloudflare provides better reliability, security, and performance than dynamic DNS.

## 📋 Prerequisites

1. **Domain purchased** and managed through Cloudflare
2. **D&D Initiative Tracker deployed** (run `.\one-click-deploy.bat`)
3. **Home router access** for port forwarding
4. **Static or known external IP** address

## 🔧 Step-by-Step Setup

### Step 1: Find Your External IP Address

1. Visit https://whatismyip.com to find your external IP address
2. Write down this IP address (e.g., `203.0.113.123`)
3. Note: If your IP changes frequently, consider upgrading to a static IP from your ISP

### Step 2: Configure Your Router (Port Forwarding)

**Access your router:**
1. Connect to your home WiFi
2. Open a web browser and go to:
   - http://192.168.1.1 (most common)
   - http://192.168.0.1 (alternative)
   - Check router label for correct IP

**Set up port forwarding:**
1. Log in with admin credentials
2. Find "Port Forwarding" or "Virtual Server" section
3. Add these rules:

| Service Name | External Port | Internal Port | Internal IP | Protocol |
|--------------|---------------|---------------|-------------|----------|
| DnD HTTP     | 80           | 80            | [Your PC IP] | TCP    |
| DnD API      | 8000         | 8000          | [Your PC IP] | TCP    |
| DnD HTTPS    | 443          | 443           | [Your PC IP] | TCP    |

**Find your PC's internal IP:**
```cmd
ipconfig
```
Look for "IPv4 Address" (e.g., `192.168.1.100`)

### Step 3: Configure Cloudflare DNS

**Log into Cloudflare Dashboard:**
1. Go to https://dash.cloudflare.com
2. Select your domain `karsusinitiative.com`
3. Go to **DNS** section

**Add DNS Records:**

| Type | Name | Content | Proxy Status | TTL |
|------|------|---------|--------------|-----|
| A    | @    | [Your External IP] | 🟠 Proxied | Auto |
| A    | www  | [Your External IP] | 🟠 Proxied | Auto |
| A    | api  | [Your External IP] | 🟠 Proxied | Auto |

**Example:**
- `@` → `203.0.113.123` (Proxied)
- `www` → `203.0.113.123` (Proxied)
- `api` → `203.0.113.123` (Proxied)

### Step 4: Configure Cloudflare SSL/TLS

1. Go to **SSL/TLS** → **Overview**
2. Set encryption mode to **"Full (strict)"** for maximum security
3. Go to **SSL/TLS** → **Edge Certificates**
4. Enable **"Always Use HTTPS"**
5. Enable **"HTTP Strict Transport Security (HSTS)"**

### Step 5: Set Up Page Rules (Optional but Recommended)

Go to **Rules** → **Page Rules** and add:

**Rule 1: API Redirect**
- URL: `karsusinitiative.com/api/*`
- Setting: Forwarding URL → `http://karsusinitiative.com:8000/$1`

**Rule 2: Force HTTPS**
- URL: `http://karsusinitiative.com/*`
- Setting: Always Use HTTPS

### Step 6: Configure Cloudflare Security

**Firewall Rules:**
1. Go to **Security** → **WAF**
2. Enable **"Managed Rules"**
3. Set security level to **"Medium"** or **"High"**

**Rate Limiting:**
1. Go to **Security** → **Rate Limiting**
2. Add rule to limit API calls (optional)

### Step 7: Test Your Setup

**Test local access first:**
```cmd
# Test frontend
curl http://localhost

# Test API
curl http://localhost:8000/health
```

**Test domain access:**
```cmd
# Test frontend
curl http://karsusinitiative.com

# Test API
curl http://karsusinitiative.com:8000/health
```

**Test from external network:**
- Use mobile data or ask a friend to test
- Visit: http://karsusinitiative.com
- API: http://karsusinitiative.com:8000/docs

## 🌐 Access URLs After Setup

- **Main Application:** https://karsusinitiative.com
- **API Endpoint:** https://karsusinitiative.com:8000
- **API Documentation:** https://karsusinitiative.com:8000/docs
- **Alternative API:** https://api.karsusinitiative.com (if configured)

## 🛡️ Security Features with Cloudflare

- **DDoS Protection:** Automatic protection against attacks
- **Web Application Firewall:** Blocks malicious requests
- **SSL/TLS Encryption:** Automatic HTTPS certificates
- **Rate Limiting:** Prevents abuse
- **Global CDN:** Faster loading worldwide
- **Analytics:** Traffic insights and security events

## 🔧 Troubleshooting

### Domain doesn't resolve
1. Wait 24-48 hours for DNS propagation
2. Check DNS records in Cloudflare dashboard
3. Use online DNS checker tools

### Can't access from outside
1. Verify router port forwarding is correct
2. Check if ISP blocks port 80/443
3. Test with different external network

### SSL/HTTPS issues
1. Ensure Cloudflare SSL is set to "Full (strict)"
2. Wait for certificate provisioning (up to 24 hours)
3. Check certificate status in Cloudflare dashboard

### API not accessible
1. Verify port 8000 is forwarded
2. Check if application is running: `docker ps`
3. Test local API first: `curl http://localhost:8000/health`

## 📱 Dynamic IP Solutions

If your external IP changes frequently:

**Option 1: Cloudflare API Updates**
- Use Cloudflare API to update DNS records automatically
- Set up a script to check and update IP changes

**Option 2: Dynamic DNS Script**
- Create a scheduled task to update Cloudflare DNS
- Use Cloudflare's API for automatic updates

**Option 3: ISP Static IP**
- Contact your ISP for a static IP address
- Usually costs extra but provides reliability

## 🎯 Final Steps

1. **Share with players:** https://karsusinitiative.com
2. **Bookmark API docs:** https://karsusinitiative.com:8000/docs
3. **Monitor with:** `.\monitor-security.bat`
4. **Backup regularly:** `.\backup-database.bat`

## 🎲 You're Ready to Game!

Your D&D Initiative Tracker is now professionally hosted with Cloudflare protection and accessible worldwide at **karsusinitiative.com**!

---

**Need help?** Check the troubleshooting section or run `.\check-status.bat` for diagnostics.