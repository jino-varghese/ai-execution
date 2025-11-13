terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "AI-Medical-Diagnosis"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# ============================================================================
# DATA SOURCES
# ============================================================================

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# ============================================================================
# IAM ROLE FOR LAMBDA
# ============================================================================

resource "aws_iam_role" "lambda_execution_role" {
  name = "${var.project_name}-lambda-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-lambda-role"
  }
}

# Attach AWS managed policy for basic Lambda execution
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Additional policy for Lambda if needed (e.g., for Bedrock, DynamoDB, etc.)
resource "aws_iam_role_policy" "lambda_additional_permissions" {
  name = "${var.project_name}-lambda-policy"
  role = aws_iam_role.lambda_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/${var.project_name}-*:*"
      }
    ]
  })
}

# ============================================================================
# CLOUDWATCH LOG GROUP
# ============================================================================

resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${var.project_name}-${var.environment}"
  retention_in_days = var.log_retention_days

  tags = {
    Name = "${var.project_name}-logs"
  }
}

# ============================================================================
# LAMBDA FUNCTION PACKAGE
# ============================================================================

# Create ZIP file for Lambda deployment
data "archive_file" "lambda_package" {
  type        = "zip"
  source_file = "${path.module}/medical_diagnosis_lambda.py"
  output_path = "${path.module}/lambda_package.zip"
}

# ============================================================================
# LAMBDA FUNCTION
# ============================================================================

resource "aws_lambda_function" "medical_diagnosis" {
  filename         = data.archive_file.lambda_package.output_path
  function_name    = "${var.project_name}-${var.environment}"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "medical_diagnosis_lambda.lambda_handler"
  source_code_hash = data.archive_file.lambda_package.output_base64sha256
  runtime         = var.lambda_runtime
  timeout         = var.lambda_timeout
  memory_size     = var.lambda_memory_size

  environment {
    variables = {
      ENVIRONMENT = var.environment
      LOG_LEVEL   = var.log_level
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.lambda_logs,
    aws_iam_role_policy_attachment.lambda_basic_execution
  ]

  tags = {
    Name = "${var.project_name}-function"
  }
}

# ============================================================================
# LAMBDA FUNCTION URL (Public Access)
# ============================================================================

resource "aws_lambda_function_url" "medical_diagnosis_url" {
  function_name      = aws_lambda_function.medical_diagnosis.function_name
  authorization_type = var.enable_public_access ? "NONE" : "AWS_IAM"

  cors {
    allow_credentials = false
    allow_origins     = var.cors_allow_origins
    allow_methods     = ["*"]
    allow_headers     = ["*"]
    expose_headers    = ["*"]
    max_age          = 86400
  }
}

# ============================================================================
# CLOUDWATCH ALARMS (Optional)
# ============================================================================

resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  count = var.enable_alarms ? 1 : 0

  alarm_name          = "${var.project_name}-lambda-errors-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name        = "Errors"
  namespace          = "AWS/Lambda"
  period             = "300"
  statistic          = "Sum"
  threshold          = var.error_threshold
  alarm_description  = "This metric monitors lambda errors"
  treat_missing_data = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.medical_diagnosis.function_name
  }

  tags = {
    Name = "${var.project_name}-error-alarm"
  }
}

resource "aws_cloudwatch_metric_alarm" "lambda_duration" {
  count = var.enable_alarms ? 1 : 0

  alarm_name          = "${var.project_name}-lambda-duration-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name        = "Duration"
  namespace          = "AWS/Lambda"
  period             = "300"
  statistic          = "Average"
  threshold          = var.duration_threshold
  alarm_description  = "This metric monitors lambda execution duration"
  treat_missing_data = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.medical_diagnosis.function_name
  }

  tags = {
    Name = "${var.project_name}-duration-alarm"
  }
}

# # ============================================================================
# # OUTPUTS
# # ============================================================================

# output "lambda_function_name" {
#   description = "Name of the Lambda function"
#   value       = aws_lambda_function.medical_diagnosis.function_name
# }

# output "lambda_function_arn" {
#   description = "ARN of the Lambda function"
#   value       = aws_lambda_function.medical_diagnosis.arn
# }

# output "lambda_function_url" {
#   description = "Public URL of the Lambda function"
#   value       = aws_lambda_function_url.medical_diagnosis_url.function_url
# }

# output "lambda_role_arn" {
#   description = "ARN of the Lambda execution role"
#   value       = aws_iam_role.lambda_execution_role.arn
# }

# output "cloudwatch_log_group" {
#   description = "Name of the CloudWatch log group"
#   value       = aws_cloudwatch_log_group.lambda_logs.name
# }

# output "deployment_region" {
#   description = "AWS region where resources are deployed"
#   value       = data.aws_region.current.name
# }

# output "aws_account_id" {
#   description = "AWS Account ID"
#   value       = data.aws_caller_identity.current.account_id
# }
