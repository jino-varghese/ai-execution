output "data_bucket_name" {
  description = "Name of the data bucket"
  value       = aws_s3_bucket.data.id
}

output "data_bucket_arn" {
  description = "ARN of the data bucket"
  value       = aws_s3_bucket.data.arn
}

output "models_bucket_name" {
  description = "Name of the models bucket"
  value       = aws_s3_bucket.models.id
}

output "models_bucket_arn" {
  description = "ARN of the models bucket"
  value       = aws_s3_bucket.models.arn
}

output "logs_bucket_name" {
  description = "Name of the logs bucket"
  value       = aws_s3_bucket.logs.id
}

output "logs_bucket_arn" {
  description = "ARN of the logs bucket"
  value       = aws_s3_bucket.logs.arn
}
