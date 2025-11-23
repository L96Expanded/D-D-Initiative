// PostgreSQL Flexible Server Module
@description('Name of the PostgreSQL server')
param serverName string

@description('Name of the database')
param databaseName string

@description('Location for the resource')
param location string

@description('Resource tags')
param tags object

@description('Administrator password')
@secure()
param administratorPassword string

@description('Database SKU')
param sku string = 'Standard_B1ms'

@description('Administrator username')
param administratorLogin string = 'dbadmin'

resource postgresServer 'Microsoft.DBforPostgreSQL/flexibleServers@2023-03-01-preview' = {
  name: serverName
  location: location
  tags: tags
  sku: {
    name: sku
    tier: startsWith(sku, 'Standard_B') ? 'Burstable' : 'GeneralPurpose'
  }
  properties: {
    administratorLogin: administratorLogin
    administratorLoginPassword: administratorPassword
    version: '15'
    storage: {
      storageSizeGB: 32
    }
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
    highAvailability: {
      mode: 'Disabled'
    }
  }
}

resource firewallRule 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2023-03-01-preview' = {
  parent: postgresServer
  name: 'AllowAzureServices'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

resource database 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2023-03-01-preview' = {
  parent: postgresServer
  name: databaseName
  properties: {
    charset: 'UTF8'
    collation: 'en_US.utf8'
  }
}

output id string = postgresServer.id
output fqdn string = postgresServer.properties.fullyQualifiedDomainName
output name string = postgresServer.name
