# Variables for AI-Powered Travel Itinerary Generator Terraform Configuration

variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "travel-ai"
}

# VPC Configuration
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

# Database Configuration
variable "db_username" {
  description = "Database master username"
  type        = string
  default     = "traveladmin"
  sensitive   = true
}

variable "db_password" {
  description = "Database master password"
  type        = string
  sensitive   = true
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "traveldb"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.medium"
}

variable "db_allocated_storage" {
  description = "Allocated storage for RDS in GB"
  type        = number
  default     = 100
}

# Redis Configuration
variable "redis_node_type" {
  description = "ElastiCache Redis node type"
  type        = string
  default     = "cache.t3.medium"
}

variable "redis_num_nodes" {
  description = "Number of cache nodes"
  type        = number
  default     = 1
}

# OpenSearch Configuration
variable "opensearch_instance_type" {
  description = "OpenSearch instance type"
  type        = string
  default     = "t3.medium.search"
}

variable "opensearch_instance_count" {
  description = "Number of OpenSearch instances"
  type        = number
  default     = 2
}

variable "opensearch_ebs_volume_size" {
  description = "EBS volume size for OpenSearch in GB"
  type        = number
  default     = 100
}

# ECS Configuration
variable "container_image" {
  description = "Docker container image for the application"
  type        = string
  default     = "nginx:latest" # Replace with your actual image
}

variable "container_port" {
  description = "Container port"
  type        = number
  default     = 8000
}

variable "ecs_desired_count" {
  description = "Desired number of ECS tasks"
  type        = number
  default     = 2
}

variable "ecs_task_cpu" {
  description = "ECS task CPU units"
  type        = string
  default     = "1024"
}

variable "ecs_task_memory" {
  description = "ECS task memory in MB"
  type        = string
  default     = "2048"
}

# SageMaker Configuration
variable "enable_sagemaker" {
  description = "Enable SageMaker endpoint for ML models"
  type        = bool
  default     = false
}

variable "sagemaker_instance_type" {
  description = "SageMaker instance type"
  type        = string
  default     = "ml.m5.xlarge"
}

variable "sagemaker_model_data_url" {
  description = "S3 URL for SageMaker model artifacts"
  type        = string
  default     = ""
}

# Lambda Configuration
variable "enable_lambda_processing" {
  description = "Enable Lambda functions for data processing"
  type        = bool
  default     = true
}

# Secrets
variable "openai_api_key" {
  description = "OpenAI API key for LLM access"
  type        = string
  sensitive   = true
  default     = ""
}

# CloudWatch Configuration
variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 30
}
