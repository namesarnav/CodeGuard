variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "public_subnet_ids" {
  description = "Public subnet IDs"
  type        = list(string)
}

variable "private_subnet_ids" {
  description = "Private subnet IDs"
  type        = list(string)
}

variable "database_url" {
  description = "Database connection URL"
  type        = string
  sensitive   = true
}

variable "qdrant_host" {
  description = "Qdrant host"
  type        = string
}

variable "qdrant_port" {
  description = "Qdrant port"
  type        = number
}

variable "secret_key" {
  description = "Application secret key"
  type        = string
  sensitive   = true
}

variable "openai_api_key" {
  description = "OpenAI API key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "github_pat" {
  description = "GitHub PAT"
  type        = string
  sensitive   = true
  default     = ""
}

variable "ecr_repository_url" {
  description = "ECR repository URL"
  type        = string
}

variable "target_group_arn" {
  description = "ALB target group ARN"
  type        = string
}

