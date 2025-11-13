# ============================================================================
# AI Medical Diagnosis System - Terraform Variables
# ============================================================================
# This file defines all configurable variables for the deployment.
# You can override these values by:
# 1. Creating a terraform.tfvars file
# 2. Using -var flag: terraform apply -var="function_name=my-function"
# 3. Using environment variables: TF_VAR_function_name=my-function
# ============================================================================

# ============================================================================
# REQUIRED VARIABLES
# ============================================================================

# AWS Region where resources will be deployed
variable "aws_region" {
  description = "AWS region where the Lambda function will be deployed"
  type        = string
  default     = "us-east-1"

  validation {
    condition     = can(regex("^[a-z]{2}-[a-z]+-[0-9]{1}$", var.aws_region))
    error_message = "AWS region must be in the format: us-east-1, eu-west-1, etc."
  }
}

# ============================================================================
# LAMBDA FUNCTION CONFIGURATION
# ============================================================================

# Lambda function name
variable "function_name" {
  description = "Name of the Lambda function"
  type        = string
  default     = "ai-medical-diagnosis"

  validation {
    condition     = length(var.function_name) <= 64 && can(regex("^[a-zA-Z0-9-_]+$", var.function_name))
    error_message = "Function name must be 64 characters or less and contain only alphanumeric characters, hyphens, and underscores."
  }
}

# Python runtime version
variable "python_runtime" {
  description = "Python runtime version for Lambda function"
  type        = string
  default     = "python3.11"

  validation {
    condition     = contains(["python3.9", "python3.10", "python3.11", "python3.12"], var.python_runtime)
    error_message = "Python runtime must be one of: python3.9, python3.10, python3.11, python3.12"
  }
}

# Lambda memory allocation (MB)
variable "memory_size" {
  description = "Amount of memory in MB allocated to the Lambda function (128-10240)"
  type        = number
  default     = 512

  validation {
    condition     = var.memory_size >= 128 && var.memory_size <= 10240
    error_message = "Memory size must be between 128 MB and 10240 MB."
  }
}

# Lambda timeout (seconds)
variable "timeout" {
  description = "Maximum execution time in seconds (1-900)"
  type        = number
  default     = 30

  validation {
    condition     = var.timeout >= 1 && var.timeout <= 900
    error_message = "Timeout must be between 1 and 900 seconds."
  }
}

# ============================================================================
# IAM ROLE CONFIGURATION
# ============================================================================

# IAM role name for Lambda execution
variable "lambda_role_name" {
  description = "Name of the IAM role for Lambda execution"
  type        = string
  default     = "ai-medical-diagnosis-role"

  validation {
    condition     = length(var.lambda_role_name) <= 64
    error_message = "IAM role name must be 64 characters or less."
  }
}

# ============================================================================
# CLOUDWATCH LOGS CONFIGURATION
# ============================================================================

# Log retention period in days
variable "log_retention_days" {
  description = "Number of days to retain CloudWatch logs (0 = never expire)"
  type        = number
  default     = 7

  validation {
    condition = contains([
      0, 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180,
      365, 400, 545, 731, 1827, 3653
    ], var.log_retention_days)
    error_message = "Log retention must be a valid CloudWatch Logs retention value."
  }
}

# ============================================================================
# MONITORING AND ALARMS
# ============================================================================

# Enable CloudWatch alarms
variable "enable_alarms" {
  description = "Enable CloudWatch alarms for monitoring"
  type        = bool
  default     = false
}

# ============================================================================
# ENVIRONMENT CONFIGURATION
# ============================================================================

# Environment name (dev, staging, prod)
variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod"
  }
}

# Log level for application
variable "log_level" {
  description = "Logging level for the application"
  type        = string
  default     = "INFO"

  validation {
    condition     = contains(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], var.log_level)
    error_message = "Log level must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL"
  }
}

# ============================================================================
# ENVIRONMENT VARIABLES FOR LAMBDA
# ============================================================================

# Optional: API keys or other environment variables
variable "environment_variables" {
  description = "Map of environment variables for Lambda function"
  type        = map(string)
  default     = {}
  sensitive   = true
}

# ============================================================================
# TAGGING
# ============================================================================

# Common tags to apply to all resources
variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default = {
    Project     = "AI-Medical-Diagnosis"
    ManagedBy   = "Terraform"
    Environment = "Development"
    Owner       = "Healthcare-AI-Team"
    CostCenter  = "Research"
  }
}

# ============================================================================
# NETWORKING (Optional - for VPC deployment)
# ============================================================================

# Enable VPC configuration (for private deployment)
variable "enable_vpc" {
  description = "Enable VPC configuration for Lambda"
  type        = bool
  default     = false
}

# VPC subnet IDs (required if enable_vpc = true)
variable "subnet_ids" {
  description = "List of subnet IDs for Lambda VPC configuration"
  type        = list(string)
  default     = []
}

# VPC security group IDs (required if enable_vpc = true)
variable "security_group_ids" {
  description = "List of security group IDs for Lambda VPC configuration"
  type        = list(string)
  default     = []
}

# ============================================================================
# COST OPTIMIZATION
# ============================================================================

# Reserved concurrent executions (prevents runaway costs)
variable "reserved_concurrent_executions" {
  description = "Reserved concurrent executions for Lambda function (-1 = unreserved)"
  type        = number
  default     = -1

  validation {
    condition     = var.reserved_concurrent_executions >= -1
    error_message = "Reserved concurrent executions must be -1 (unreserved) or a positive number."
  }
}

# Enable X-Ray tracing for debugging
variable "enable_xray_tracing" {
  description = "Enable AWS X-Ray tracing for the Lambda function"
  type        = bool
  default     = false
}

# ============================================================================
# CORS CONFIGURATION
# ============================================================================

# Allowed origins for CORS
variable "cors_allowed_origins" {
  description = "List of allowed origins for CORS"
  type        = list(string)
  default     = ["*"] # Allow all origins (for demo purposes)
}

# Allowed methods for CORS
variable "cors_allowed_methods" {
  description = "List of allowed HTTP methods for CORS"
  type        = list(string)
  default     = ["GET", "POST", "OPTIONS"]
}

# Allowed headers for CORS
variable "cors_allowed_headers" {
  description = "List of allowed headers for CORS"
  type        = list(string)
  default     = ["content-type", "x-amz-date", "authorization", "x-api-key"]
}

# CORS max age (seconds)
variable "cors_max_age" {
  description = "CORS max age in seconds"
  type        = number
  default     = 86400 # 24 hours
}
