# Main Terraform Configuration for AI-Powered Travel Itinerary Generator
# This deploys a complete AWS infrastructure for the travel assistant application

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Uncomment to use S3 backend for state management
  # backend "s3" {
  #   bucket         = "your-terraform-state-bucket"
  #   key            = "travel-ai/terraform.tfstate"
  #   region         = "us-east-1"
  #   encrypt        = true
  #   dynamodb_table = "terraform-state-lock"
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "AI-Travel-Itinerary-Generator"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

# Local variables
locals {
  name_prefix = "${var.project_name}-${var.environment}"

  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }

  azs = slice(data.aws_availability_zones.available.names, 0, 3)
}

# VPC Module
module "vpc" {
  source = "./modules/vpc"

  name_prefix         = local.name_prefix
  vpc_cidr            = var.vpc_cidr
  availability_zones  = local.azs
  tags                = local.common_tags
}

# Security Groups
module "security_groups" {
  source = "./modules/security"

  name_prefix = local.name_prefix
  vpc_id      = module.vpc.vpc_id
  tags        = local.common_tags
}

# S3 Buckets for data storage
module "s3" {
  source = "./modules/s3"

  name_prefix = local.name_prefix
  tags        = local.common_tags
}

# RDS PostgreSQL Database
module "rds" {
  source = "./modules/rds"

  name_prefix           = local.name_prefix
  vpc_id                = module.vpc.vpc_id
  private_subnet_ids    = module.vpc.private_subnet_ids
  database_security_group_id = module.security_groups.database_sg_id
  db_username           = var.db_username
  db_password           = var.db_password
  db_name               = var.db_name
  instance_class        = var.db_instance_class
  allocated_storage     = var.db_allocated_storage
  tags                  = local.common_tags
}

# ElastiCache Redis for caching
module "elasticache" {
  source = "./modules/elasticache"

  name_prefix           = local.name_prefix
  vpc_id                = module.vpc.vpc_id
  private_subnet_ids    = module.vpc.private_subnet_ids
  cache_security_group_id = module.security_groups.cache_sg_id
  node_type             = var.redis_node_type
  num_cache_nodes       = var.redis_num_nodes
  tags                  = local.common_tags
}

# OpenSearch for RAG (Vector Search)
module "opensearch" {
  source = "./modules/opensearch"

  name_prefix           = local.name_prefix
  vpc_id                = module.vpc.vpc_id
  private_subnet_ids    = module.vpc.private_subnet_ids
  opensearch_security_group_id = module.security_groups.opensearch_sg_id
  instance_type         = var.opensearch_instance_type
  instance_count        = var.opensearch_instance_count
  ebs_volume_size       = var.opensearch_ebs_volume_size
  tags                  = local.common_tags
}

# Application Load Balancer
module "alb" {
  source = "./modules/alb"

  name_prefix        = local.name_prefix
  vpc_id             = module.vpc.vpc_id
  public_subnet_ids  = module.vpc.public_subnet_ids
  alb_security_group_id = module.security_groups.alb_sg_id
  tags               = local.common_tags
}

# ECS Cluster and Services
module "ecs" {
  source = "./modules/ecs"

  name_prefix              = local.name_prefix
  vpc_id                   = module.vpc.vpc_id
  private_subnet_ids       = module.vpc.private_subnet_ids
  ecs_security_group_id    = module.security_groups.ecs_sg_id
  alb_target_group_arn     = module.alb.target_group_arn

  # Container configuration
  container_image          = var.container_image
  container_port           = var.container_port
  desired_count            = var.ecs_desired_count
  cpu                      = var.ecs_task_cpu
  memory                   = var.ecs_task_memory

  # Environment variables for the application
  environment_variables = {
    ENVIRONMENT           = var.environment
    DATABASE_HOST         = module.rds.db_endpoint
    DATABASE_NAME         = var.db_name
    DATABASE_USER         = var.db_username
    REDIS_ENDPOINT        = module.elasticache.redis_endpoint
    OPENSEARCH_ENDPOINT   = module.opensearch.opensearch_endpoint
    S3_DATA_BUCKET        = module.s3.data_bucket_name
    S3_MODELS_BUCKET      = module.s3.models_bucket_name
    AWS_REGION            = var.aws_region
  }

  # Secrets from Secrets Manager
  secrets = {
    DATABASE_PASSWORD     = module.secrets.db_password_arn
    OPENAI_API_KEY        = module.secrets.openai_api_key_arn
  }

  tags = local.common_tags
}

# Secrets Manager
module "secrets" {
  source = "./modules/secrets"

  name_prefix    = local.name_prefix
  db_password    = var.db_password
  openai_api_key = var.openai_api_key
  tags           = local.common_tags
}

# SageMaker for ML Model Hosting (Optional)
module "sagemaker" {
  source = "./modules/sagemaker"
  count  = var.enable_sagemaker ? 1 : 0

  name_prefix           = local.name_prefix
  vpc_id                = module.vpc.vpc_id
  private_subnet_ids    = module.vpc.private_subnet_ids
  sagemaker_security_group_id = module.security_groups.sagemaker_sg_id
  instance_type         = var.sagemaker_instance_type
  model_data_url        = var.sagemaker_model_data_url
  tags                  = local.common_tags
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "app_logs" {
  name              = "/aws/ecs/${local.name_prefix}"
  retention_in_days = var.log_retention_days

  tags = local.common_tags
}

# Lambda for data processing (Optional)
module "lambda" {
  source = "./modules/lambda"
  count  = var.enable_lambda_processing ? 1 : 0

  name_prefix           = local.name_prefix
  vpc_id                = module.vpc.vpc_id
  private_subnet_ids    = module.vpc.private_subnet_ids
  lambda_security_group_id = module.security_groups.lambda_sg_id
  data_bucket_name      = module.s3.data_bucket_name
  data_bucket_arn       = module.s3.data_bucket_arn
  tags                  = local.common_tags
}
