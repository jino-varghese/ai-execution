# ============================================================================
# AI Medical Diagnosis System - Terraform Version Requirements
# ============================================================================
# This file defines the required Terraform version and provider versions.
# It ensures compatibility and consistent behavior across deployments.
# ============================================================================

terraform {
  # Require Terraform version 1.0 or higher
  required_version = ">= 1.0"

  # Required providers with version constraints
  required_providers {
    # AWS Provider
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0" # Use AWS provider version 5.x
    }

    # Archive Provider (for creating ZIP files)
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4"
    }
  }

  # Optional: Configure remote state backend
  # Uncomment and configure for team collaboration or production use
  /*
  backend "s3" {
    bucket         = "your-terraform-state-bucket"
    key            = "medical-diagnosis/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
  */
}

# ============================================================================
# AWS PROVIDER CONFIGURATION
# ============================================================================

provider "aws" {
  region = var.aws_region

  # Default tags applied to all resources
  default_tags {
    tags = {
      Project     = "AI-Medical-Diagnosis"
      ManagedBy   = "Terraform"
      Environment = var.environment
    }
  }

  # Optional: Assume role for cross-account deployment
  /*
  assume_role {
    role_arn     = "arn:aws:iam::ACCOUNT_ID:role/ROLE_NAME"
    session_name = "terraform-medical-diagnosis"
  }
  */
}

# ============================================================================
# ARCHIVE PROVIDER CONFIGURATION
# ============================================================================

provider "archive" {
  # No additional configuration needed
}
