# Lambda Module for data processing

# Lambda Execution Role
resource "aws_iam_role" "lambda" {
  name_prefix = "${var.name_prefix}-lambda-"

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

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

# S3 Access Policy
resource "aws_iam_role_policy" "lambda_s3" {
  name_prefix = "${var.name_prefix}-lambda-s3-"
  role        = aws_iam_role.lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          var.data_bucket_arn,
          "${var.data_bucket_arn}/*"
        ]
      }
    ]
  })
}

# Lambda function for data processing
resource "aws_lambda_function" "data_processor" {
  function_name = "${var.name_prefix}-data-processor"
  role          = aws_iam_role.lambda.arn

  # Placeholder values - update with actual deployment package
  filename      = "${path.module}/lambda_placeholder.zip"
  handler       = "index.handler"
  runtime       = "python3.11"
  timeout       = 300
  memory_size   = 1024

  vpc_config {
    subnet_ids         = var.private_subnet_ids
    security_group_ids = [var.lambda_security_group_id]
  }

  environment {
    variables = {
      DATA_BUCKET = var.data_bucket_name
    }
  }

  tags = var.tags
}

# Create a placeholder zip file for Lambda
resource "null_resource" "lambda_placeholder" {
  provisioner "local-exec" {
    command = <<EOF
      mkdir -p ${path.module}
      echo 'def handler(event, context):
    return {"statusCode": 200, "body": "Placeholder function"}' > ${path.module}/index.py
      cd ${path.module} && zip lambda_placeholder.zip index.py
    EOF
  }

  triggers = {
    always_run = timestamp()
  }
}

# S3 Event Notification for Lambda trigger
resource "aws_s3_bucket_notification" "data_upload" {
  bucket = var.data_bucket_name

  lambda_function {
    lambda_function_arn = aws_lambda_function.data_processor.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "uploads/"
  }

  depends_on = [aws_lambda_permission.allow_s3]
}

# Lambda permission for S3 to invoke
resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowExecutionFromS3"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.data_processor.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = var.data_bucket_arn
}
