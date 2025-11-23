# Azure Migration - Quick Reference

## 🚀 5-Minute Quick Start

```powershell
# 1. Run deployment script
cd azure-infrastructure
.\deploy.ps1

# 2. Create service principal and copy JSON output
az ad sp create-for-rbac --name "github-actions-dnd" --role contributor --scopes /subscriptions/{subscription-id}/resourceGroups/rg-dnd-initiative-prod --sdk-auth

# 3. Add GitHub secrets (from deployment script output)
# Go to: GitHub repo → Settings → Secrets → Actions
# Add: AZURE_CREDENTIALS, AZURE_REGISTRY_NAME, AZURE_REGISTRY_USERNAME, AZURE_REGISTRY_PASSWORD, DATABASE_URL, SECRET_KEY

# 4. Push to GitHub
git add .
git commit -m "feat: add Azure infrastructure"
git push origin main

# 5. Watch deployment
# Go to: GitHub repo → Actions tab
```

## 📋 Resources Created

```
Resource Group: rg-dnd-initiative-prod
├── Container Registry (acrdndinitiativeprod)
├── App Service Plan (asp-dnd-initiative-prod) - B1 Linux
├── Frontend Web App (app-dnd-initiative-frontend-prod)
├── Backend Web App (app-dnd-initiative-backend-prod)
├── PostgreSQL Server (psql-dnd-initiative-prod) - B1ms
├── Application Insights (appi-dnd-initiative-prod)
└── Log Analytics Workspace (log-dnd-initiative-prod)

Cost: ~$35-40/month
```

## 🔑 GitHub Secrets Required

| Secret | Where to Get It | Example |
|--------|----------------|---------|
| `AZURE_CREDENTIALS` | Service principal creation | JSON object |
| `AZURE_REGISTRY_NAME` | ACR name | `acrdndinitiativeprod` |
| `AZURE_REGISTRY_USERNAME` | ACR → Access keys | `acrdndinitiativeprod` |
| `AZURE_REGISTRY_PASSWORD` | ACR → Access keys | `xxx...` |
| `DATABASE_URL` | Deployment script output | `postgresql://...` |
| `SECRET_KEY` | Deployment script output | `xxx...` |

## 🌐 Custom Domain Setup

### 1. Update DNS (Cloudflare)
```
Type  | Name | Target
------|------|-------
CNAME | @    | app-dnd-initiative-frontend-prod.azurewebsites.net
CNAME | api  | app-dnd-initiative-backend-prod.azurewebsites.net
```

### 2. Add Custom Domain
```bash
# Frontend
az webapp config hostname add \
  --webapp-name app-dnd-initiative-frontend-prod \
  --resource-group rg-dnd-initiative-prod \
  --hostname karsusinitiative.com

# Backend
az webapp config hostname add \
  --webapp-name app-dnd-initiative-backend-prod \
  --resource-group rg-dnd-initiative-prod \
  --hostname api.karsusinitiative.com

# Enable HTTPS
az webapp config ssl bind \
  --name app-dnd-initiative-frontend-prod \
  --resource-group rg-dnd-initiative-prod \
  --certificate-thumbprint auto \
  --ssl-type SNI

az webapp config ssl bind \
  --name app-dnd-initiative-backend-prod \
  --resource-group rg-dnd-initiative-prod \
  --certificate-thumbprint auto \
  --ssl-type SNI
```

## 📊 Monitoring Commands

```bash
# View logs
az webapp log tail --name app-dnd-initiative-backend-prod --resource-group rg-dnd-initiative-prod

# Check health
curl https://app-dnd-initiative-backend-prod.azurewebsites.net/api/health

# View metrics
az monitor metrics list --resource /subscriptions/{sub-id}/resourceGroups/rg-dnd-initiative-prod/providers/Microsoft.Web/sites/app-dnd-initiative-backend-prod

# Application Insights
# Azure Portal → appi-dnd-initiative-prod → Logs
```

## 🔄 Database Migration

```bash
# Export from Docker
docker exec -t dnd-db pg_dump -U postgres dnd_tracker > backup.sql

# Import to Azure PostgreSQL
psql "host=psql-dnd-initiative-prod.postgres.database.azure.com port=5432 dbname=dnd_tracker user=dbadmin password=PASSWORD sslmode=require" < backup.sql
```

## 🛠️ Common Operations

### Restart App
```bash
az webapp restart --name app-dnd-initiative-backend-prod --resource-group rg-dnd-initiative-prod
```

### Scale Up
```bash
az appservice plan update --name asp-dnd-initiative-prod --resource-group rg-dnd-initiative-prod --sku B2
```

### View Costs
```bash
az consumption usage list --start-date 2024-01-01
```

### Rollback Deployment
```bash
# Use previous image
az webapp config container set \
  --name app-dnd-initiative-backend-prod \
  --resource-group rg-dnd-initiative-prod \
  --docker-custom-image-name acrdndinitiativeprod.azurecr.io/backend:previous-sha
```

## ❌ Delete Everything
```bash
az group delete --name rg-dnd-initiative-prod --yes --no-wait
```

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| Container won't start | Check logs: `az webapp log tail` |
| DB connection fails | Check firewall rules |
| Custom domain not working | Verify DNS propagation: `nslookup` |
| High costs | Review Azure Cost Management |
| Deployment failed | Check GitHub Actions logs |

## 📚 Documentation

- Full guide: `docs/AZURE_MIGRATION_GUIDE.md`
- Infrastructure: `azure-infrastructure/README.md`
- Bicep templates: `azure-infrastructure/main.bicep`
- CI/CD workflow: `.github/workflows/azure-deploy.yml`

## ⚡ Architecture

```
GitHub → Actions → ACR → Azure Web Apps → PostgreSQL
          ↓
    Application Insights
```

## 🎯 Success Criteria

- ✅ All tests pass in GitHub Actions
- ✅ Images pushed to ACR
- ✅ Apps deployed to Azure
- ✅ Health endpoints return 200
- ✅ Frontend accessible via custom domain
- ✅ Backend API working
- ✅ Database connected
- ✅ Monitoring active

## 💰 Cost Optimization

1. Use B1 tier (not F1 - no custom domain support)
2. Burstable database (B1ms) for low traffic
3. Stop dev environments when not using
4. Set budget alerts
5. Review costs monthly

---

**Need Help?** See full guide: `docs/AZURE_MIGRATION_GUIDE.md`
