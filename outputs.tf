output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.gen_ai_dashboard.function_name
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.gen_ai_dashboard.arn
}

output "lambda_role_arn" {
  description = "ARN of the Lambda IAM role"
  value       = aws_iam_role.lambda_role.arn
}

output "function_url" {
  description = "Lambda Function URL - Open this in your browser"
  value       = aws_lambda_function_url.gen_ai_dashboard_url.function_url
}

output "cloudwatch_log_group" {
  description = "CloudWatch Log Group name"
  value       = aws_cloudwatch_log_group.lambda_logs.name
}

output "deployment_region" {
  description = "AWS region where resources are deployed"
  value       = var.aws_region
}
