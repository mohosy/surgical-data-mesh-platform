provider "aws" {
  region = var.aws_region
}

locals {
  prefix = "${var.project_name}-${var.environment}"
}

resource "aws_s3_bucket" "iceberg_warehouse" {
  bucket = "${local.prefix}-iceberg-warehouse"

  tags = {
    Project = var.project_name
    Env     = var.environment
    Stack   = "spark-iceberg"
  }
}

resource "aws_s3_bucket_versioning" "iceberg_warehouse_versioning" {
  bucket = aws_s3_bucket.iceberg_warehouse.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_cloudwatch_log_group" "platform_logs" {
  name              = "/${local.prefix}/platform"
  retention_in_days = 30
}

resource "aws_ecr_repository" "telemetry_gateway" {
  name = "${local.prefix}/telemetry-gateway"
}

resource "aws_ecr_repository" "safety_indexer" {
  name = "${local.prefix}/safety-indexer"
}

resource "aws_ecr_repository" "query_service_java" {
  name = "${local.prefix}/query-service-java"
}

# Extend this baseline with MSK, EMR on EKS, and managed Cassandra/OpenSearch modules.
# Keeping this starter intentionally compact enables a fast first deploy and iterative IaC growth.
