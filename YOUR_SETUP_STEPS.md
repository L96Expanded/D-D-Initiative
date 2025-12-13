# 🎯 Your Personalized Setup Steps

## ✅ Great News!
You already have these Azure resources deployed:
- ✅ **Database:** `dnd-initiative-db` (PostgreSQL Flexible Server)
- ✅ **Frontend:** `dnd-initiative-frontend` (Static Web App)
- ✅ **Backend:** `dnd-initiative-prod` (App Service)
- ✅ **Resource Group:** `BCSAI2025-DEVOPS-STUDENTS-A`
- ❌ **Storage:** Not created yet (optional - see Step 2B)

You just need to connect them properly! Follow these steps:

---

## Step 1: Get PostgreSQL Connection String (5 minutes)

### A. Find Your Database Admin Username

1. Go to https://portal.azure.com
2. Navigate to your PostgreSQL server: **`dnd-initiative-db`**
3. In the left menu, click **"Overview"**
4. Look for **"Server name"** and **"Admin username"**
   - Server name: `dnd-initiative-db.postgres.database.azure.com`
   - Admin username: (note this down - probably something like `dbadmin` or similar)

### B. Get Your Database Name

1. Still in `dnd-initiative-db`
2. Left menu → **"Databases"**
3. Check if `dnd_tracker` exists
   - ✅ If it exists: great, use it!
   - ❌ If it doesn't: click **"+ Add"** → name it `dnd_tracker` → Create

### C. Construct Connection String

Your DATABASE_URL should be:
```
postgresql://[YOUR_ADMIN_USERNAME]:[YOUR_PASSWORD]@dnd-initiative-db.postgres.database.azure.com:5432/dnd_tracker?sslmode=require
```

**Example:**
```
postgresql://dbadmin:MySecurePass123!@dnd-initiative-db.postgres.database.azure.com:5432/dnd_tracker?sslmode=require
```

**Important:**
- Replace `[YOUR_ADMIN_USERNAME]` with actual username from step A
- Replace `[YOUR_PASSWORD]` with your actual database password
- Keep `?sslmode=require` at the end (required for Azure)

### D. Check Firewall Rules

1. In `dnd-initiative-db`, go to **"Networking"** (left menu)
2. Make sure **"Allow public access from any Azure service within Azure to this server"** is checked
3. This allows your App Service to connect to the database
4. Click **"Save"** if you made changes

---

## Step 2: Azure Storage Setup (OPTIONAL but Recommended)

### ⚠️ You Don't Have Storage Yet - Two Options:

**Option A: Skip for now (Quick fix - database only)**
- Your app will work but uploaded images will be stored locally
- Images may be lost when the app restarts
- You can add storage later

**Option B: Create Azure Storage (Recommended - 10 minutes)**
- Images persist permanently in the cloud
- Better for production use
- Follow steps below

---

### Option A: Skip Storage (Do This First to Fix Database)

**Just update DATABASE_URL secret (Step 3) and deploy. Skip to Step 3 below.**

Your app will work, but use local storage for uploads. You can add Azure Storage later!

---

### Option B: Create Azure Storage Account

#### B1. Create Storage Account

1. Go to Azure Portal: https://portal.azure.com
2. Click **"Create a resource"**
3. Search for **"Storage account"** and select it
4. Click **"Create"**
5. Fill in the details:
   - **Resource Group:** `BCSAI2025-DEVOPS-STUDENTS-A`
   - **Storage account name:** `dndinitiativestorage` (or any unique name, lowercase only)
   - **Region:** Canada Central (same as your App Service for better performance)
   - **Performance:** Standard
   - **Redundancy:** LRS (Locally Redundant Storage - cheapest)
6. Click **"Review + Create"** → **"Create"**
7. Wait for deployment (2-3 minutes)

#### B2. Get Connection String

1. Go to your new Storage Account (e.g., `dndinitiativestorage`)
2. Left menu → **"Access keys"** (under Security + networking section)
3. Click **"Show"** next to key1
4. Copy the **"Connection string"** (the long string that starts with `DefaultEndpointsProtocol=https...`)

It should look like:
```
DefaultEndpointsProtocol=https;AccountName=dndinitiativestorage;AccountKey=LONG_KEY_HERE;EndpointSuffix=core.windows.net
```

#### B3. Create Container

1. Still in your Storage Account
2. Left menu → **"Containers"** (under Data storage section)
3. Click **"+ Container"**
4. Fill in:
   - **Name:** `creature-images`
   - **Public access level:** **Blob (anonymous read access for blobs only)**
5. Click **"Create"**

---

## Step 3: Update GitHub Secrets (5 minutes)

### A. Go to Your GitHub Repository

1. Open your repository in GitHub
2. Click **"Settings"** (top menu)
3. Left sidebar → **"Secrets and variables"** → **"Actions"**

### B. Update DATABASE_URL Secret

1. Look for existing secret named **`DATABASE_URL`**
   - If it exists: click on it → **"Update secret"**
   - If not: click **"New repository secret"**
2. Name: `DATABASE_URL`
3. Value: Paste the connection string from Step 1C
4. Click **"Add secret"** or **"Update secret"**

### C. Update or Add AZURE_STORAGE_CONNECTION_STRING Secret (OPTIONAL)

**Only if you created Azure Storage in Step 2:**

1. Look for **`AZURE_STORAGE_CONNECTION_STRING`**
   - If it exists: click on it → **"Update secret"**
   - If not: click **"New repository secret"**
2. Name: `AZURE_STORAGE_CONNECTION_STRING`
3. Value: Paste the connection string from Step 2 (Option B2)
4. Click **"Add secret"** or **"Update secret"**

**If you skipped Azure Storage:** Don't worry about this secret. Your app will use local storage.

### D. Check SECRET_KEY Exists

1. Make sure you have **`SECRET_KEY`** secret
2. If not, create it:
   - Name: `SECRET_KEY`
   - Value: Use your current JWT_SECRET or generate a new one with:
     ```powershell
     # Run this in PowerShell to generate a secure secret:
     [Convert]::ToBase64String((1..64 | ForEach-Object { Get-Random -Minimum 0 -Maximum 256 }))
     ```

---

## Step 4: Deploy! (5 minutes)

### A. Trigger Deployment

1. In GitHub, go to **"Actions"** tab
2. Click on **"Deploy to Azure App Service"** workflow (left sidebar)
3. Click **"Run workflow"** button (right side)
4. Keep branch as `main`
5. Click green **"Run workflow"** button
6. Wait for the workflow to complete (watch for green checkmark ✅)

### B. Watch the Logs

1. Click on the running workflow
2. Click on **"build-and-deploy"** job
3. Watch the steps execute
4. Look for successful completion messages

---

## Step 5: Test! (5 minutes)

### A. Test Backend

Open these URLs in your browser:

1. **Health Check:**
   ```
   https://dnd-initiative-prod.azurewebsites.net/api/health
   ```
   Should return: `{"status":"healthy"}`

2. **API Docs:**
   ```
   https://dnd-initiative-prod.azurewebsites.net/docs
   ```
   Should show Swagger UI

### B. Test Frontend

Open your Static Web App URL (get it from Azure Portal → `dnd-initiative-frontend` → Overview → URL)

Or check your custom domain if configured.

### C. Test Full Functionality

1. Create an account
2. Login
3. Create an encounter
4. Add a creature
5. Upload an image for the creature
6. **Turn off your computer** 💻❌
7. **Test from your phone or another device** 📱
8. Should still work perfectly! ✅

---

## Step 6: Verify Azure Storage is Working (OPTIONAL)

**Only if you set up Azure Storage in Step 2:**

### A. Check Uploaded Images

1. Go to Azure Portal → Your Storage Account (e.g., `dndinitiativestorage`)
2. Navigate to **Containers** → **creature-images**
3. You should see your uploaded images listed as blobs
4. If images appear here after upload, Azure Storage is working! 🎉

### B. Check Backend Logs

1. Go to Azure Portal → `dnd-initiative-prod`
2. Left menu → **"Log stream"**
3. Upload an image in your app
4. Watch the logs for messages like:
   - `✓ Azure Blob Storage enabled`
   - `Uploading X bytes to Azure Blob`
   - `Successfully uploaded to: https://[yourstorage].blob.core.windows.net/...`

**If you skipped Azure Storage:**
- Logs will show: `ℹ Using local file storage in /tmp/uploads`
- This is fine! App works, but uploads may not persist on restart
- You can add Azure Storage anytime later

---

## 🎉 Success!

If all tests pass, your app is now:
- ✅ Running 24/7 in Azure cloud
- ✅ Using Azure PostgreSQL (not local Docker)
- ✅ Using Azure Blob Storage (persistent uploads)
- ✅ Working even when your computer is off!

---

## 🐛 Troubleshooting

### "Connection refused" or "Can't connect to database"

**Check:**
1. DATABASE_URL has correct format with `?sslmode=require`
2. Database firewall allows Azure services
3. Database `dnd_tracker` exists
4. Username and password are correct

**Test connection locally:**
```powershell
# Install PostgreSQL client if needed, then:
$env:PGPASSWORD="YOUR_PASSWORD"
psql -h dnd-initiative-db.postgres.database.azure.com -U YOUR_USERNAME -d dnd_tracker -c "SELECT version();"
```

### Images not uploading or returning 500 error

**Check:**
1. AZURE_STORAGE_CONNECTION_STRING secret is set correctly
2. Container `creature-images` exists
3. Container has "Blob" public access level
4. Check App Service logs for specific error

### App works but images don't persist

**This means Azure Storage is NOT configured:**
1. Double-check AZURE_STORAGE_CONNECTION_STRING secret
2. Re-run deployment workflow
3. Check App Service logs for "Using local file storage" warning

### Backend returns CORS errors

**Your CORS is already configured, but if you get errors:**
1. Make sure frontend is using correct API URL
2. Check browser console for specific error
3. Verify App Service configuration has correct CORS_ORIGINS

---

## 📞 Need Help?

If you're stuck, check:
1. **Azure Portal Logs:** App Service → Log stream
2. **GitHub Actions Logs:** Actions tab → Latest workflow run
3. **Browser Console:** F12 → Console tab (for frontend errors)
4. **Database Status:** Azure Portal → `dnd-initiative-db` → Overview

---

## ⏱️ Estimated Time

- **Getting connection strings:** 8 minutes
- **Updating GitHub secrets:** 5 minutes
- **Deployment:** 5 minutes
- **Testing:** 5 minutes
- **Total:** About 25 minutes

Good luck! You're almost there! 🚀
