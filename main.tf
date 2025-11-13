terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Create deployment package
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda_package"
  output_path = "${path.module}/lambda_function.zip"

  depends_on = [null_resource.prepare_lambda_package]
}

# Prepare Lambda package with dependencies
resource "null_resource" "prepare_lambda_package" {
  triggers = {
    lambda_function = filemd5("${path.module}/lambda_function.py")
    requirements    = filemd5("${path.module}/requirements.txt")
  }

  provisioner "local-exec" {
    command = <<-EOT
      rm -rf lambda_package lambda_function.zip
      mkdir -p lambda_package
      pip install -r requirements.txt -t lambda_package/ --upgrade
      cp lambda_function.py lambda_package/
    EOT
  }
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "${var.function_name}-role"

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

  tags = var.tags
}

# Attach basic Lambda execution policy
resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Lambda Function
resource "aws_lambda_function" "gen_ai_dashboard" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = var.function_name
  role            = aws_iam_role.lambda_role.arn
  handler         = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime         = var.runtime
  timeout         = var.timeout
  memory_size     = var.memory_size

  environment {
    variables = {
      OPENWEATHER_API_KEY = var.openweather_api_key
    }
  }

  tags = var.tags
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${var.function_name}"
  retention_in_days = var.log_retention_days

  tags = var.tags
}

# Lambda Function URL
resource "aws_lambda_function_url" "gen_ai_dashboard_url" {
  function_name      = aws_lambda_function.gen_ai_dashboard.function_name
  authorization_type = "NONE"

  cors {
    allow_credentials = true
    allow_origins     = ["*"]
    allow_methods     = ["GET", "POST"]
    allow_headers     = ["content-type", "x-amz-date", "authorization", "x-api-key", "x-amz-security-token", "x-amz-user-agent"]
    max_age          = 86400
  }
}

# Lambda permission for Function URL
resource "aws_lambda_permission" "allow_function_url" {
  statement_id           = "AllowExecutionFromFunctionURL"
  action                = "lambda:InvokeFunctionUrl"
  function_name         = aws_lambda_function.gen_ai_dashboard.function_name
  principal             = "*"
  function_url_auth_type = "NONE"
}
