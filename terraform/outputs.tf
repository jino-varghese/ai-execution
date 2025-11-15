# Outputs for AI-Powered Travel Itinerary Generator

output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = module.alb.alb_dns_name
}

output "alb_url" {
  description = "URL of the Application Load Balancer"
  value       = "http://${module.alb.alb_dns_name}"
}

output "rds_endpoint" {
  description = "RDS database endpoint"
  value       = module.rds.db_endpoint
  sensitive   = true
}

output "redis_endpoint" {
  description = "Redis cache endpoint"
  value       = module.elasticache.redis_endpoint
  sensitive   = true
}

output "opensearch_endpoint" {
  description = "OpenSearch domain endpoint"
  value       = module.opensearch.opensearch_endpoint
  sensitive   = true
}

output "opensearch_dashboard_endpoint" {
  description = "OpenSearch Dashboards endpoint"
  value       = module.opensearch.opensearch_dashboard_endpoint
}

output "s3_data_bucket" {
  description = "S3 bucket for travel data"
  value       = module.s3.data_bucket_name
}

output "s3_models_bucket" {
  description = "S3 bucket for ML models"
  value       = module.s3.models_bucket_name
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = module.ecs.cluster_name
}

output "ecs_service_name" {
  description = "Name of the ECS service"
  value       = module.ecs.service_name
}

output "cloudwatch_log_group" {
  description = "CloudWatch log group name"
  value       = aws_cloudwatch_log_group.app_logs.name
}

output "sagemaker_endpoint_name" {
  description = "SageMaker endpoint name (if enabled)"
  value       = var.enable_sagemaker ? module.sagemaker[0].endpoint_name : null
}

output "aws_region" {
  description = "AWS region"
  value       = var.aws_region
}

output "environment" {
  description = "Environment name"
  value       = var.environment
}
