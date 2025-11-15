variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs"
  type        = list(string)
}

variable "sagemaker_security_group_id" {
  description = "Security group ID for SageMaker"
  type        = string
}

variable "instance_type" {
  description = "SageMaker instance type"
  type        = string
  default     = "ml.m5.xlarge"
}

variable "initial_instance_count" {
  description = "Initial number of instances"
  type        = number
  default     = 1
}

variable "model_image" {
  description = "Docker image for the model"
  type        = string
  default     = "763104351884.dkr.ecr.us-east-1.amazonaws.com/huggingface-pytorch-inference:1.13.1-transformers4.26.0-cpu-py39-ubuntu20.04"
}

variable "model_data_url" {
  description = "S3 URL for model artifacts"
  type        = string
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
