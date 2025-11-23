// App Service Plan Module
@description('Name of the App Service Plan')
param name string

@description('Location for the resource')
param location string

@description('Resource tags')
param tags object

@description('SKU for App Service Plan')
@allowed(['B1', 'B2', 'B3', 'S1', 'S2', 'S3', 'P1v2', 'P2v2', 'P3v2'])
param sku string = 'B1'

resource appServicePlan 'Microsoft.Web/serverfarms@2022-09-01' = {
  name: name
  location: location
  tags: tags
  kind: 'linux'
  sku: {
    name: sku
  }
  properties: {
    reserved: true // Required for Linux
  }
}

output id string = appServicePlan.id
output name string = appServicePlan.name
