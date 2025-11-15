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

variable "lambda_security_group_id" {
  description = "Security group ID for Lambda"
  type        = string
}

variable "data_bucket_name" {
  description = "Name of the S3 data bucket"
  type        = string
}

variable "data_bucket_arn" {
  description = "ARN of the S3 data bucket"
  type        = string
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
