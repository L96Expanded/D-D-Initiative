// Web App Module (for container-based deployment)
@description('Name of the Web App')
param name string

@description('Location for the resource')
param location string

@description('Resource tags')
param tags object

@description('App Service Plan ID')
param appServicePlanId string

@description('Container Registry name')
param containerRegistryName string

@description('Container image name')
param containerImageName string

@description('Container image tag')
param containerImageTag string

@description('Application Insights instrumentation key')
param appInsightsKey string

@description('Additional app settings')
param appSettings array = []

resource webApp 'Microsoft.Web/sites@2022-09-01' = {
  name: name
  location: location
  tags: tags
  kind: 'app,linux,container'
  properties: {
    serverFarmId: appServicePlanId
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'DOCKER|${containerRegistryName}.azurecr.io/${containerImageName}:${containerImageTag}'
      alwaysOn: true
      http20Enabled: true
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
      appSettings: concat([
        {
          name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
          value: appInsightsKey
        }
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: 'InstrumentationKey=${appInsightsKey}'
        }
        {
          name: 'ApplicationInsightsAgent_EXTENSION_VERSION'
          value: '~3'
        }
      ], appSettings)
    }
  }
}

// Enable container continuous deployment webhook
resource containerSettings 'Microsoft.Web/sites/config@2022-09-01' = {
  parent: webApp
  name: 'web'
  properties: {
    acrUseManagedIdentityCreds: false
  }
}

output id string = webApp.id
output name string = webApp.name
output defaultHostName string = webApp.properties.defaultHostName
