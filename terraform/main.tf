# ============================================================================
# AI Medical Diagnosis System - Terraform Main Configuration
# ============================================================================
# This Terraform configuration deploys the complete medical diagnosis system
# to AWS Lambda with a public Function URL.
#
# Resources created:
# - IAM Role for Lambda execution
# - IAM Policy attachments
# - Lambda Function
# - Lambda Function URL (public endpoint)
# - CloudWatch Log Group
#
# Author: AI Medical Diagnosis Team
# Version: 1.0.0
# ============================================================================

# ============================================================================
# DATA SOURCES
# ============================================================================

# Get current AWS account ID and region
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# ============================================================================
# LAMBDA FUNCTION CODE PACKAGING
# ============================================================================

# Archive the Lambda function code into a ZIP file
# This takes the Python file and creates a deployment package
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "../medical_diagnosis_lambda.py"
  output_path = "${path.module}/lambda_function.zip"
}

# ============================================================================
# IAM ROLE FOR LAMBDA EXECUTION
# ============================================================================

# IAM Role that Lambda will assume to execute
# This role defines what permissions the Lambda function has
resource "aws_iam_role" "lambda_execution_role" {
  name        = var.lambda_role_name
  description = "Execution role for AI Medical Diagnosis Lambda function"

  # Trust policy: Allows Lambda service to assume this role
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = merge(
    var.common_tags,
    {
      Name = var.lambda_role_name
    }
  )
}

# Attach AWS managed policy for basic Lambda execution
# This provides permissions to write logs to CloudWatch
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Optional: Custom IAM policy for additional permissions
# Uncomment if you need access to other AWS services (S3, DynamoDB, etc.)
/*
resource "aws_iam_role_policy" "lambda_custom_policy" {
  name = "${var.function_name}-custom-policy"
  role = aws_iam_role.lambda_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = "*"
      }
    ]
  })
}
*/

# ============================================================================
# CLOUDWATCH LOG GROUP
# ============================================================================

# Create CloudWatch Log Group for Lambda function logs
# This allows us to control log retention and monitor the function
resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name              = "/aws/lambda/${var.function_name}"
  retention_in_days = var.log_retention_days

  tags = merge(
    var.common_tags,
    {
      Name = "${var.function_name}-logs"
    }
  )
}

# ============================================================================
# LAMBDA FUNCTION
# ============================================================================

# Main Lambda function resource
# This deploys the medical diagnosis application
resource "aws_lambda_function" "medical_diagnosis" {
  # Basic configuration
  function_name = var.function_name
  description   = "AI-Powered Medical Diagnosis and Treatment Recommendations System"
  role          = aws_iam_role.lambda_execution_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = var.python_runtime

  # Code deployment
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  # Performance configuration
  memory_size = var.memory_size
  timeout     = var.timeout

  # Environment variables (if needed)
  # Uncomment to add API keys or configuration
  /*
  environment {
    variables = {
      ENVIRONMENT = var.environment
      LOG_LEVEL   = var.log_level
      # Add API keys or other configuration here
    }
  }
  */

  # Ensure log group exists before creating function
  depends_on = [
    aws_cloudwatch_log_group.lambda_log_group,
    aws_iam_role_policy_attachment.lambda_basic_execution
  ]

  tags = merge(
    var.common_tags,
    {
      Name = var.function_name
    }
  )
}

# ============================================================================
# LAMBDA FUNCTION URL (PUBLIC ENDPOINT)
# ============================================================================

# Create a public HTTPS endpoint for the Lambda function
# This allows direct browser access without API Gateway
resource "aws_lambda_function_url" "medical_diagnosis_url" {
  function_name      = aws_lambda_function.medical_diagnosis.function_name
  authorization_type = "NONE" # Public access (no authentication required)

  # CORS configuration for browser access
  cors {
    allow_credentials = false
    allow_origins     = ["*"] # Allow all origins (for demo purposes)
    allow_methods     = ["GET", "POST", "OPTIONS"]
    allow_headers     = ["content-type", "x-amz-date", "authorization", "x-api-key", "x-amz-security-token"]
    expose_headers    = ["x-amz-request-id"]
    max_age           = 86400 # 24 hours
  }
}

# ============================================================================
# LAMBDA PERMISSIONS
# ============================================================================

# Allow public invocation of the Lambda function via Function URL
# Without this permission, the Function URL would return 403 Forbidden
resource "aws_lambda_permission" "allow_function_url" {
  statement_id           = "FunctionURLAllowPublicAccess"
  action                 = "lambda:InvokeFunctionUrl"
  function_name          = aws_lambda_function.medical_diagnosis.function_name
  principal              = "*"
  function_url_auth_type = "NONE"
}

# ============================================================================
# OPTIONAL: CLOUDWATCH ALARMS
# ============================================================================

# Alarm for Lambda errors
# Triggers when error rate exceeds threshold
resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  count = var.enable_alarms ? 1 : 0

  alarm_name          = "${var.function_name}-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = "300" # 5 minutes
  statistic           = "Sum"
  threshold           = "5"
  alarm_description   = "This metric monitors Lambda function errors"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.medical_diagnosis.function_name
  }

  tags = var.common_tags
}

# Alarm for Lambda duration (timeout warning)
# Triggers when execution time approaches timeout
resource "aws_cloudwatch_metric_alarm" "lambda_duration" {
  count = var.enable_alarms ? 1 : 0

  alarm_name          = "${var.function_name}-duration"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Average"
  threshold           = var.timeout * 800 # 80% of timeout
  alarm_description   = "This metric monitors Lambda function duration"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.medical_diagnosis.function_name
  }

  tags = var.common_tags
}

# Alarm for Lambda throttles
# Triggers when function is being throttled due to concurrency limits
resource "aws_cloudwatch_metric_alarm" "lambda_throttles" {
  count = var.enable_alarms ? 1 : 0

  alarm_name          = "${var.function_name}-throttles"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "Throttles"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Sum"
  threshold           = "5"
  alarm_description   = "This metric monitors Lambda function throttles"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.medical_diagnosis.function_name
  }

  tags = var.common_tags
}

# ============================================================================
# OPTIONAL: LAMBDA RESERVED CONCURRENT EXECUTIONS
# ============================================================================

# Uncomment to set reserved concurrency (prevents runaway costs)
/*
resource "aws_lambda_function_reserved_concurrent_executions" "medical_diagnosis_concurrency" {
  function_name                     = aws_lambda_function.medical_diagnosis.function_name
  reserved_concurrent_executions    = 10
}
*/
