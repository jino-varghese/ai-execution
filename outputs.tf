# ============================================================================
# LAMBDA OUTPUTS
# ============================================================================

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.medical_diagnosis.function_name
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.medical_diagnosis.arn
}

output "lambda_function_url" {
  description = "Public URL to access the Medical Diagnosis application"
  value       = aws_lambda_function_url.medical_diagnosis_url.function_url
}

output "lambda_invoke_arn" {
  description = "Invoke ARN of the Lambda function"
  value       = aws_lambda_function.medical_diagnosis.invoke_arn
}

# ============================================================================
# IAM OUTPUTS
# ============================================================================

output "lambda_role_name" {
  description = "Name of the Lambda execution role"
  value       = aws_iam_role.lambda_execution_role.name
}

output "lambda_role_arn" {
  description = "ARN of the Lambda execution role"
  value       = aws_iam_role.lambda_execution_role.arn
}

# ============================================================================
# CLOUDWATCH OUTPUTS
# ============================================================================

output "cloudwatch_log_group" {
  description = "Name of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.lambda_logs.name
}

output "cloudwatch_log_group_arn" {
  description = "ARN of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.lambda_logs.arn
}

# ============================================================================
# DEPLOYMENT INFO
# ============================================================================

output "deployment_region" {
  description = "AWS region where resources are deployed"
  value       = data.aws_region.current.name
}

output "aws_account_id" {
  description = "AWS Account ID"
  value       = data.aws_caller_identity.current.account_id
}

output "environment" {
  description = "Environment name"
  value       = var.environment
}

# ============================================================================
# ACCESS INSTRUCTIONS
# ============================================================================

output "access_instructions" {
  description = "Instructions to access the application"
  value       = <<-EOT

    ============================================================
    🏥 AI Medical Diagnosis System - Deployment Complete!
    ============================================================

    📍 Application URL:
    ${aws_lambda_function_url.medical_diagnosis_url.function_url}

    📊 CloudWatch Logs:
    https://console.aws.amazon.com/cloudwatch/home?region=${data.aws_region.current.name}#logsV2:log-groups/log-group/$252Faws$252Flambda$252F${aws_lambda_function.medical_diagnosis.function_name}

    🔧 Lambda Function:
    https://console.aws.amazon.com/lambda/home?region=${data.aws_region.current.name}#/functions/${aws_lambda_function.medical_diagnosis.function_name}

    💰 Estimated Monthly Cost: $0.00 - $1.00 (within AWS Free Tier)

    ⚠️  IMPORTANT: This is an educational demo only.
        NOT for actual medical use.

    ============================================================
  EOT
}
