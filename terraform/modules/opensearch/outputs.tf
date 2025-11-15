output "opensearch_endpoint" {
  description = "OpenSearch domain endpoint"
  value       = "https://${aws_opensearch_domain.main.endpoint}"
}

output "opensearch_dashboard_endpoint" {
  description = "OpenSearch Dashboards endpoint"
  value       = "https://${aws_opensearch_domain.main.endpoint}/_dashboards"
}

output "domain_id" {
  description = "OpenSearch domain ID"
  value       = aws_opensearch_domain.main.domain_id
}

output "domain_arn" {
  description = "OpenSearch domain ARN"
  value       = aws_opensearch_domain.main.arn
}
