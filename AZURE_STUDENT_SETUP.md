# Azure for Students - Quick Setup Guide

## ⚡ FAST TRACK TO AZURE (For Student Accounts)

### 🎯 YOU ARE HERE:
- IE University managed subscription ❌ (no permissions)
- Need: Personal Azure for Students account ✅

---

## 📝 STEP-BY-STEP (30 minutes total)

### STEP 1: Get Azure for Students (10 min)

1. **Open browser:** https://azure.microsoft.com/free/students/
2. **Click:** "Activate now" or "Start free"
3. **Sign in:** with `dvelasco.ieu2023@student.ie.edu`
4. **Verify:** Upload student ID or use school verification
5. **Complete:** Profile information
6. **Get:** $100 free credit (no credit card!)

---

### STEP 2: Install Azure CLI (5 min)

**Download:** https://aka.ms/installazurecliwindows

Or use winget:
```powershell
winget install Microsoft.AzureCLI
```

**IMPORTANT:** Restart PowerShell after installation!

---

### STEP 3: Login to YOUR subscription (2 min)

```powershell
# Login (opens browser)
az login

# List subscriptions
az account list --output table

# You should see TWO subscriptions:
# 1. IE University managed (5841fd26-...) - DON'T USE THIS
# 2. Azure for Students (new one) - USE THIS ONE

# Set your NEW subscription as active
az account set --subscription "Azure for Students"

# Verify
az account show
```

---

### STEP 4: Deploy to Azure (15 min)

```powershell
cd azure-infrastructure
.\deploy.ps1 -Environment prod
```

The script will:
- Create resource group
- Deploy all Azure resources
- Give you GitHub secrets

---

## 🚨 TROUBLESHOOTING

### Issue: "az command not found"
**Solution:** Restart PowerShell after Azure CLI installation

### Issue: Still getting permission errors
**Solution:** Make sure you selected the RIGHT subscription:
```powershell
az account list --output table
az account set --subscription "Azure for Students"
```

### Issue: Student verification fails
**Solution:** 
- Use your student ID document
- Or contact: https://azure.microsoft.com/support/

---

## ⏰ TIMELINE:
- Azure for Students signup: 10 min
- Azure CLI install: 5 min  
- Login & setup: 2 min
- Deployment: 15 min
- **Total: ~30 minutes**

---

## 📋 AFTER DEPLOYMENT:

1. **Add GitHub Secrets** (script tells you which ones)
2. **Push to GitHub:**
   ```bash
   git push origin main
   ```
3. **Watch deployment:** GitHub Actions tab
4. **Access app:** Azure Portal → Web Apps

---

## 💡 NEED HELP?

Run this in PowerShell to see your subscriptions:
```powershell
az login
az account list --output table
```

Look for:
- ❌ IE managed: `5841fd26-0b2d-4bd0-8dcb-40add3353593`
- ✅ Your new one: Different ID, "Azure for Students" name

---

**Ready?** Follow the steps above, then run `.\deploy.ps1`
