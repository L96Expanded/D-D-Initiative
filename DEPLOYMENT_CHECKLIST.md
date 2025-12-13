# 🚀 Deployment Checklist - Make Your App Work Without Your Computer

## ❌ Current Problem
Your app stops working when your computer is off because it's using:
- Local Docker PostgreSQL database (on your computer)
- Local filesystem for uploads (on your computer)

## ✅ Solution
Use Azure cloud services that run 24/7:
- Azure PostgreSQL (managed database)
- Azure Blob Storage (cloud file storage)

---

## 📋 Step-by-Step Checklist

### Phase 1: Check What You Have (5 minutes)

- [ ] **Login to Azure Portal**: https://portal.azure.com
- [ ] **Find Resource Group**: `BCSAI2025-DEVOPS-STUDENTS-A`
- [ ] **Check if these exist:**
  - [ ] App Service: `dnd-initiative-prod` ✅ (backend is deployed)
  - [ ] Static Web App: `wonderful-stone-035aba410` ✅ (frontend is deployed)
  - [ ] PostgreSQL Server: `psql-dnd-initiative-prod` ❓ (need to check)
  - [ ] Storage Account: `stdndinitiative` or similar ❓ (need to check)

---

### Phase 2: Set Up Azure PostgreSQL (10-15 minutes)

#### If NOT deployed yet:

- [ ] **Create PostgreSQL Server**
  - Go to Azure Portal → Create Resource → Azure Database for PostgreSQL
  - Choose "Flexible Server"
  - Resource Group: `BCSAI2025-DEVOPS-STUDENTS-A`
  - Server Name: `psql-dnd-initiative-prod`
  - Region: East US
  - PostgreSQL Version: 15
  - Compute: Burstable, B1ms (cheapest option)
  - Storage: 32 GB
  - Admin Username: `dbadmin`
  - Admin Password: **Save this securely!**
  - Click "Review + Create" → "Create"

- [ ] **Configure Firewall** (after database is created)
  - Go to your PostgreSQL server
  - Settings → Networking
  - Check "Allow public access from any Azure service"
  - Add your IP if you want to connect locally
  - Save

- [ ] **Create Database**
  - In PostgreSQL server, go to Databases
  - Click "+ Add"
  - Name: `dnd_tracker`
  - Charset: `UTF8`
  - Collation: `en_US.utf8`
  - Create

#### If already deployed:

- [ ] **Get Connection String**
  - Go to PostgreSQL server → Connect
  - Copy connection string format:
  ```
  postgresql://dbadmin:YOUR_PASSWORD@psql-dnd-initiative-prod.postgres.database.azure.com:5432/dnd_tracker?sslmode=require
  ```
  - Replace `YOUR_PASSWORD` with your actual password
  - **Save this for GitHub Secrets!**

---

### Phase 3: Set Up Azure Storage (10 minutes)

- [ ] **Create Storage Account**
  - Azure Portal → Create Resource → Storage Account
  - Resource Group: `BCSAI2025-DEVOPS-STUDENTS-A`
  - Storage Account Name: `stdndinitiative` (or any unique name)
  - Region: East US
  - Performance: Standard
  - Redundancy: LRS (cheapest)
  - Click "Review + Create" → "Create"

- [ ] **Create Blob Container**
  - Go to Storage Account → Containers
  - Click "+ Container"
  - Name: `creature-images`
  - Public access level: **Blob** (anonymous read for blobs)
  - Create

- [ ] **Get Connection String**
  - Storage Account → Access Keys
  - Show keys
  - Copy "Connection string" from key1
  - It looks like: `DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...;EndpointSuffix=core.windows.net`
  - **Save this for GitHub Secrets!**

---

### Phase 4: Update GitHub Secrets (5 minutes)

- [ ] **Go to GitHub Repository**
  - Navigate to your repo
  - Settings → Secrets and variables → Actions

- [ ] **Add/Update These Secrets:**

  #### DATABASE_URL (CRITICAL!)
  - [ ] Click "New repository secret" or edit existing
  - Name: `DATABASE_URL`
  - Value: `postgresql://dbadmin:YOUR_PASSWORD@psql-dnd-initiative-prod.postgres.database.azure.com:5432/dnd_tracker?sslmode=require`
  - **Make sure to use Azure hostname, not `@postgres:5432`!**

  #### SECRET_KEY
  - [ ] Keep existing or generate new
  - Name: `SECRET_KEY`
  - Value: Your JWT secret (long random string)

  #### AZURE_STORAGE_CONNECTION_STRING (IMPORTANT!)
  - [ ] Click "New repository secret" or edit existing
  - Name: `AZURE_STORAGE_CONNECTION_STRING`
  - Value: (paste the connection string from Azure Storage)

---

### Phase 5: Deploy and Test (10 minutes)

- [ ] **Trigger Deployment**
  - Go to GitHub → Actions tab
  - Click "Deploy to Azure App Service"
  - Click "Run workflow" → "Run workflow"
  - Wait for deployment to complete (watch the logs)

- [ ] **Verify Deployment**
  - [ ] Check workflow completed successfully (green checkmark)
  - [ ] Backend health check: https://dnd-initiative-prod.azurewebsites.net/api/health
    - Should return: `{"status": "healthy"}`
  - [ ] Backend API docs: https://dnd-initiative-prod.azurewebsites.net/docs
    - Should load Swagger UI

- [ ] **Test Application**
  - [ ] Open frontend: https://wonderful-stone-035aba410.3.azurestaticapps.net
  - [ ] Or: https://karsusinitiative.com (if DNS is configured)
  - [ ] Create a test account
  - [ ] Create a test encounter
  - [ ] Upload a creature image
  - [ ] **Turn off your computer** 💻❌
  - [ ] **Test from phone or another device** 📱✅
  - [ ] App should still work!

---

### Phase 6: Verify Azure Storage is Working (5 minutes)

- [ ] **Upload an Image in Your App**
  - Create or edit a creature
  - Upload an image
  - Save

- [ ] **Check Azure Portal**
  - Go to Storage Account → Containers → `creature-images`
  - You should see the uploaded image file
  - If images are there, Azure Storage is working! ✅

- [ ] **Check App Service Logs** (optional)
  - Go to App Service → Log stream
  - Look for messages like:
    - `✓ Azure Blob Storage enabled`
    - `Uploading X bytes to Azure Blob`
  - If you see these, storage integration is working!

---

## 🎉 Success Criteria

Your app is properly deployed when:
- ✅ Backend connects to Azure PostgreSQL (not local Docker)
- ✅ Images upload to Azure Blob Storage (not local filesystem)
- ✅ App works when your computer is OFF
- ✅ Multiple users can access simultaneously
- ✅ Data persists across deployments

---

## 🐛 Troubleshooting

### Backend won't start:
1. Check App Service logs in Azure Portal
2. Verify `DATABASE_URL` secret is correct
3. Check PostgreSQL firewall allows Azure services
4. Ensure database `dnd_tracker` exists

### Can't upload images:
1. Check `AZURE_STORAGE_CONNECTION_STRING` secret is set
2. Verify container `creature-images` exists
3. Ensure container has "Blob" public access level
4. Check App Service logs for error messages

### Database connection errors:
1. Verify connection string format:
   - Should have: `?sslmode=require` at the end
   - Should NOT have: `@postgres:5432` (that's local!)
   - Should have: `@psql-xxx.postgres.database.azure.com:5432`
2. Check PostgreSQL firewall rules
3. Verify admin password is correct

### App works locally but not in Azure:
1. This is the original problem! Make sure:
   - GitHub secret `DATABASE_URL` points to Azure (not local)
   - Not using `.env` file values in production
   - Deployment workflow completed successfully

---

## 📚 Reference Files

After completing this checklist, refer to these files for more details:
- **Full Setup Guide**: [AZURE_SETUP_GUIDE.md](./AZURE_SETUP_GUIDE.md)
- **Environment Template**: [.env.example](./.env.example)
- **Deployment Workflow**: [.github/workflows/azure-app-service-deploy.yml](.github/workflows/azure-app-service-deploy.yml)

---

## ⏱️ Estimated Total Time: 45-60 minutes

Most of this is waiting for Azure resources to provision. The actual work is about 20 minutes!

---

## 💡 Pro Tips

1. **Save all passwords securely** - use a password manager
2. **Test on mobile/other device** - best way to confirm it works
3. **Monitor costs** - Azure has free tiers, but check usage
4. **Enable Application Insights** - helps debug issues in production
5. **Set up alerts** - get notified if something breaks

---

Good luck! 🚀 Your app will be running 24/7 in the cloud soon!
