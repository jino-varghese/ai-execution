output "alb_sg_id" {
  description = "ID of the ALB security group"
  value       = aws_security_group.alb.id
}

output "ecs_sg_id" {
  description = "ID of the ECS security group"
  value       = aws_security_group.ecs.id
}

output "database_sg_id" {
  description = "ID of the database security group"
  value       = aws_security_group.database.id
}

output "cache_sg_id" {
  description = "ID of the cache security group"
  value       = aws_security_group.cache.id
}

output "opensearch_sg_id" {
  description = "ID of the OpenSearch security group"
  value       = aws_security_group.opensearch.id
}

output "lambda_sg_id" {
  description = "ID of the Lambda security group"
  value       = aws_security_group.lambda.id
}

output "sagemaker_sg_id" {
  description = "ID of the SageMaker security group"
  value       = aws_security_group.sagemaker.id
}
