# SageMaker Module for ML Model Hosting

# SageMaker Execution Role
resource "aws_iam_role" "sagemaker" {
  name_prefix = "${var.name_prefix}-sagemaker-"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "sagemaker.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "sagemaker" {
  role       = aws_iam_role.sagemaker.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"
}

# S3 Access Policy
resource "aws_iam_role_policy" "sagemaker_s3" {
  name_prefix = "${var.name_prefix}-sagemaker-s3-"
  role        = aws_iam_role.sagemaker.id

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
        Resource = "*"
      }
    ]
  })
}

# SageMaker Model
resource "aws_sagemaker_model" "main" {
  name               = "${var.name_prefix}-model"
  execution_role_arn = aws_iam_role.sagemaker.arn

  primary_container {
    image          = var.model_image
    model_data_url = var.model_data_url
  }

  vpc_config {
    subnets            = var.private_subnet_ids
    security_group_ids = [var.sagemaker_security_group_id]
  }

  tags = var.tags
}

# SageMaker Endpoint Configuration
resource "aws_sagemaker_endpoint_configuration" "main" {
  name = "${var.name_prefix}-endpoint-config"

  production_variants {
    variant_name           = "primary"
    model_name             = aws_sagemaker_model.main.name
    initial_instance_count = var.initial_instance_count
    instance_type          = var.instance_type
  }

  tags = var.tags
}

# SageMaker Endpoint
resource "aws_sagemaker_endpoint" "main" {
  name                 = "${var.name_prefix}-endpoint"
  endpoint_config_name = aws_sagemaker_endpoint_configuration.main.name

  tags = var.tags
}
