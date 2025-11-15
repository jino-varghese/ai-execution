variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name to be used for resource naming"
  type        = string
  default     = "travel-itinerary-ai"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "s3_bucket_name" {
  description = "S3 bucket name for static website hosting (must be globally unique)"
  type        = string
  default     = ""  # Will be auto-generated if not provided
}

variable "lambda_function_name" {
  description = "Name of the Lambda function"
  type        = string
  default     = "itinerary-generator"
}

variable "tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default = {
    Project     = "AI Travel Itinerary Generator"
    ManagedBy   = "Terraform"
    Environment = "dev"
  }
}
