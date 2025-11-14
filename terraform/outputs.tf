# Lambda Function Outputs
output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.legal_analyzer.function_name
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.legal_analyzer.arn
}

output "lambda_function_version" {
  description = "Latest version of the Lambda function"
  value       = aws_lambda_function.legal_analyzer.version
}

output "lambda_role_arn" {
  description = "ARN of the Lambda execution role"
  value       = aws_iam_role.lambda_role.arn
}

output "lambda_role_name" {
  description = "Name of the Lambda execution role"
  value       = aws_iam_role.lambda_role.name
}

# Function URL Outputs
output "function_url" {
  description = "URL endpoint for the Lambda function"
  value       = aws_lambda_function_url.legal_analyzer_url.function_url
}

output "function_url_id" {
  description = "ID of the Lambda Function URL"
  value       = aws_lambda_function_url.legal_analyzer_url.url_id
}

# CloudWatch Outputs
output "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.lambda_logs.name
}

output "cloudwatch_log_group_arn" {
  description = "ARN of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.lambda_logs.arn
}

# Deployment Information
output "deployment_info" {
  description = "Deployment information"
  value = {
    region              = data.aws_region.current.name
    account_id          = data.aws_caller_identity.current.account_id
    runtime             = var.lambda_runtime
    memory_size         = var.lambda_memory_size
    timeout             = var.lambda_timeout
    environment         = var.environment
    function_url_auth   = var.function_url_auth_type
  }
}

# Quick Start Guide
output "quick_start" {
  description = "Quick start instructions"
  value = <<-EOT
    ==========================================
    Legal Document Analysis Agent Deployed!
    ==========================================

    Access URL:
    ${aws_lambda_function_url.legal_analyzer_url.function_url}

    Function Name: ${aws_lambda_function.legal_analyzer.function_name}
    Region: ${data.aws_region.current.name}

    Next Steps:
    1. Open the URL above in your browser
    2. Try the sample contracts (NDA, Service Agreement, Employment)
    3. Paste your own legal documents for analysis

    Important: Ensure AWS Bedrock access is enabled
    - AWS Console → Bedrock → Model access
    - Enable: Anthropic Claude 3 Sonnet

    Monitor Logs:
    aws logs tail ${aws_cloudwatch_log_group.lambda_logs.name} --follow --region ${data.aws_region.current.name}

    View Function:
    aws lambda get-function --function-name ${aws_lambda_function.legal_analyzer.function_name} --region ${data.aws_region.current.name}
  EOT
}
