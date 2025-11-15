# OpenSearch Module for RAG (Retrieval Augmented Generation)

# OpenSearch Domain
resource "aws_opensearch_domain" "main" {
  domain_name    = "${var.name_prefix}-opensearch"
  engine_version = "OpenSearch_2.11"

  cluster_config {
    instance_type          = var.instance_type
    instance_count         = var.instance_count
    zone_awareness_enabled = var.instance_count > 1

    dynamic "zone_awareness_config" {
      for_each = var.instance_count > 1 ? [1] : []
      content {
        availability_zone_count = min(var.instance_count, 3)
      }
    }
  }

  ebs_options {
    ebs_enabled = true
    volume_size = var.ebs_volume_size
    volume_type = "gp3"
    throughput  = 125
    iops        = 3000
  }

  vpc_options {
    subnet_ids         = var.instance_count > 1 ? slice(var.private_subnet_ids, 0, min(var.instance_count, 3)) : [var.private_subnet_ids[0]]
    security_group_ids = [var.opensearch_security_group_id]
  }

  encrypt_at_rest {
    enabled = true
  }

  node_to_node_encryption {
    enabled = true
  }

  domain_endpoint_options {
    enforce_https       = true
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }

  advanced_security_options {
    enabled                        = true
    internal_user_database_enabled = true
    master_user_options {
      master_user_name     = var.master_user_name
      master_user_password = var.master_user_password
    }
  }

  access_policies = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = "*"
        }
        Action   = "es:*"
        Resource = "arn:aws:es:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:domain/${var.name_prefix}-opensearch/*"
      }
    ]
  })

  tags = merge(
    var.tags,
    {
      Name    = "${var.name_prefix}-opensearch"
      Purpose = "Vector search for RAG"
    }
  )
}

data "aws_region" "current" {}
data "aws_caller_identity" "current" {}
