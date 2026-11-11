output "resource_group_name" {
  description = "Nom du groupe de ressources"
  value       = azurerm_resource_group.main.name
}

output "subnet_id" {
  description = "Identifiant du sous-réseau applicatif"
  value       = azurerm_subnet.app.id
}

output "api_url" {
  description = "Adresse publique de l'API"
  value       = "https://${azurerm_container_app.api.ingress[0].fqdn}"
}
