# Azure Infrastructure - README

## Overview

This directory contains Infrastructure-as-Code (IaC) templates and scripts for deploying the D&D Initiative Tracker to Azure.

## Files

- **main.bicep** - Main Bicep template that orchestrates all resources
- **modules/** - Individual resource modules
  - `container-registry.bicep` - Azure Container Registry
  - `app-service-plan.bicep` - App Service Plan (Linux)
  - `postgresql.bicep` - PostgreSQL Flexible Server
  - `monitoring.bicep` - Application Insights + Log Analytics
  - `web-app.bicep` - Web App (container-based)
- **deploy.ps1** - PowerShell deployment script with interactive prompts
- **parameters.example.json** - Example parameters file

## Prerequisites

1. **Azure CLI** installed
   ```powershell
   winget install Microsoft.AzureCLI
   ```

2. **Azure Account** with active subscription
   ```powershell
   az login
   ```

3. **Permissions** - Contributor role on subscription

## Quick Start

### Option 1: Interactive Deployment (Recommended)

```powershell
# Run the deployment script
.\deploy.ps1 -Environment prod -Location eastus
```

The script will:
- Check prerequisites
- Prompt for subscription selection
- Request database password and secret key
- Display cost estimates
- Deploy all infrastructure
- Output GitHub secrets

### Option 2: Manual Deployment

```bash
# Set parameters
$dbPassword = "YourSecurePassword123!"
$secretKey = "your-64-char-secret-key"

# Deploy
az deployment sub create \
  --name dnd-initiative-deployment \
  --location eastus \
  --template-file main.bicep \
  --parameters environment=prod \
  --parameters dbAdminPassword=$dbPassword \
  --parameters secretKey=$secretKey
```

## Resources Created

| Resource | Type | SKU | Estimated Cost |
|----------|------|-----|----------------|
| Container Registry | ACR | Basic | $5/month |
| App Service Plan | Linux | B1 | $13/month |
| Frontend Web App | Container | Included | - |
| Backend Web App | Container | Included | - |
| PostgreSQL Server | Flexible | B1ms | $15/month |
| Application Insights | Monitoring | Free tier | $0 |
| Log Analytics | Logs | Pay-as-you-go | ~$2/month |
| **Total** | | | **~$35/month** |

## After Deployment

1. **Add GitHub Secrets**
   - Go to repository → Settings → Secrets and variables → Actions
   - Add the secrets displayed after deployment

2. **Create Service Principal**
   ```bash
   az ad sp create-for-rbac \
     --name "github-actions-dnd-initiative" \
     --role contributor \
     --scopes /subscriptions/SUBSCRIPTION_ID/resourceGroups/rg-dnd-initiative-prod \
     --sdk-auth
   ```
   - Add the JSON output as `AZURE_CREDENTIALS` secret

3. **Configure Custom Domain**
   - Update DNS records
   - Add custom domains in Azure Portal
   - Enable HTTPS (automatic SSL)
   - See: `docs/AZURE_MIGRATION_GUIDE.md`

4. **Migrate Database**
   ```bash
   # Export from Docker
   docker exec -t dnd-db pg_dump -U postgres dnd_tracker > backup.sql
   
   # Import to Azure
   psql "host=YOUR_DB_HOST port=5432 dbname=dnd_tracker user=dbadmin password=PASSWORD sslmode=require" < backup.sql
   ```

5. **Trigger Deployment**
   ```bash
   git add .
   git commit -m "feat: add Azure infrastructure"
   git push origin main
   ```

## Monitoring

### View Logs
```bash
az webapp log tail \
  --name app-dnd-initiative-backend-prod \
  --resource-group rg-dnd-initiative-prod
```

### Application Insights
- Azure Portal → Application Insights → `appi-dnd-initiative-prod`
- View: Requests, failures, dependencies, performance

### Container Logs
```bash
az webapp log download \
  --name app-dnd-initiative-backend-prod \
  --resource-group rg-dnd-initiative-prod \
  --log-file logs.zip
```

## Scaling

### Scale Up (Vertical)
```bash
# Upgrade to B2 (2 cores, 3.5GB RAM)
az appservice plan update \
  --name asp-dnd-initiative-prod \
  --resource-group rg-dnd-initiative-prod \
  --sku B2
```

### Scale Out (Horizontal)
```bash
# Add more instances
az appservice plan update \
  --name asp-dnd-initiative-prod \
  --resource-group rg-dnd-initiative-prod \
  --number-of-workers 2
```

## Troubleshooting

### Deployment Fails
```bash
# View deployment logs
az deployment sub show \
  --name dnd-initiative-deployment

# View specific resource errors
az deployment sub operation list \
  --name dnd-initiative-deployment
```

### Container Won't Start
```bash
# Check container logs
az webapp log tail \
  --name app-dnd-initiative-backend-prod \
  --resource-group rg-dnd-initiative-prod

# Check configuration
az webapp config show \
  --name app-dnd-initiative-backend-prod \
  --resource-group rg-dnd-initiative-prod
```

### Database Connection Issues
```bash
# Check firewall rules
az postgres flexible-server firewall-rule list \
  --server-name psql-dnd-initiative-prod \
  --resource-group rg-dnd-initiative-prod

# Add Azure services to firewall
az postgres flexible-server firewall-rule create \
  --resource-group rg-dnd-initiative-prod \
  --name psql-dnd-initiative-prod \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

## Cleanup

### Delete Everything
```bash
az group delete \
  --name rg-dnd-initiative-prod \
  --yes \
  --no-wait
```

⚠️ **Warning**: This permanently deletes all resources and data!

## Cost Management

### View Costs
```bash
az consumption usage list \
  --start-date 2024-01-01 \
  --end-date 2024-01-31
```

### Set Budget Alert
```bash
az consumption budget create \
  --budget-name dnd-initiative-budget \
  --amount 50 \
  --time-grain Monthly \
  --time-period start-date=2024-01-01
```

## Support

- Full migration guide: `../docs/AZURE_MIGRATION_GUIDE.md`
- Azure Documentation: https://docs.microsoft.com/azure
- Azure Pricing: https://azure.com/e/pricing
- Issues: Open issue in GitHub repository
