output "iceberg_warehouse_bucket" {
  value = aws_s3_bucket.iceberg_warehouse.bucket
}

output "ecr_repositories" {
  value = {
    telemetry_gateway = aws_ecr_repository.telemetry_gateway.repository_url
    safety_indexer    = aws_ecr_repository.safety_indexer.repository_url
    query_service_java = aws_ecr_repository.query_service_java.repository_url
  }
}
