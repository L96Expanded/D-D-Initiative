# Database Connection & 500 Error Fix

## The Real Problem

Looking at your screenshots, you're getting **500 Internal Server Error** - the CORS error is actually a side effect of the server crashing. The issue is most likely:

1. **Database connection is failing** - Azure PostgreSQL isn't accessible
2. **Database tables don't exist** - Tables weren't created during deployment
3. **Database credentials are wrong** - `DATABASE_URL` environment variable is incorrect

## Immediate Diagnostics

### Step 1: Check Backend Health
Open this URL in your browser:
```
https://dnd-initiative-prod.azurewebsites.net/api/health
```

**If you see this:**
```json
{
  "status": "unhealthy",
  "database": {
    "status": "disconnected",
    "message": "Database error: ..."
  }
}
```
→ **Database connection is broken** ❌

**If you see this:**
```json
{
  "status": "healthy",
  "database": {
    "status": "connected",
    "message": "Database is accessible"
  }
}
```
→ **Database is working** ✅ (problem is elsewhere)

### Step 2: Check Application Logs
```powershell
# View recent logs
az webapp log tail --name dnd-initiative-prod --resource-group BCSAI2025-DEVOPS-STUDENTS-A

# Or download logs
az webapp log download --name dnd-initiative-prod --resource-group BCSAI2025-DEVOPS-STUDENTS-A --log-file app-logs.zip
```

**Look for these error patterns:**
- `Failed to create database tables`
- `Database connection error`
- `OperationalError`
- `could not connect to server`
- `password authentication failed`

## Most Likely Causes

### Cause 1: Database Connection String is Wrong

**Check the DATABASE_URL:**
```powershell
az webapp config appsettings list `
  --name dnd-initiative-prod `
  --resource-group BCSAI2025-DEVOPS-STUDENTS-A `
  --query "[?name=='DATABASE_URL'].value" -o tsv
```

**Correct format should be:**
```
postgresql://username:password@hostname.postgres.database.azure.com:5432/database_name?sslmode=require
```

**Common issues:**
- Missing `?sslmode=require` at the end
- Wrong hostname (should end with `.postgres.database.azure.com`)
- URL-encoded password if it contains special characters
- Wrong port (should be 5432)

### Cause 2: Azure PostgreSQL Firewall Rules

Your Azure PostgreSQL server might not allow connections from the App Service.

**Fix:**
```powershell
# Get your database server name
$dbServer = "dnd-initiative-db"  # Replace with your actual server name

# Allow Azure services
az postgres server firewall-rule create `
  --resource-group BCSAI2025-DEVOPS-STUDENTS-A `
  --server-name $dbServer `
  --name AllowAzureServices `
  --start-ip-address 0.0.0.0 `
  --end-ip-address 0.0.0.0

# Get App Service outbound IPs and add them
$outboundIps = az webapp show `
  --name dnd-initiative-prod `
  --resource-group BCSAI2025-DEVOPS-STUDENTS-A `
  --query "outboundIpAddresses" -o tsv

Write-Host "App Service Outbound IPs: $outboundIps"
```

### Cause 3: Database Doesn't Exist

**List databases on your PostgreSQL server:**
```powershell
az postgres flexible-server db list `
  --resource-group BCSAI2025-DEVOPS-STUDENTS-A `
  --server-name dnd-initiative-db -o table
```

**Create database if missing:**
```powershell
az postgres flexible-server db create `
  --resource-group BCSAI2025-DEVOPS-STUDENTS-A `
  --server-name dnd-initiative-db `
  --database-name dnd_initiative
```

### Cause 4: Database User Doesn't Have Permissions

**Connect to database and check:**
```powershell
# Get connection string
$connString = az webapp config appsettings list `
  --name dnd-initiative-prod `
  --resource-group BCSAI2025-DEVOPS-STUDENTS-A `
  --query "[?name=='DATABASE_URL'].value" -o tsv

# Use pgAdmin or psql to connect and run:
# GRANT ALL PRIVILEGES ON DATABASE dnd_initiative TO your_user;
# GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_user;
```

## Quick Fix Commands

### Option 1: Verify and Fix Database URL

```powershell
# First, get your database connection details from Azure
$dbServer = "dnd-initiative-db"  # Your PostgreSQL server name
$dbName = "dnd_initiative"
$dbUser = "dbadmin"  # Your admin username
$dbPassword = "YourSecurePassword123!"  # Your database password

# Construct the correct DATABASE_URL
$databaseUrl = "postgresql://${dbUser}:${dbPassword}@${dbServer}.postgres.database.azure.com:5432/${dbName}?sslmode=require"

# Update the app setting
az webapp config appsettings set `
  --name dnd-initiative-prod `
  --resource-group BCSAI2025-DEVOPS-STUDENTS-A `
  --settings DATABASE_URL="$databaseUrl"

# Restart the app
az webapp restart `
  --name dnd-initiative-prod `
  --resource-group BCSAI2025-DEVOPS-STUDENTS-A
```

### Option 2: Check if Database Server Exists

```powershell
# List all PostgreSQL servers in resource group
az postgres flexible-server list `
  --resource-group BCSAI2025-DEVOPS-STUDENTS-A `
  -o table

# If no database exists, you need to create one first!
```

## What I Fixed in the Code

### 1. Better Error Handling ([backend/app/routers/auth.py](backend/app/routers/auth.py))
- Added try-catch blocks around database operations
- Specific error messages for connection failures vs other errors
- Proper logging of all errors
- Returns 503 Service Unavailable for database connection issues
- Returns 500 Internal Server Error for other database issues

### 2. Database Connection Test ([backend/main.py](backend/main.py))
- Tests database connection before creating tables
- Logs the DATABASE_URL (first 50 chars) for debugging
- Better error messages to help diagnose issues

### 3. Enhanced Health Check
- Already exists at `/api/health`
- Shows database connection status
- Helps quickly identify if database is the problem

## Deployment Steps

1. **Commit and push the fixes:**
```powershell
git add .
git commit -m "Fix database error handling and add better logging"
git push
```

2. **Wait for GitHub Actions to complete** (3-5 minutes)

3. **Check health endpoint:**
```
https://dnd-initiative-prod.azurewebsites.net/api/health
```

4. **If still broken, check logs:**
```powershell
az webapp log tail --name dnd-initiative-prod --resource-group BCSAI2025-DEVOPS-STUDENTS-A
```

## What to Check Right Now

### Priority 1: Is the database server even running?
```powershell
az postgres flexible-server list `
  --resource-group BCSAI2025-DEVOPS-STUDENTS-A `
  -o table
```

### Priority 2: Is DATABASE_URL set correctly?
```powershell
az webapp config appsettings list `
  --name dnd-initiative-prod `
  --resource-group BCSAI2025-DEVOPS-STUDENTS-A `
  --query "[?name=='DATABASE_URL']" -o table
```

### Priority 3: Are there firewall rules blocking the connection?
```powershell
# Replace with your actual database server name
az postgres flexible-server firewall-rule list `
  --resource-group BCSAI2025-DEVOPS-STUDENTS-A `
  --server-name dnd-initiative-db `
  -o table
```

## Expected Outcome After Fix

1. **Health check shows database connected** ✅
2. **Registration works** ✅  
3. **Login works** ✅
4. **No more 500 errors** ✅
5. **Better error messages if something goes wrong** ✅

## Still Having Issues?

If after all this the problem persists:

1. **Check if you have a database at all:**
   - Go to Azure Portal
   - Look for "Azure Database for PostgreSQL flexible servers"
   - If nothing exists, you need to create one first

2. **Share the logs with me:**
   ```powershell
   az webapp log tail --name dnd-initiative-prod --resource-group BCSAI2025-DEVOPS-STUDENTS-A > logs.txt
   ```

3. **Check the GitHub Actions deployment logs:**
   - Go to your GitHub repository
   - Click "Actions" tab
   - Look at the latest workflow run
   - Check for any errors during deployment

---

**Next Steps:**
1. Run the diagnostic commands above
2. Share the output of the health check endpoint
3. If database doesn't exist, we need to create it first
4. If database exists but connection fails, we need to fix the connection string
