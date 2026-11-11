terraform {
  required_version = ">= 1.5"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "main" {
  name     = "rg-${var.project}-${var.environment}"
  location = var.location

  tags = {
    project     = var.project
    environment = var.environment
  }
}

resource "azurerm_virtual_network" "main" {
  name                = "vnet-${var.project}-${var.environment}"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  tags = azurerm_resource_group.main.tags
}

resource "azurerm_subnet" "app" {
  name                 = "snet-app"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_log_analytics_workspace" "main" {
  name                = "log-${var.project}-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30

  tags = azurerm_resource_group.main.tags
}

resource "azurerm_container_app_environment" "main" {
  name                       = "cae-${var.project}-${var.environment}"
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  tags = azurerm_resource_group.main.tags
}

resource "azurerm_container_app" "api" {
  name                         = "ca-${var.project}-api"
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = azurerm_resource_group.main.name
  revision_mode                = "Single"

  secret {
    name  = "database-url"
    value = var.database_url
  }

  template {
    min_replicas = 0
    max_replicas = 2

    container {
      name   = "api"
      image  = "ghcr.io/helbrini/url-shortener:${var.image_tag}"
      cpu    = 0.25
      memory = "0.5Gi"

      env {
        name        = "DATABASE_URL"
        secret_name = "database-url"
      }
    }
  }

  ingress {
    external_enabled = true
    target_port      = 8000

    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  tags = azurerm_resource_group.main.tags
}
