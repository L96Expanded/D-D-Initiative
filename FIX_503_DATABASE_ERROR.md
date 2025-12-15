# 503 Service Unavailable - Database Connection Fix

## The Problem
Your app is returning **503 Service Unavailable** for both register and login. This means:
- ✅ The backend server is running
- ✅ CORS is configured correctly  
- ❌ **The database connection is failing**

## Quick Fix Steps

### Step 1: Check Database Health (Azure Portal)

1. Go to https://portal.azure.com
2. Navigate to your App Service: `dnd-initiative-prod`
3. Click **Advanced Tools** → **Go** (opens Kudu)
4. In Kudu, click **Debug console** → **CMD**
5. Type: `curl http://localhost:8000/api/health`

**Expected output if database is broken:**
```json
{
  "status": "unhealthy",
  "database": {
    "status": "disconnected",
    "message": "Database error: could not translate host name..."
  }
}
```

### Step 2: Verify DATABASE_URL (Azure Portal)

1. In Azure Portal, go to App Service: `dnd-initiative-prod`
2. Click **Configuration** → **Application settings**
3. Look for `DATABASE_URL`

**Should look like:**
```
postgresql://username:password@servername.postgres.database.azure.com:5432/dbname?sslmode=require
```

**Common issues:**
- ❌ Empty or missing
- ❌ Missing `?sslmode=require` at the end
- ❌ Wrong server name
- ❌ Wrong password (special chars not URL-encoded)

### Step 3: Check if Database Server Exists

1. In Azure Portal, search for "Azure Database for PostgreSQL"
2. Look for your database server (e.g., `dnd-initiative-db`)

**If you don't see a database:**
→ You need to create one! See "Create Database" section below.

**If database exists:**
→ Check firewall rules (Step 4)

### Step 4: Check Firewall Rules

1. Go to your PostgreSQL server in Azure Portal
2. Click **Networking** or **Connection security**
3. Ensure one of these rules exists:
   - **Allow Azure services and resources to access this server** = ON
   - OR a firewall rule for your App Service's outbound IPs

**To add "Allow Azure services":**
1. Toggle ON: "Allow public access from any Azure service"
2. Click **Save**
3. Wait 30 seconds

### Step 5: Test After Each Change

After making changes, restart the app:
1. Go to App Service: `dnd-initiative-prod`
2. Click **Restart** at the top
3. Wait 30 seconds
4. Test the health endpoint:
   ```
   https://dnd-initiative-prod.azurewebsites.net/api/health
   ```

## Create Database (If Missing)

If you don't have a database server at all:

### Option 1: Azure Portal (Easy)
1. Click **Create a resource**
2. Search for "Azure Database for PostgreSQL"
3. Choose **Flexible Server**
4. Fill in:
   - **Server name**: `dnd-initiative-db`
   - **Region**: Same as your App Service (Canada Central)
   - **PostgreSQL version**: 14 or 15
   - **Compute + storage**: Burstable, B1ms (cheapest)
   - **Admin username**: `dbadmin`
   - **Password**: Create a strong password
   - **Networking**: Allow public access, check "Allow Azure services"
5. Click **Review + create** → **Create**
6. Wait 3-5 minutes

### Option 2: Use Existing Database
If your professor provided a shared database:
1. Get the connection string from them
2. Update `DATABASE_URL` in App Service Configuration
3. Make sure your database user has permissions:
   ```sql
   GRANT ALL PRIVILEGES ON DATABASE your_database TO your_user;
   ```

## Fix DATABASE_URL Format

Common mistakes in DATABASE_URL:

### ❌ Wrong: Missing SSL mode
```
postgresql://user:pass@server.postgres.database.azure.com:5432/dbname
```

### ✅ Correct: With SSL mode
```
postgresql://user:pass@server.postgres.database.azure.com:5432/dbname?sslmode=require
```

### ❌ Wrong: Special characters in password not encoded
```
postgresql://user:P@ssw0rd!@server.postgres...
```

### ✅ Correct: URL-encoded password
```
postgresql://user:P%40ssw0rd%21@server.postgres...
```

**URL encode your password:**
- `@` → `%40`
- `!` → `%21`
- `#` → `%23`
- `$` → `%24`
- `%` → `%25`
- Use: https://www.urlencoder.org/

## Update DATABASE_URL in GitHub Secrets

If you need to update the connection string:

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Find `DATABASE_URL` secret
4. Click **Update**
5. Paste the correct connection string
6. Click **Update secret**
7. Go to **Actions** tab
8. Re-run the latest workflow

## Verify Everything Works

After fixing the database connection:

1. **Health check** should show "healthy":
   ```
   https://dnd-initiative-prod.azurewebsites.net/api/health
   ```
   Response:
   ```json
   {
     "status": "healthy",
     "database": {
       "status": "connected",
       "message": "Database is accessible"
     }
   }
   ```

2. **Test registration** at https://karsusinitiative.com/register
   - Should create an account successfully
   - No more 503 errors

3. **Test login** at https://karsusinitiative.com/login
   - Should log in successfully

## Still Not Working?

### Check Application Logs

**In Azure Portal:**
1. Go to App Service: `dnd-initiative-prod`
2. Click **Log stream** in left menu
3. Look for errors

**Or download logs:**
1. Go to App Service
2. Click **Diagnose and solve problems**
3. Click **Application Logs**

**What to look for:**
- `Failed to create database tables`
- `OperationalError`
- `password authentication failed`
- `could not translate host name`

### Common Error Messages

**"could not translate host name"**
→ Server name is wrong in DATABASE_URL

**"password authentication failed"**
→ Password is wrong or needs URL encoding

**"database does not exist"**
→ Create the database: `CREATE DATABASE dnd_initiative;`

**"connection refused"**
→ Firewall is blocking the connection

**"SSL connection required"**
→ Add `?sslmode=require` to DATABASE_URL

## My Database Info (Template)

Fill this in for your reference:

```
Database Server Name: ___________________________
Database Name: dnd_initiative
Admin Username: ___________________________
Admin Password: ___________________________ (keep secure!)
Connection String:
postgresql://[username]:[password]@[servername].postgres.database.azure.com:5432/dnd_initiative?sslmode=require
```

## Need Help?

1. Check the health endpoint first
2. Look at the error message in the health check
3. Check application logs in Azure Portal
4. Verify DATABASE_URL is set correctly
5. Ensure firewall allows Azure services

---

**Quick Checklist:**
- [ ] Database server exists in Azure
- [ ] DATABASE_URL is set in App Service Configuration
- [ ] DATABASE_URL has `?sslmode=require` at the end
- [ ] Password is URL-encoded if it has special characters
- [ ] Firewall allows Azure services
- [ ] Health endpoint shows "connected"
- [ ] App Service has been restarted
