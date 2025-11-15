# ElastiCache Redis Module

# Subnet Group
resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.name_prefix}-cache-subnet"
  subnet_ids = var.private_subnet_ids

  tags = merge(
    var.tags,
    {
      Name = "${var.name_prefix}-cache-subnet-group"
    }
  )
}

# Parameter Group
resource "aws_elasticache_parameter_group" "main" {
  name_prefix = "${var.name_prefix}-cache-params-"
  family      = "redis7"

  parameter {
    name  = "maxmemory-policy"
    value = "allkeys-lru"
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.name_prefix}-cache-parameter-group"
    }
  )

  lifecycle {
    create_before_destroy = true
  }
}

# ElastiCache Cluster
resource "aws_elasticache_cluster" "main" {
  cluster_id           = "${var.name_prefix}-redis"
  engine               = "redis"
  engine_version       = "7.0"
  node_type            = var.node_type
  num_cache_nodes      = var.num_cache_nodes
  parameter_group_name = aws_elasticache_parameter_group.main.name
  subnet_group_name    = aws_elasticache_subnet_group.main.name
  security_group_ids   = [var.cache_security_group_id]

  port = 6379

  snapshot_retention_limit = 5
  snapshot_window          = "03:00-05:00"
  maintenance_window       = "mon:05:00-mon:07:00"

  tags = merge(
    var.tags,
    {
      Name = "${var.name_prefix}-redis-cluster"
    }
  )
}
