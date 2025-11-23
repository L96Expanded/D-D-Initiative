# Azure Migration Guide

## Overview

This guide will help you migrate your D&D Initiative Tracker from local Docker + Cloudflare Tunnel to a fully Azure-hosted solution with automated CI/CD.

## Architecture

### Current Setup
- Docker Compose (local)
- Cloudflare Tunnel for public access
- PostgreSQL in Docker
- Manual deployment

### Target Azure Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Actions CI/CD                     │
│  (Build → Test → Push to ACR → Deploy to Azure)            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Azure Container Registry                  │
│              (Stores Docker images securely)                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  Azure App Service (Web Apps)                │
│  ┌──────────────────┐        ┌──────────────────┐          │
│  │  Frontend Web App │        │  Backend Web App │          │
│  │  (React + Nginx) │◄────►  │    (FastAPI)     │          │
│  └──────────────────┘        └──────────────────┘          │
│         HTTPS                        HTTPS                   │
│    Custom Domain                 API Subdomain               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│         Azure Database for PostgreSQL - Flexible Server     │
│           (Managed, automated backups, scaling)              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Azure Monitor + Application Insights            │
│         (Logs, metrics, alerts, performance monitoring)      │
└─────────────────────────────────────────────────────────────┘
```

## Azure Resources Required

### 1. Resource Group
- **Purpose**: Logical container for all resources
- **Name**: `rg-dnd-initiative-prod`
- **Region**: East US (or your preferred region)

### 2. Azure Container Registry (ACR)
- **Purpose**: Store Docker images securely
- **Name**: `acrdndinitiative` (must be globally unique)
- **SKU**: Basic (sufficient for small projects)
- **Cost**: ~$5/month

### 3. Azure App Service Plan
- **Purpose**: Host web applications
- **Name**: `asp-dnd-initiative-prod`
- **SKU**: B1 (Basic) - 1 core, 1.75GB RAM
- **Cost**: ~$13/month
- **Note**: Can host both frontend and backend

### 4. Azure Web Apps (2)
- **Frontend App**
  - Name: `app-dnd-initiative-frontend`
  - Container: nginx with React build
  - Custom domain: karsusinitiative.com
  
- **Backend App**
  - Name: `app-dnd-initiative-backend`
  - Container: FastAPI application
  - Custom domain: api.karsusinitiative.com

### 5. Azure Database for PostgreSQL - Flexible Server
- **Purpose**: Managed PostgreSQL database
- **Name**: `psql-dnd-initiative-prod`
- **SKU**: Burstable B1ms (1 vCore, 2GB RAM)
- **Storage**: 32GB
- **Cost**: ~$15/month
- **Features**: Automated backups, high availability option

### 6. Azure Application Insights
- **Purpose**: Monitoring and diagnostics
- **Name**: `appi-dnd-initiative-prod`
- **Cost**: Free tier includes 5GB/month

### Total Estimated Cost: ~$35-40/month

## Prerequisites

1. **Azure Account** (you have this ✓)
2. **Azure CLI** installed locally
3. **GitHub Repository** with admin access
4. **Custom Domain** (karsusinitiative.com)

## Migration Steps

### Phase 1: Setup Azure Infrastructure (30 minutes)

#### Step 1.1: Install Azure CLI (if not installed)
```bash
# Windows (PowerShell)
winget install Microsoft.AzureCLI

# Or download from: https://aka.ms/installazurecliwindows
```

#### Step 1.2: Login to Azure
```bash
az login
```

#### Step 1.3: Create Resources Using Bicep
We'll use Infrastructure-as-Code (Bicep) to create all resources consistently.

```bash
# Navigate to project directory
cd azure-infrastructure

# Deploy infrastructure
az deployment sub create \
  --location eastus \
  --template-file main.bicep \
  --parameters environment=prod
```

This creates:
- Resource Group
- Container Registry
- App Service Plan
- 2 Web Apps
- PostgreSQL Server
- Application Insights

### Phase 2: Configure GitHub Secrets (10 minutes)

#### Step 2.1: Create Azure Service Principal
```bash
# Get subscription ID
az account show --query id -o tsv

# Create service principal with contributor role
az ad sp create-for-rbac \
  --name "github-actions-dnd-initiative" \
  --role contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/rg-dnd-initiative-prod \
  --sdk-auth
```

Copy the entire JSON output.

#### Step 2.2: Add GitHub Secrets
Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:
- `AZURE_CREDENTIALS`: The JSON from service principal creation
- `AZURE_REGISTRY_NAME`: `acrdndinitiative`
- `AZURE_REGISTRY_USERNAME`: (from ACR → Access keys)
- `AZURE_REGISTRY_PASSWORD`: (from ACR → Access keys)
- `DATABASE_URL`: (PostgreSQL connection string)
- `SECRET_KEY`: (your FastAPI secret key)

#### Step 2.3: Get PostgreSQL Connection String
```bash
# Get connection string
az postgres flexible-server show-connection-string \
  --server-name psql-dnd-initiative-prod \
  --database-name dnd_tracker \
  --admin-user dbadmin \
  --admin-password 'YourSecurePassword123!'
```

Format for GitHub secret:
```
postgresql://dbadmin:YourSecurePassword123!@psql-dnd-initiative-prod.postgres.database.azure.com/dnd_tracker?sslmode=require
```

### Phase 3: Configure Custom Domain (15 minutes)

#### Step 3.1: Get App Service IPs
```bash
# Get frontend IP
az webapp show \
  --name app-dnd-initiative-frontend \
  --resource-group rg-dnd-initiative-prod \
  --query defaultHostName -o tsv

# Get backend IP
az webapp show \
  --name app-dnd-initiative-backend \
  --resource-group rg-dnd-initiative-prod \
  --query defaultHostName -o tsv
```

#### Step 3.2: Update DNS Records
In your domain registrar (Cloudflare DNS):

| Type  | Name | Value |
|-------|------|-------|
| CNAME | @    | app-dnd-initiative-frontend.azurewebsites.net |
| CNAME | api  | app-dnd-initiative-backend.azurewebsites.net |

#### Step 3.3: Configure Custom Domains in Azure
```bash
# Add custom domain to frontend
az webapp config hostname add \
  --webapp-name app-dnd-initiative-frontend \
  --resource-group rg-dnd-initiative-prod \
  --hostname karsusinitiative.com

# Add custom domain to backend
az webapp config hostname add \
  --webapp-name app-dnd-initiative-backend \
  --resource-group rg-dnd-initiative-prod \
  --hostname api.karsusinitiative.com

# Enable HTTPS (free SSL from Azure)
az webapp config ssl bind \
  --name app-dnd-initiative-frontend \
  --resource-group rg-dnd-initiative-prod \
  --certificate-thumbprint auto \
  --ssl-type SNI

az webapp config ssl bind \
  --name app-dnd-initiative-backend \
  --resource-group rg-dnd-initiative-prod \
  --certificate-thumbprint auto \
  --ssl-type SNI
```

### Phase 4: Deploy Application (Automated via GitHub Actions)

#### Step 4.1: Push Code to GitHub
```bash
git add .
git commit -m "feat: add Azure infrastructure and CI/CD"
git push origin main
```

#### Step 4.2: Monitor Deployment
1. Go to GitHub repository → Actions tab
2. Watch the CI/CD pipeline execute
3. Stages: Test → Build → Push to ACR → Deploy to Azure

### Phase 5: Database Migration (15 minutes)

#### Step 5.1: Export Current Data
```bash
# From your local Docker container
docker exec -t dnd-db pg_dump -U postgres dnd_tracker > backup.sql
```

#### Step 5.2: Import to Azure PostgreSQL
```bash
# Connect to Azure PostgreSQL
psql "host=psql-dnd-initiative-prod.postgres.database.azure.com \
      port=5432 \
      dbname=dnd_tracker \
      user=dbadmin \
      password=YourSecurePassword123! \
      sslmode=require" \
     < backup.sql
```

### Phase 6: Verify Deployment (5 minutes)

#### Test Endpoints
```bash
# Test frontend
curl https://karsusinitiative.com

# Test backend health
curl https://api.karsusinitiative.com/api/health

# Test backend API
curl https://api.karsusinitiative.com/docs
```

## GitHub Actions Workflow Changes

The updated `.github/workflows/azure-deploy.yml` will:

1. **Test Stage**: Run all tests (same as before)
2. **Build Stage**: Build Docker images for frontend and backend
3. **Push Stage**: Push images to Azure Container Registry
4. **Deploy Stage**: Update Azure Web Apps with new images
5. **Smoke Tests**: Verify deployment health

Key workflow steps:
```yaml
- name: Login to Azure Container Registry
  uses: azure/docker-login@v1
  with:
    login-server: acrdndinitiative.azurecr.io
    username: ${{ secrets.AZURE_REGISTRY_USERNAME }}
    password: ${{ secrets.AZURE_REGISTRY_PASSWORD }}

- name: Build and push images
  run: |
    docker build -t acrdndinitiative.azurecr.io/backend:${{ github.sha }} ./backend
    docker push acrdndinitiative.azurecr.io/backend:${{ github.sha }}

- name: Deploy to Azure Web App
  uses: azure/webapps-deploy@v2
  with:
    app-name: app-dnd-initiative-backend
    images: acrdndinitiative.azurecr.io/backend:${{ github.sha }}
```

## Monitoring & Observability

### Application Insights Dashboard
Access: Azure Portal → Application Insights → `appi-dnd-initiative-prod`

Monitors:
- Request rates and response times
- Failed requests and exceptions
- Dependency calls (database queries)
- Custom metrics (from Prometheus)

### Set Up Alerts
```bash
# Alert on high error rate
az monitor metrics alert create \
  --name high-error-rate \
  --resource-group rg-dnd-initiative-prod \
  --scopes /subscriptions/{sub-id}/resourceGroups/rg-dnd-initiative-prod \
  --condition "avg requests/failed > 10" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action email your-email@example.com
```

## Cost Optimization Tips

1. **Use B1 tier** for App Service (not F1 Free tier - doesn't support custom domains)
2. **Burstable database** tier for PostgreSQL (B1ms) - perfect for small workloads
3. **Stop dev environments** when not in use
4. **Set budget alerts** in Azure Cost Management
5. **Use Azure Calculator** to estimate: https://azure.com/e/pricing

## Rollback Procedure

If something goes wrong:

```bash
# Rollback to previous image
az webapp config container set \
  --name app-dnd-initiative-backend \
  --resource-group rg-dnd-initiative-prod \
  --docker-custom-image-name acrdndinitiative.azurecr.io/backend:previous-sha

# Or use Azure Portal: Deployment Center → Deployment History → Redeploy
```

## Comparison: Cloudflare Tunnel vs Azure

| Feature | Cloudflare Tunnel | Azure App Service |
|---------|------------------|-------------------|
| Cost | Free | ~$35/month |
| Availability | Depends on local machine | 99.95% SLA |
| Scaling | No | Auto-scaling available |
| SSL | Free | Free |
| Monitoring | Limited | Comprehensive |
| Backups | Manual | Automated |
| Professional | Hobby setup | Production-ready |

## Troubleshooting

### Issue: Database connection fails
**Solution**: Check firewall rules
```bash
az postgres flexible-server firewall-rule create \
  --resource-group rg-dnd-initiative-prod \
  --name psql-dnd-initiative-prod \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

### Issue: Container won't start
**Solution**: Check logs
```bash
az webapp log tail \
  --name app-dnd-initiative-backend \
  --resource-group rg-dnd-initiative-prod
```

### Issue: Custom domain not working
**Solution**: Verify DNS propagation
```bash
nslookup karsusinitiative.com
```
Wait up to 48 hours for DNS propagation.

## Next Steps After Migration

1. ✅ **Delete local infrastructure** (Docker containers, Cloudflare tunnel)
2. ✅ **Update README.md** with new Azure deployment info
3. ✅ **Set up automated backups** (Azure handles this)
4. ✅ **Configure monitoring alerts**
5. ✅ **Test disaster recovery** procedure
6. ✅ **Document runbooks** for common operations

## Support & Resources

- **Azure Documentation**: https://docs.microsoft.com/azure
- **Azure Pricing Calculator**: https://azure.com/e/pricing
- **Azure Support**: Azure Portal → Help + Support
- **Community**: Microsoft Q&A, Stack Overflow

## Appendix: Quick Command Reference

```bash
# View all resources
az resource list --resource-group rg-dnd-initiative-prod -o table

# Restart web apps
az webapp restart --name app-dnd-initiative-backend --resource-group rg-dnd-initiative-prod

# View logs
az webapp log tail --name app-dnd-initiative-backend --resource-group rg-dnd-initiative-prod

# Scale up
az appservice plan update --name asp-dnd-initiative-prod --resource-group rg-dnd-initiative-prod --sku B2

# Delete everything (careful!)
az group delete --name rg-dnd-initiative-prod --yes --no-wait
```

---

**Ready to migrate?** Start with Phase 1 and work through each phase sequentially. The entire migration should take ~2 hours.
