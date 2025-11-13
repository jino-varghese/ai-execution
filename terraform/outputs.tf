# ============================================================================
# AI Medical Diagnosis System - Terraform Outputs
# ============================================================================
# This file defines the outputs that will be displayed after deployment.
# These values are useful for accessing and monitoring the deployed resources.
#
# View outputs after deployment:
#   terraform output
#   terraform output function_url  (get specific output)
#   terraform output -json          (get all outputs as JSON)
# ============================================================================

# ============================================================================
# LAMBDA FUNCTION OUTPUTS
# ============================================================================

# Lambda function name
output "function_name" {
  description = "Name of the deployed Lambda function"
  value       = aws_lambda_function.medical_diagnosis.function_name
}

# Lambda function ARN (Amazon Resource Name)
output "function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.medical_diagnosis.arn
}

# Lambda function version
output "function_version" {
  description = "Latest version of the Lambda function"
  value       = aws_lambda_function.medical_diagnosis.version
}

# Lambda function last modified date
output "function_last_modified" {
  description = "Last modified date of the Lambda function"
  value       = aws_lambda_function.medical_diagnosis.last_modified
}

# Lambda function memory size
output "function_memory_size" {
  description = "Memory size allocated to the Lambda function (MB)"
  value       = aws_lambda_function.medical_diagnosis.memory_size
}

# Lambda function timeout
output "function_timeout" {
  description = "Timeout configured for the Lambda function (seconds)"
  value       = aws_lambda_function.medical_diagnosis.timeout
}

# Lambda function runtime
output "function_runtime" {
  description = "Runtime environment of the Lambda function"
  value       = aws_lambda_function.medical_diagnosis.runtime
}

# ============================================================================
# FUNCTION URL OUTPUTS (Most Important!)
# ============================================================================

# Public Function URL - This is your application URL!
output "function_url" {
  description = "Public HTTPS URL to access the medical diagnosis application"
  value       = aws_lambda_function_url.medical_diagnosis_url.function_url
}

# Function URL ID
output "function_url_id" {
  description = "ID of the Lambda Function URL"
  value       = aws_lambda_function_url.medical_diagnosis_url.url_id
}

# ============================================================================
# IAM ROLE OUTPUTS
# ============================================================================

# IAM role name
output "lambda_role_name" {
  description = "Name of the IAM role used by Lambda"
  value       = aws_iam_role.lambda_execution_role.name
}

# IAM role ARN
output "lambda_role_arn" {
  description = "ARN of the IAM role used by Lambda"
  value       = aws_iam_role.lambda_execution_role.arn
}

# ============================================================================
# CLOUDWATCH LOGS OUTPUTS
# ============================================================================

# CloudWatch Log Group name
output "log_group_name" {
  description = "Name of the CloudWatch Log Group"
  value       = aws_cloudwatch_log_group.lambda_log_group.name
}

# CloudWatch Log Group ARN
output "log_group_arn" {
  description = "ARN of the CloudWatch Log Group"
  value       = aws_cloudwatch_log_group.lambda_log_group.arn
}

# Log retention period
output "log_retention_days" {
  description = "Log retention period in days"
  value       = aws_cloudwatch_log_group.lambda_log_group.retention_in_days
}

# ============================================================================
# AWS ACCOUNT INFORMATION
# ============================================================================

# AWS Account ID
output "aws_account_id" {
  description = "AWS Account ID where resources are deployed"
  value       = data.aws_caller_identity.current.account_id
}

# AWS Region
output "aws_region" {
  description = "AWS Region where resources are deployed"
  value       = data.aws_region.current.name
}

# ============================================================================
# MONITORING OUTPUTS
# ============================================================================

# CloudWatch Alarms (if enabled)
output "alarm_names" {
  description = "Names of CloudWatch alarms (if enabled)"
  value = var.enable_alarms ? [
    aws_cloudwatch_metric_alarm.lambda_errors[0].alarm_name,
    aws_cloudwatch_metric_alarm.lambda_duration[0].alarm_name,
    aws_cloudwatch_metric_alarm.lambda_throttles[0].alarm_name
  ] : []
}

# ============================================================================
# USEFUL COMMANDS (as outputs)
# ============================================================================

# Command to view logs
output "view_logs_command" {
  description = "AWS CLI command to view Lambda logs"
  value       = "aws logs tail ${aws_cloudwatch_log_group.lambda_log_group.name} --follow --region ${data.aws_region.current.name}"
}

# Command to invoke function
output "invoke_function_command" {
  description = "AWS CLI command to invoke Lambda function"
  value       = "aws lambda invoke --function-name ${aws_lambda_function.medical_diagnosis.function_name} --region ${data.aws_region.current.name} response.json"
}

# Command to update function code
output "update_function_command" {
  description = "AWS CLI command to update function code"
  value       = "aws lambda update-function-code --function-name ${aws_lambda_function.medical_diagnosis.function_name} --zip-file fileb://lambda_function.zip --region ${data.aws_region.current.name}"
}

# ============================================================================
# DEPLOYMENT SUMMARY
# ============================================================================

# Comprehensive deployment summary
output "deployment_summary" {
  description = "Summary of the deployed resources"
  value = {
    application_name = "AI Medical Diagnosis System"
    environment      = var.environment
    function_url     = aws_lambda_function_url.medical_diagnosis_url.function_url
    function_name    = aws_lambda_function.medical_diagnosis.function_name
    region           = data.aws_region.current.name
    account_id       = data.aws_caller_identity.current.account_id
    runtime          = aws_lambda_function.medical_diagnosis.runtime
    memory_mb        = aws_lambda_function.medical_diagnosis.memory_size
    timeout_seconds  = aws_lambda_function.medical_diagnosis.timeout
    log_group        = aws_cloudwatch_log_group.lambda_log_group.name
    alarms_enabled   = var.enable_alarms
  }
}

# ============================================================================
# PRETTY OUTPUT FOR USER
# ============================================================================

# Success message
output "deployment_success_message" {
  description = "Deployment success message with instructions"
  value       = <<-EOT

    ╔════════════════════════════════════════════════════════════════╗
    ║          🎉 DEPLOYMENT SUCCESSFUL! 🎉                         ║
    ╚════════════════════════════════════════════════════════════════╝

    Your AI Medical Diagnosis System is now live!

    📍 Access your application at:
    ${aws_lambda_function_url.medical_diagnosis_url.function_url}

    📊 Function Details:
      • Name:       ${aws_lambda_function.medical_diagnosis.function_name}
      • Region:     ${data.aws_region.current.name}
      • Runtime:    ${aws_lambda_function.medical_diagnosis.runtime}
      • Memory:     ${aws_lambda_function.medical_diagnosis.memory_size} MB
      • Timeout:    ${aws_lambda_function.medical_diagnosis.timeout} seconds

    📝 View Logs:
      aws logs tail ${aws_cloudwatch_log_group.lambda_log_group.name} --follow

    🧹 To Destroy:
      terraform destroy

    ⚠️  IMPORTANT: This is an educational demo. NOT for actual medical use.

  EOT
}
