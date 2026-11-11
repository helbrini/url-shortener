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

variable "image_tag" {
  description = "Tag de l'image de l'API (hash de commit publié dans GHCR)"
  type        = string
  default     = "latest"
}

variable "database_url" {
  description = "Chaîne de connexion à la base Postgres"
  type        = string
  sensitive   = true
}
