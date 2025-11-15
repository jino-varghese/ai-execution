output "function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.data_processor.function_name
}

output "function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.data_processor.arn
}

output "function_invoke_arn" {
  description = "Invoke ARN of the Lambda function"
  value       = aws_lambda_function.data_processor.invoke_arn
}
