// ============================================================================
// Azure Infrastructure for D&D Initiative Tracker
// ============================================================================
// This Bicep template creates all Azure resources needed for the application
// Usage: az deployment sub create --location eastus --template-file main.bicep
// ============================================================================

targetScope = 'subscription'

@description('Environment name (dev, staging, prod)')
@allowed(['dev', 'staging', 'prod'])
param environment string = 'prod'

@description('Azure region for resources')
param location string = 'eastus'

@description('Database administrator password')
@secure()
param dbAdminPassword string

@description('JWT secret key for FastAPI')
@secure()
param secretKey string

// ============================================================================
// Variables
// ============================================================================

var projectName = 'dnd-initiative'
var resourceGroupName = 'rg-${projectName}-${environment}'
var containerRegistryName = 'acr${projectName}${environment}'
var appServicePlanName = 'asp-${projectName}-${environment}'
var frontendAppName = 'app-${projectName}-frontend-${environment}'
var backendAppName = 'app-${projectName}-backend-${environment}'
var databaseServerName = 'psql-${projectName}-${environment}'
var databaseName = 'dnd_tracker'
var appInsightsName = 'appi-${projectName}-${environment}'
var logAnalyticsName = 'log-${projectName}-${environment}'

// Tags for resource organization and cost tracking
var tags = {
  Project: 'D&D Initiative Tracker'
  Environment: environment
  ManagedBy: 'Bicep'
  CostCenter: 'DevOps-Assignment'
}

// ============================================================================
// Resource Group
// ============================================================================

resource resourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: resourceGroupName
  location: location
  tags: tags
}

// ============================================================================
// Module Deployments
// ============================================================================

module containerRegistry 'modules/container-registry.bicep' = {
  name: 'containerRegistry'
  scope: resourceGroup
  params: {
    name: containerRegistryName
    location: location
    tags: tags
    sku: environment == 'prod' ? 'Standard' : 'Basic'
  }
}

module appServicePlan 'modules/app-service-plan.bicep' = {
  name: 'appServicePlan'
  scope: resourceGroup
  params: {
    name: appServicePlanName
    location: location
    tags: tags
    sku: environment == 'prod' ? 'B2' : 'B1'
  }
}

module database 'modules/postgresql.bicep' = {
  name: 'database'
  scope: resourceGroup
  params: {
    serverName: databaseServerName
    databaseName: databaseName
    location: location
    tags: tags
    administratorPassword: dbAdminPassword
    sku: environment == 'prod' ? 'Standard_B2s' : 'Standard_B1ms'
  }
}

module monitoring 'modules/monitoring.bicep' = {
  name: 'monitoring'
  scope: resourceGroup
  params: {
    appInsightsName: appInsightsName
    logAnalyticsName: logAnalyticsName
    location: location
    tags: tags
  }
}

module frontendApp 'modules/web-app.bicep' = {
  name: 'frontendApp'
  scope: resourceGroup
  params: {
    name: frontendAppName
    location: location
    tags: tags
    appServicePlanId: appServicePlan.outputs.id
    containerRegistryName: containerRegistryName
    containerImageName: 'frontend'
    containerImageTag: 'latest'
    appInsightsKey: monitoring.outputs.instrumentationKey
    appSettings: [
      {
        name: 'WEBSITES_ENABLE_APP_SERVICE_STORAGE'
        value: 'false'
      }
      {
        name: 'DOCKER_ENABLE_CI'
        value: 'true'
      }
    ]
  }
  dependsOn: [
    containerRegistry
  ]
}

module backendApp 'modules/web-app.bicep' = {
  name: 'backendApp'
  scope: resourceGroup
  params: {
    name: backendAppName
    location: location
    tags: tags
    appServicePlanId: appServicePlan.outputs.id
    containerRegistryName: containerRegistryName
    containerImageName: 'backend'
    containerImageTag: 'latest'
    appInsightsKey: monitoring.outputs.instrumentationKey
    appSettings: [
      {
        name: 'WEBSITES_ENABLE_APP_SERVICE_STORAGE'
        value: 'false'
      }
      {
        name: 'DOCKER_ENABLE_CI'
        value: 'true'
      }
      {
        name: 'DATABASE_URL'
        value: 'postgresql://dbadmin:${dbAdminPassword}@${databaseServerName}.postgres.database.azure.com/${databaseName}?sslmode=require'
      }
      {
        name: 'SECRET_KEY'
        value: secretKey
      }
      {
        name: 'ENVIRONMENT'
        value: environment
      }
      {
        name: 'CORS_ORIGINS'
        value: environment == 'prod' ? 'https://karsusinitiative.com,https://app-${projectName}-frontend-${environment}.azurewebsites.net' : '*'
      }
    ]
  }
  dependsOn: [
    containerRegistry
    database
  ]
}

// ============================================================================
// Outputs
// ============================================================================

output resourceGroupName string = resourceGroup.name
output containerRegistryLoginServer string = containerRegistry.outputs.loginServer
output frontendAppUrl string = frontendApp.outputs.defaultHostName
output backendAppUrl string = backendApp.outputs.defaultHostName
output databaseHost string = database.outputs.fqdn
output appInsightsInstrumentationKey string = monitoring.outputs.instrumentationKey
output appInsightsConnectionString string = monitoring.outputs.connectionString
