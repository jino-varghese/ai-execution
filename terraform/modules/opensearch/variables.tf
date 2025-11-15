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

variable "opensearch_security_group_id" {
  description = "Security group ID for OpenSearch"
  type        = string
}

variable "instance_type" {
  description = "OpenSearch instance type"
  type        = string
  default     = "t3.medium.search"
}

variable "instance_count" {
  description = "Number of instances"
  type        = number
  default     = 2
}

variable "ebs_volume_size" {
  description = "EBS volume size in GB"
  type        = number
  default     = 100
}

variable "master_user_name" {
  description = "Master user name for OpenSearch"
  type        = string
  default     = "admin"
  sensitive   = true
}

variable "master_user_password" {
  description = "Master user password for OpenSearch"
  type        = string
  default     = "Admin123!SecurePassword"
  sensitive   = true
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
