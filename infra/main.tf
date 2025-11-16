terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket = "codeguard-terraform-state"
    key    = "terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC Module
module "vpc" {
  source = "./modules/vpc"

  vpc_cidr             = var.vpc_cidr
  availability_zones   = var.availability_zones
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs  = var.private_subnet_cidrs
  enable_nat_gateway   = true
  enable_vpn_gateway   = false
  name_prefix          = var.name_prefix
}

# RDS Module
module "rds" {
  source = "./modules/rds"

  name_prefix          = var.name_prefix
  vpc_id               = module.vpc.vpc_id
  private_subnet_ids   = module.vpc.private_subnet_ids
  db_instance_class    = var.db_instance_class
  db_allocated_storage  = var.db_allocated_storage
  db_name              = var.db_name
  db_username          = var.db_username
  db_password          = var.db_password
}

# ALB
module "alb" {
  source = "./modules/alb"

  name_prefix       = var.name_prefix
  vpc_id            = module.vpc.vpc_id
  public_subnet_ids = module.vpc.public_subnet_ids
  certificate_arn   = var.certificate_arn
}

# ECS Cluster
module "ecs" {
  source = "./modules/ecs"

  name_prefix          = var.name_prefix
  vpc_id               = module.vpc.vpc_id
  public_subnet_ids    = module.vpc.public_subnet_ids
  private_subnet_ids   = module.vpc.private_subnet_ids
  database_url         = module.rds.database_url
  qdrant_host          = module.qdrant.qdrant_host
  qdrant_port          = module.qdrant.qdrant_port
  secret_key           = var.secret_key
  openai_api_key       = var.openai_api_key
  github_pat            = var.github_pat
  ecr_repository_url    = module.ecr.repository_url
  target_group_arn      = module.alb.target_group_arn
}

# ECR
module "ecr" {
  source = "./modules/ecr"

  name_prefix = var.name_prefix
}

# Qdrant on EC2
module "qdrant" {
  source = "./modules/qdrant"

  name_prefix        = var.name_prefix
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  instance_type      = var.qdrant_instance_type
}

# S3
module "s3" {
  source = "./modules/s3"

  name_prefix = var.name_prefix
}

# Outputs
output "alb_dns_name" {
  value       = module.alb.dns_name
  description = "ALB DNS name"
}

output "ecr_repo_url" {
  value       = module.ecr.repository_url
  description = "ECR repository URL"
}

output "rds_endpoint" {
  value       = module.rds.endpoint
  description = "RDS endpoint"
  sensitive   = true
}

