variable "project" {
  description = "Nom du projet, utilisé dans le nom des ressources"
  type        = string
  default     = "urlshortener"
}

variable "environment" {
  description = "Environnement (dev, test, prod)"
  type        = string
  default     = "dev"
}

variable "location" {
  description = "Région Azure"
  type        = string
  default     = "francecentral"
}
