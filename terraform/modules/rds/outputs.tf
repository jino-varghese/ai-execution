output "db_instance_id" {
  description = "ID of the DB instance"
  value       = aws_db_instance.main.id
}

output "db_endpoint" {
  description = "Connection endpoint"
  value       = aws_db_instance.main.endpoint
}

output "db_name" {
  description = "Database name"
  value       = aws_db_instance.main.db_name
}

output "db_port" {
  description = "Database port"
  value       = aws_db_instance.main.port
}

output "db_arn" {
  description = "ARN of the DB instance"
  value       = aws_db_instance.main.arn
}
