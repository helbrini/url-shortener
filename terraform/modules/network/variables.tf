variable "name_suffix" {
  description = "Suffixe de nommage, par exemple projet-environnement"
  type        = string
}

variable "location" {
  description = "Région Azure"
  type        = string
}

variable "resource_group_name" {
  description = "Groupe de ressources qui contient le réseau"
  type        = string
}

variable "address_space" {
  description = "Plage d'adresses du réseau virtuel"
  type        = list(string)
  default     = ["10.0.0.0/16"]
}

variable "app_subnet_prefix" {
  description = "Plage d'adresses du sous-réseau applicatif"
  type        = string
  default     = "10.0.1.0/24"
}

variable "tags" {
  description = "Étiquettes appliquées aux ressources"
  type        = map(string)
  default     = {}
}