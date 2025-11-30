# 🟠 Cloudflare Proxy (Orange Cloud) Fix

## 🔴 Problem
Your site works with **gray cloud** (DNS only) but **fails with orange cloud** (Cloudflare proxy enabled).

**Symptoms**:
- ✅ Gray cloud: Site loads perfectly
- ❌ Orange cloud: Connection timeout, 522 errors, or site doesn't load

## 🎯 Root Cause
**Azure Static Web Apps require specific SSL/TLS settings when behind Cloudflare's proxy.** The default "Flexible" SSL mode doesn't work with Azure.

## ✅ Solution: Configure Cloudflare SSL Properly

### Step 1: Fix SSL/TLS Mode (CRITICAL!)

1. Login to **Cloudflare Dashboard**: https://dash.cloudflare.com/
2. Select your domain: **karsusinitiative.com**
3. Go to **SSL/TLS** → **Overview**
4. Change encryption mode:
   - ❌ **NOT** "Flexible" (this breaks Azure)
   - ❌ **NOT** "Off"
   - ✅ **Change to "Full"** (recommended)
   - ✅ **OR "Full (strict)"** (more secure)

**Why this matters**: Azure Static Web Apps have HTTPS enabled by default. Cloudflare needs to connect via HTTPS too, not HTTP.

### Step 2: Enable Always Use HTTPS

1. Stay in **SSL/TLS** section
2. Go to **Edge Certificates**
3. Enable these settings:
   - ✅ **Always Use HTTPS**: ON
   - ✅ **Automatic HTTPS Rewrites**: ON
   - ✅ **Minimum TLS Version**: 1.2 (default is fine)

### Step 3: Verify DNS Settings

Go to **DNS** → **Records** and confirm:

```
Type: CNAME
Name: @
Target: wonderful-stone-035aba410.3.azurestaticapps.net
Proxy: ON (orange cloud) ← Should work now!
TTL: Auto
```

### Step 4: Clear Cloudflare Cache (Important!)

1. Go to **Caching** → **Configuration**
2. Click **"Purge Everything"**
3. Confirm the purge
4. Wait 1 minute

### Step 5: Test

After making the changes, test:

```powershell
# Test from PowerShell
Invoke-WebRequest -Uri "https://karsusinitiative.com" -UseBasicParsing | Select-Object StatusCode

# Should return: StatusCode 200
```

Or just visit https://karsusinitiative.com in your browser (hard refresh with Ctrl+Shift+R)

## 🔧 Troubleshooting

### Still Getting 522 Error?

**522 = Connection Timed Out** between Cloudflare and Azure

**Check these**:
1. SSL/TLS mode is "Full" or "Full (strict)" ✅
2. CNAME points to correct URL (`.3.azurestaticapps.net`) ✅
3. Cloudflare cache is purged ✅
4. Wait 2-3 minutes for changes to propagate ⏱️

### Still Getting 525 Error?

**525 = SSL Handshake Failed**

**Solution**:
1. Change SSL/TLS mode to **"Full"** (not "Full (strict)")
2. Azure's certificate might not be trusted by Cloudflare in strict mode
3. "Full" mode is secure enough and works reliably

### Site Loads But CSS/JS Don't Load?

**Check**:
1. Go to **SSL/TLS** → **Edge Certificates**
2. Enable **"Automatic HTTPS Rewrites"**
3. This fixes mixed content (HTTP/HTTPS) issues

### Cloudflare Shows "Active" But Site Not Loading?

**Wait for DNS propagation**:
- DNS changes: 1-5 minutes (usually instant with Cloudflare)
- SSL changes: 1-2 minutes
- Cache purge: 30 seconds

**Force refresh**:
```powershell
# Flush local DNS cache
ipconfig /flushdns

# Test again
Invoke-WebRequest -Uri "https://karsusinitiative.com" -UseBasicParsing
```

## 📊 Recommended Cloudflare Configuration

### SSL/TLS Settings
- **Encryption Mode**: Full ✅
- **Always Use HTTPS**: ON ✅
- **HSTS**: OFF (Azure handles this)
- **Minimum TLS Version**: 1.2 ✅
- **Automatic HTTPS Rewrites**: ON ✅

### Speed Settings
- **Auto Minify**: OFF (Azure already optimizes)
- **Brotli**: ON ✅
- **Early Hints**: ON ✅
- **HTTP/2 to Origin**: ON ✅
- **HTTP/3 (QUIC)**: ON ✅

### Network Settings
- **WebSockets**: ON (if your app needs them) ✅
- **gRPC**: OFF (not needed)
- **Onion Routing**: OFF (not needed)

### Firewall Settings
- **Security Level**: Medium (default) ✅
- **Browser Integrity Check**: ON ✅
- **Challenge Passage**: 30 minutes ✅

### Page Rules (Optional)
Create a page rule for better control:

**URL Pattern**: `karsusinitiative.com/*`
**Settings**:
- SSL: Full
- Cache Level: Standard
- Browser Cache TTL: Respect Existing Headers

## 🎯 Quick Fix: Gray Cloud (DNS Only)

If you need the site working RIGHT NOW and can't wait:

1. Go to **DNS** → **Records**
2. Find your CNAME record for `@` (root domain)
3. Click the **orange cloud** icon → it turns **gray**
4. Site will work immediately (within 1 minute)

**Trade-offs**:
- ✅ Site works immediately
- ❌ No Cloudflare CDN (slower for global users)
- ❌ No DDoS protection
- ❌ No caching
- ❌ No Cloudflare firewall

**Use this only temporarily while you fix SSL settings!**

## ✅ Final Verification

After configuring everything correctly:

### 1. Check SSL Certificate
Visit https://www.ssllabs.com/ssltest/analyze.html?d=karsusinitiative.com
- Should show grade A or B
- Should show valid certificate

### 2. Check DNS Propagation
Visit https://www.whatsmydns.net/#CNAME/karsusinitiative.com
- Should show `wonderful-stone-035aba410.3.azurestaticapps.net` globally

### 3. Test HTTPS
```powershell
# Should return 200 OK
Invoke-WebRequest -Uri "https://karsusinitiative.com" -UseBasicParsing | Select-Object StatusCode

# Should return 200 OK
Invoke-WebRequest -Uri "https://www.karsusinitiative.com" -UseBasicParsing | Select-Object StatusCode
```

### 4. Test in Browser
1. Open **Incognito/Private browsing** window
2. Visit https://karsusinitiative.com
3. Should load perfectly ✅
4. Check DevTools Console (F12) → No errors ✅

## 📝 Summary

**The Issue**: Cloudflare's default "Flexible" SSL doesn't work with Azure Static Web Apps

**The Fix**: 
1. Change SSL/TLS mode to **"Full"**
2. Enable **"Always Use HTTPS"**
3. Purge Cloudflare cache
4. Turn orange cloud back ON

**Result**: Orange cloud (proxy) works perfectly with proper SSL settings! 🎉

**Time to Fix**: ~5 minutes
**Time to Propagate**: ~2 minutes

---

**Need Help?** If you're still having issues after following this guide, check:
1. SSL/TLS mode is "Full" (not Flexible, not Off)
2. CNAME is correct (`.3.azurestaticapps.net` not `.5`)
3. Cache is purged in Cloudflare
4. Wait 5 minutes after making changes
5. Clear browser cache completely
