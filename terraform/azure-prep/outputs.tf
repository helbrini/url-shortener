output "resource_group_name" {
  description = "Nom du groupe de ressources"
  value       = azurerm_resource_group.main.name
}

output "subnet_id" {
  description = "Identifiant du sous-réseau applicatif"
  value       = azurerm_subnet.app.id
}
