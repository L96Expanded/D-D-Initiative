# 🔧 Cloudflare DNS Configuration Fix

## 🔴 Problem
Your domain `karsusinitiative.com` is timing out because the Cloudflare DNS record is likely pointing to the old Azure Static Web App URL.

## ✅ Current Azure Configuration
- **Azure Static Web App URL**: `wonderful-stone-035aba410.3.azurestaticapps.net` (Working ✅)
- **Azure Custom Domain**: `karsusinitiative.com` (Status: Ready ✅)
- **Backend URL**: `dnd-initiative-prod.azurewebsites.net` (Working ✅)

## 📋 DNS Update Required

### Step 1: Login to Cloudflare
1. Go to https://dash.cloudflare.com/
2. Select your domain: `karsusinitiative.com`

### Step 2: Update DNS Records

Navigate to **DNS** → **Records** and update/verify these records:

#### Root Domain (karsusinitiative.com)
```
Type: CNAME
Name: @
Target: wonderful-stone-035aba410.3.azurestaticapps.net
Proxy status: Proxied (orange cloud) ← IMPORTANT
TTL: Auto
```

#### WWW Subdomain (www.karsusinitiative.com)
```
Type: CNAME
Name: www
Target: wonderful-stone-035aba410.3.azurestaticapps.net
Proxy status: Proxied (orange cloud)
TTL: Auto
```

#### API Subdomain (api.karsusinitiative.com) - Optional
If you want to use api.karsusinitiative.com for the backend:
```
Type: CNAME
Name: api
Target: dnd-initiative-prod.azurewebsites.net
Proxy status: Proxied (orange cloud)
TTL: Auto
```

### Step 3: Verify SSL/TLS Settings

Go to **SSL/TLS** → **Overview**:
- **Encryption mode**: Full (strict) or Full
- This ensures HTTPS works correctly with Azure

### Step 4: Verify Page Rules (Optional)

Go to **Rules** → **Page Rules**:
- You can set up automatic HTTPS redirect if needed
- Example rule: `http://karsusinitiative.com/*` → Always Use HTTPS

## 🔍 Current Issue Analysis

### What's Working ✅
- Azure backend: https://dnd-initiative-prod.azurewebsites.net/api/health (200 OK)
- Azure frontend: https://wonderful-stone-035aba410.3.azurestaticapps.net (200 OK)
- DNS resolution: karsusinitiative.com resolves to Cloudflare IPs

### What's Broken ❌
- Custom domain: https://karsusinitiative.com (Connection timeout)
- Cause: **CNAME record likely pointing to old `.5.azurestaticapps.net` URL**

## ⚡ Quick Fix Commands

After updating Cloudflare DNS, test with:

```powershell
# Test the domain (should work after DNS propagation)
Invoke-WebRequest -Uri "https://karsusinitiative.com" -UseBasicParsing | Select-Object StatusCode

# Check DNS propagation (may take 5-30 minutes)
nslookup karsusinitiative.com

# Test with curl to see actual backend
curl -I https://karsusinitiative.com
```

## ⏱️ DNS Propagation Time
- Cloudflare DNS changes are usually **instant to 5 minutes**
- If proxied (orange cloud), changes are immediate on Cloudflare's edge
- Clear your browser cache after updating

## 🎯 Why This Happened

The Azure Static Web App was likely **redeployed or recreated**, which changed the default hostname from:
- Old: `wonderful-stone-035aba410.5.azurestaticapps.net`
- New: `wonderful-stone-035aba410.3.azurestaticapps.net`

The Cloudflare CNAME record still points to the old `.5` URL, causing timeouts.

## ✅ After Fix Verification

Once DNS is updated, verify all URLs work:

```powershell
# Test main domain
curl https://karsusinitiative.com

# Test www subdomain
curl https://www.karsusinitiative.com

# Test backend (direct Azure URL)
curl https://dnd-initiative-prod.azurewebsites.net/api/health

# Test frontend (direct Azure URL)
curl https://wonderful-stone-035aba410.3.azurestaticapps.net
```

## 🚨 Advanced Troubleshooting (Connection Completely Failing)

### Issue: TCP Connection to Cloudflare IPs Failing

If updating the CNAME doesn't work and you see `TCP connect failed` errors, try these steps:

#### Option 1: Temporarily Disable Cloudflare Proxy (Quick Test)

In Cloudflare DNS settings:
1. Click on the **orange cloud** icon next to your CNAME record
2. Change it to **DNS only** (gray cloud)
3. Wait 2-3 minutes
4. Test: `Invoke-WebRequest -Uri "https://karsusinitiative.com"`

**If this works**, the issue is with Cloudflare's proxy configuration.

#### Option 2: Delete and Re-add Custom Domain in Azure

Sometimes Azure's custom domain needs to be reset:

```powershell
# Remove the custom domain
az staticwebapp hostname delete --name dnd-initiative-frontend --resource-group BCSAI2025-DEVOPS-STUDENTS-A --hostname karsusinitiative.com

# Add it back
az staticwebapp hostname set --name dnd-initiative-frontend --resource-group BCSAI2025-DEVOPS-STUDENTS-A --hostname karsusinitiative.com
```

#### Option 3: Verify Cloudflare DNS Records

**Critical Check**: Make sure your Cloudflare CNAME is **NOT** pointing to:
- ❌ `wonderful-stone-035aba410.5.azurestaticapps.net` (OLD - doesn't work)
- ✅ `wonderful-stone-035aba410.3.azurestaticapps.net` (CURRENT - works)

#### Option 4: Use Azure's Default Domain Temporarily

While troubleshooting, you can use the working Azure URL:
```
https://wonderful-stone-035aba410.3.azurestaticapps.net
```

This bypasses Cloudflare entirely and proves your app is working.

#### Option 5: Check Cloudflare SSL Mode

In Cloudflare → SSL/TLS → Overview:
- Change from "Flexible" to **"Full"** or **"Full (strict)"**
- Azure Static Web Apps require proper SSL/TLS mode

#### Option 6: Flush Cloudflare Cache

In Cloudflare → Caching → Configuration:
- Click **"Purge Everything"**
- This clears any cached DNS or routing information

## 🔧 Quick Fix Script

Run this PowerShell script to reset everything:

```powershell
# Navigate to project
cd "c:\Users\david\OneDrive\Documents\School\DevOps\DnD_Initiative_Project\D-D-Initiative"

# Remove and re-add custom domain in Azure
az staticwebapp hostname delete --name dnd-initiative-frontend --resource-group BCSAI2025-DEVOPS-STUDENTS-A --hostname karsusinitiative.com

# Wait a moment
Start-Sleep -Seconds 10

# Add it back
az staticwebapp hostname set --name dnd-initiative-frontend --resource-group BCSAI2025-DEVOPS-STUDENTS-A --hostname karsusinitiative.com

# Test
Write-Host "Testing domain..." -ForegroundColor Yellow
Start-Sleep -Seconds 30
Invoke-WebRequest -Uri "https://karsusinitiative.com" -UseBasicParsing | Select-Object StatusCode
```

## 📝 Summary

**Primary Action**: Update Cloudflare CNAME record from `.5.azurestaticapps.net` to `.3.azurestaticapps.net`

**If that fails**: 
1. Disable Cloudflare proxy (gray cloud) temporarily
2. Delete and re-add custom domain in Azure
3. Verify SSL/TLS mode is "Full" in Cloudflare
4. Purge Cloudflare cache

**Working URLs Right Now**:
- ✅ Backend: https://dnd-initiative-prod.azurewebsites.net
- ✅ Frontend: https://wonderful-stone-035aba410.3.azurestaticapps.net
- ❌ Custom Domain: https://karsusinitiative.com (needs DNS fix)

This is a DNS/proxy configuration issue - the Azure services are healthy and ready, they just need the correct DNS routing! 🚀
