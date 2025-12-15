# Fix CORS Error for karsusinitiative.com

## Problem
The backend at `dnd-initiative-prod.azurewebsites.net` is not configured to accept requests from `https://karsusinitiative.com`, causing CORS errors during login/registration.

## Solution

### Option 1: Azure Portal (Easiest)

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your App Service: `dnd-initiative-prod`
3. Click **Configuration** in the left menu
4. Under **Application settings**, find or add `CORS_ORIGINS`
5. Set the value to:
   ```json
   ["https://karsusinitiative.com", "http://localhost:3000", "http://127.0.0.1:3000"]
   ```
6. Click **Save** at the top
7. The app will restart automatically

### Option 2: Azure CLI (Faster)

Run this PowerShell command:

```powershell
az webapp config appsettings set --name dnd-initiative-prod --resource-group <your-resource-group> --settings CORS_ORIGINS='["https://karsusinitiative.com","http://localhost:3000","http://127.0.0.1:3000"]'
```

### Option 3: Update Your Deployment Configuration

If you're using environment variables in your deployment, add this to your configuration:

```
CORS_ORIGINS=["https://karsusinitiative.com","http://localhost:3000","http://127.0.0.1:3000"]
```

## Also Update ALLOWED_HOSTS

Since you're in production mode, also update `ALLOWED_HOSTS`:

```json
["karsusinitiative.com", "dnd-initiative-prod.azurewebsites.net", "localhost", "127.0.0.1"]
```

## Verification

After making the change:
1. Wait 30-60 seconds for the app to restart
2. Open your browser's DevTools (F12)
3. Go to the Console tab
4. Try to register/login at https://karsusinitiative.com
5. The error should be gone!

## Quick Azure CLI Commands

Find your resource group:
```powershell
az webapp list --query "[?name=='dnd-initiative-prod'].{name:name, resourceGroup:resourceGroup}" -o table
```

View current CORS settings:
```powershell
az webapp config appsettings list --name dnd-initiative-prod --resource-group <your-resource-group> --query "[?name=='CORS_ORIGINS']"
```

Update both CORS_ORIGINS and ALLOWED_HOSTS:
```powershell
az webapp config appsettings set --name dnd-initiative-prod --resource-group <your-resource-group> --settings CORS_ORIGINS='["https://karsusinitiative.com","http://localhost:3000","http://127.0.0.1:3000"]' ALLOWED_HOSTS='["karsusinitiative.com","dnd-initiative-prod.azurewebsites.net","localhost","127.0.0.1"]'
```
