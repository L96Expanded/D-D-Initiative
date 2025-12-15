# IMMEDIATE FIX: 503 Database Error

## The Problem
✅ Your website loads  
✅ Your backend is running  
❌ **Your backend can't connect to the database**  

Result: 503 errors when trying to register or login

---

## Fix It in 5 Minutes (Azure Portal Method)

### Step 1: Check Health Status
Open this URL: **https://dnd-initiative-prod.azurewebsites.net/api/health**

If you see `"database": {"status": "disconnected"}` → Continue to Step 2

### Step 2: Check Your Database Exists

1. Go to https://portal.azure.com
2. Search for **"Azure Database for PostgreSQL"** in the top search bar
3. Look for a database server (might be named like `psql-dnd-initiative-prod` or `dnd-initiative-db`)

**Option A: If you see a database →** Go to Step 3  
**Option B: If NO database exists →** Go to "Create Database" section below

### Step 3: Fix Firewall (If Database Exists)

1. Click on your PostgreSQL server
2. In the left menu, click **Networking**
3. Make sure **"Allow public access from any Azure service within Azure to this server"** is **CHECKED**
4. Click **Save** at the top
5. Wait 30 seconds

### Step 4: Get Connection String

1. Still in your PostgreSQL server page
2. Click **Connection strings** in the left menu
3. Copy the connection string (should look like):
   ```
   postgresql://dbadmin@servername:PASSWORD@servername.postgres.database.azure.com:5432/postgres?sslmode=require
   ```
4. **IMPORTANT:** Replace `PASSWORD` with your actual database password

### Step 5: Update App Service Configuration

1. Go back to the main portal page
2. Search for **"dnd-initiative-prod"** (your App Service)
3. Click on it
4. In the left menu, click **Configuration**
5. Under **Application settings**, look for `DATABASE_URL`

**If DATABASE_URL exists:**
- Click on it
- Click **Edit**
- Replace the value with your corrected connection string from Step 4
- Click **OK**
- Click **Save** at the top

**If DATABASE_URL doesn't exist:**
- Click **New application setting**
- Name: `DATABASE_URL`
- Value: Paste your connection string from Step 4
- Click **OK**
- Click **Save** at the top

### Step 6: Restart and Test

1. At the top of the App Service page, click **Restart**
2. Wait 30 seconds
3. Test health: **https://dnd-initiative-prod.azurewebsites.net/api/health**
4. Should now show: `"database": {"status": "connected"}` ✅
5. Try registering at: **https://karsusinitiative.com/register** ✅

---

## Create Database (If Missing)

If you don't have a PostgreSQL server:

### Quick Create via Azure Portal

1. Go to https://portal.azure.com
2. Click **Create a resource** (top left)
3. Search for **"Azure Database for PostgreSQL"**
4. Click **Create**
5. Choose **Flexible Server**
6. Fill in the form:

**Basics:**
- Subscription: Your Azure for Students
- Resource group: `BCSAI2025-DEVOPS-STUDENTS-A`
- Server name: `dnd-initiative-db` (must be unique)
- Region: **Canada Central** (same as your App Service)
- PostgreSQL version: **15**
- Workload type: **Development**

**Compute + Storage:**
- Click **Configure server**
- Choose **Burstable** tier
- Choose **B1ms** (cheapest option)
- Click **Save**

**Authentication:**
- Admin username: `dbadmin`
- Password: Create a strong password (SAVE THIS!)
- Confirm password

**Networking:**
- Connectivity method: **Public access**
- Check: **Allow public access from any Azure service**
- Firewall rules: Click **Add current client IP address** if you want to connect from your computer

**Review + Create:**
- Click **Review + create**
- Click **Create**
- Wait 3-5 minutes

After creation:
1. Go to the database server
2. Click **Databases** in left menu
3. Click **Add** to create database named: `dnd_initiative`
4. Follow Steps 4-6 above to configure your App Service

---

## Common Issues

### "SSL connection required"
Your DATABASE_URL must end with `?sslmode=require`

**Wrong:**
```
postgresql://user:pass@server.postgres.database.azure.com:5432/dbname
```

**Correct:**
```
postgresql://user:pass@server.postgres.database.azure.com:5432/dbname?sslmode=require
```

### "Password authentication failed"
Your password might have special characters. URL-encode them:
- Replace `@` with `%40`
- Replace `!` with `%21`
- Replace `#` with `%23`

Use this tool: https://www.urlencoder.org/

### Connection String Format

```
postgresql://[USERNAME]:[PASSWORD]@[SERVERNAME].postgres.database.azure.com:5432/[DBNAME]?sslmode=require
```

Example:
```
postgresql://dbadmin:MyP%40ssw0rd@dnd-initiative-db.postgres.database.azure.com:5432/dnd_initiative?sslmode=require
```

---

## Verify It Works

After completing all steps:

1. **Health Check:**
   ```
   https://dnd-initiative-prod.azurewebsites.net/api/health
   ```
   Should show: `"status": "healthy"`

2. **Register:**
   Go to https://karsusinitiative.com/register
   - Fill in email and password
   - Click Create Account
   - Should work! ✅

3. **Login:**
   Go to https://karsusinitiative.com/login
   - Use the email and password you just created
   - Should work! ✅

---

## Still Stuck?

Run this PowerShell script (requires Azure CLI):
```powershell
cd "C:\Users\david\OneDrive\Documents\School\DevOps\DnD_Initiative_Project\D-D-Initiative"
.\check-database.ps1
```

Or check detailed guide: [FIX_503_DATABASE_ERROR.md](FIX_503_DATABASE_ERROR.md)
