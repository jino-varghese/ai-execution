output "redis_endpoint" {
  description = "Redis endpoint"
  value       = aws_elasticache_cluster.main.cache_nodes[0].address
}

output "redis_port" {
  description = "Redis port"
  value       = aws_elasticache_cluster.main.port
}

output "cluster_id" {
  description = "ElastiCache cluster ID"
  value       = aws_elasticache_cluster.main.cluster_id
}
