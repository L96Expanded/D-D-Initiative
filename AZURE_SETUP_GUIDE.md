# Azure Setup Guide - Fix Database & Storage Issues

## 🔴 PROBLEM: Your app only works when your local computer is on

**Root Cause:** Your backend is connecting to a local Docker PostgreSQL database instead of Azure's managed database.

---

## ✅ SOLUTION: Complete Azure Setup

### Step 1: Check Your Azure Resources

1. **Log into Azure Portal**: https://portal.azure.com
2. **Find your Resource Group**: Look for `BCSAI2025-DEVOPS-STUDENTS-A`
3. **Check if these resources exist:**
   - ✅ App Service (backend): `dnd-initiative-prod`
   - ❓ PostgreSQL Flexible Server: `psql-dnd-initiative-prod`
   - ❓ Storage Account: `stdndinitiativeprod` or similar

---

### Step 2: Get Azure PostgreSQL Connection String

#### Option A: If PostgreSQL is Already Deployed

1. Go to **Azure Portal** → **Resource Groups** → `BCSAI2025-DEVOPS-STUDENTS-A`
2. Find your **PostgreSQL Flexible Server** (starts with `psql-`)
3. Click on it → **Connect** → **Connection strings**
4. Copy the connection string, it should look like:
   ```
   postgresql://dbadmin:YOUR_PASSWORD@psql-dnd-initiative-prod.postgres.database.azure.com:5432/dnd_tracker?sslmode=require
   ```
5. **Important:** Replace `YOUR_PASSWORD` with your actual database password

#### Option B: If PostgreSQL is NOT Deployed

Run these commands in PowerShell (after installing Azure CLI):

```powershell
# Install Azure CLI if not installed
# Download from: https://aka.ms/installazurecliwindows

# Login to Azure
az login

# Deploy the database infrastructure
cd azure-infrastructure
az deployment group create `
  --resource-group BCSAI2025-DEVOPS-STUDENTS-A `
  --template-file modules/postgresql.bicep `
  --parameters `
    serverName=psql-dnd-initiative-prod `
    databaseName=dnd_tracker `
    location=eastus `
    administratorPassword="YOUR_SECURE_PASSWORD_HERE" `
    sku=Standard_B1ms `
    tags='{"Project":"D&D Initiative Tracker","Environment":"prod"}'

# Get the connection details
az postgres flexible-server show `
  --resource-group BCSAI2025-DEVOPS-STUDENTS-A `
  --name psql-dnd-initiative-prod `
  --query "{Host:fullyQualifiedDomainName}" -o table
```

#### Your Database Connection String Should Be:
```
postgresql://dbadmin:YOUR_DB_PASSWORD@psql-dnd-initiative-prod.postgres.database.azure.com:5432/dnd_tracker?sslmode=require
```

**⚠️ IMPORTANT:** 
- Use SSL mode (`?sslmode=require`) for Azure PostgreSQL
- Never use `@postgres:5432` (that's your local Docker!)
- Never use `localhost` or `127.0.0.1`

---

### Step 3: Set Up Azure Storage for File Uploads

#### Why Use Azure Storage?
- Files persist even when containers restart
- Better performance and scalability
- No risk of losing user uploads

#### Create Storage Account:

1. **Via Azure Portal:**
   - Go to **Create a resource** → **Storage Account**
   - **Resource Group:** `BCSAI2025-DEVOPS-STUDENTS-A`
   - **Name:** `stdndinitiative` (must be globally unique, lowercase, no special chars)
   - **Region:** East US
   - **Performance:** Standard
   - **Redundancy:** LRS (Locally Redundant Storage)
   - Click **Review + Create** → **Create**

2. **Get Connection String:**
   - Go to your Storage Account → **Access keys**
   - Copy **Connection string** from key1
   - It looks like: `DefaultEndpointsProtocol=https;AccountName=stdndinitiative;AccountKey=...;EndpointSuffix=core.windows.net`

3. **Create Container:**
   - Go to **Containers** → **+ Container**
   - **Name:** `creature-images`
   - **Public access level:** Blob (anonymous read access for blobs only)
   - Click **Create**

#### Or via PowerShell:

```powershell
# Create storage account
az storage account create `
  --name stdndinitiative `
  --resource-group BCSAI2025-DEVOPS-STUDENTS-A `
  --location eastus `
  --sku Standard_LRS `
  --kind StorageV2

# Get connection string
az storage account show-connection-string `
  --name stdndinitiative `
  --resource-group BCSAI2025-DEVOPS-STUDENTS-A `
  --query connectionString -o tsv

# Create blob container
az storage container create `
  --name creature-images `
  --account-name stdndinitiative `
  --public-access blob
```

---

### Step 4: Update GitHub Secrets

1. **Go to your GitHub repository**
2. **Settings** → **Secrets and variables** → **Actions**
3. **Update or create these secrets:**

#### Required Secrets:

| Secret Name | Value | Example |
|------------|-------|---------|
| `DATABASE_URL` | Azure PostgreSQL connection string | `postgresql://dbadmin:PASSWORD@psql-dnd-initiative-prod.postgres.database.azure.com:5432/dnd_tracker?sslmode=require` |
| `SECRET_KEY` | Your JWT secret (keep current or generate new) | `jwt_super_secret_key_for_initiative_tracker_production_2024` |
| `AZURE_STORAGE_CONNECTION_STRING` | Azure Storage connection string | `DefaultEndpointsProtocol=https;AccountName=stdndinitiative;AccountKey=...` |

#### How to Update:
- Click **New repository secret** or click on existing secret name
- Paste the value
- Click **Add secret** or **Update secret**

---

### Step 5: Initialize Azure Database Schema

Your backend will automatically create tables on first startup, but you can also manually run:

```powershell
# Connect to Azure PostgreSQL and run init.sql
# Get the host from your connection string
$dbHost = "psql-dnd-initiative-prod.postgres.database.azure.com"
$dbName = "dnd_tracker"
$dbUser = "dbadmin"

# Install PostgreSQL client if not installed
# Download from: https://www.postgresql.org/download/windows/

psql -h $dbHost -U $dbUser -d $dbName -f backend/init.sql
```

Or wait for your backend to initialize it automatically on first run.

---

### Step 6: Verify Deployment

After updating GitHub secrets, trigger a new deployment:

1. **Push to main branch** or go to **Actions** tab → **Run workflow**
2. **Wait for deployment** to complete
3. **Test your backend:**
   - Health: https://dnd-initiative-prod.azurewebsites.net/api/health
   - API Docs: https://dnd-initiative-prod.azurewebsites.net/docs
4. **Test your frontend:**
   - https://wonderful-stone-035aba410.3.azurestaticapps.net
   - Or: https://karsusinitiative.com

---

## 🎉 Success Checklist

- [ ] Azure PostgreSQL is deployed and accessible
- [ ] Azure Storage Account is created with `creature-images` container
- [ ] GitHub secrets updated with Azure connection strings
- [ ] Deployment workflow runs successfully
- [ ] Backend health endpoint returns 200 OK
- [ ] You can create an account and upload creature images
- [ ] App works when your local computer is OFF

---

## 🔧 Troubleshooting

### Backend can't connect to database:
- Check firewall rules on PostgreSQL server
- Ensure you're using `?sslmode=require` in connection string
- Verify password is correct and URL-encoded if it contains special characters

### Images not uploading:
- Check `AZURE_STORAGE_CONNECTION_STRING` secret is set
- Verify container `creature-images` exists and has blob-level public access
- Check backend logs for error messages

### CORS errors:
- Your CORS configuration looks good
- Make sure frontend is using correct API URL
- Check browser console for specific error messages

---

## 📝 Quick Reference

### Current Setup:
- **Frontend:** Azure Static Web Apps
- **Backend:** Azure App Service
- **Database:** Should be Azure PostgreSQL (currently using local Docker)
- **Storage:** Should be Azure Blob Storage (currently using local filesystem)

### After This Fix:
- **Frontend:** Azure Static Web Apps ✅
- **Backend:** Azure App Service ✅
- **Database:** Azure PostgreSQL ✅ (no more local dependency!)
- **Storage:** Azure Blob Storage ✅ (persistent file uploads!)

---

## Need Help?

If you get stuck:
1. Check Azure Portal for resource status
2. Look at GitHub Actions logs for deployment errors
3. Check App Service logs in Azure Portal
4. Test connection strings locally before deploying
