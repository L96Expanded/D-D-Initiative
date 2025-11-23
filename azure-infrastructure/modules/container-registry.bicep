// Container Registry Module
@description('Name of the Container Registry')
param name string

@description('Location for the resource')
param location string

@description('Resource tags')
param tags object

@description('SKU for Container Registry')
@allowed(['Basic', 'Standard', 'Premium'])
param sku string = 'Basic'

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' = {
  name: name
  location: location
  tags: tags
  sku: {
    name: sku
  }
  properties: {
    adminUserEnabled: true
    publicNetworkAccess: 'Enabled'
  }
}

output id string = containerRegistry.id
output loginServer string = containerRegistry.properties.loginServer
output name string = containerRegistry.name
