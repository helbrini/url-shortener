output "vnet_id" {
  description = "Identifiant du réseau virtuel"
  value       = azurerm_virtual_network.main.id
}

output "subnet_id" {
  description = "Identifiant du sous-réseau applicatif"
  value       = azurerm_subnet.app.id
}