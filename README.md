# Surgical Data Mesh Platform

Production-style reference architecture for **robotic surgery telemetry**: ingest high-frequency events, process streams, build a lakehouse, and serve low-latency safety insights.

This project is intentionally designed to demonstrate the exact engineering surface area common in modern healthcare data platforms: **Python + Java microservices**, **Kafka streaming**, **Spark + Iceberg**, **Cassandra/MongoDB/Elasticsearch storage patterns**, **AWS IaC**, and **testing discipline**.

## Why this project is strong

- Models a realistic operating-room telemetry workflow rather than a toy CRUD app.
- Uses a polyglot architecture: Python services for ingestion/indexing and a Java service for query APIs.
- Shows both batch-lakehouse thinking (Spark/Iceberg) and online serving (Cassandra/Elasticsearch/MongoDB).
- Includes practical engineering workflows: unit/integration tests, Docker, Kubernetes manifests, Terraform starter, and Prometheus metrics.

## Advanced capabilities

- **Idempotent ingest path:** replay-safe event handling keyed by `event_id`.
- **Batch ingest endpoint:** supports up to 1000 events per call with per-batch accounting.
- **Stateful safety engine:** composite risk scoring, high-force/high-latency/error triggers, and alert feeds.
- **Risk analytics APIs:** patient and procedure summaries (`avg risk`, `p95 latency`, `critical count`).
- **Operational metrics:** Prometheus counters for deduplication, alert emission, and query load.
- **Analytical transforms:** Spark-side safety scoring, force spike detection, and KPI aggregation helpers.
- **Java analytical API:** top critical alerts and patient summary endpoints for low-latency consumers.

## Architecture

```mermaid
flowchart LR
    A["Robotic telemetry\n(force, velocity, latency, step)"] --> B["Telemetry Gateway\nPython/FastAPI"]
    B --> C["Kafka topic\nsurgical.telemetry.raw"]
    C --> D["Spark Structured Streaming\nparse/enrich/risk scoring"]
    D --> E["Iceberg tables\nS3 warehouse"]

    B --> F["Safety Indexer\nPython/FastAPI"]
    F --> G["Cassandra\npatient timeline"]
    F --> H["Elasticsearch\nerror/step search"]
    F --> I["MongoDB\ncase summary docs"]

    G --> J["Java Query Service\nSpring Boot API"]
    H --> J
    I --> J

    B --> K["Prometheus\n/metrics scraping"]
    F --> K
```

## Stack coverage map

- `Python`: telemetry gateway + safety indexer + Spark jobs
- `Java`: Spring Boot query service
- `AWS`: Terraform starter for S3/ECR/CloudWatch + AWS-ready deployment model
- `Kubernetes`: deployable manifests for all microservices
- `Airflow`: DAG included for Spark -> dbt -> data tests orchestration
- `dbt`: staging/mart models included with Snowflake profile template
- `Kafka`: raw telemetry stream transport
- `Flink/Spark`: Spark Structured Streaming implemented + Flink windowed alert reference module
- `Snowflake/Iceberg`: Iceberg lakehouse table write path implemented (Snowflake is downstream warehouse target)
- `Cassandra`: timeline backend interface and deployment profile
- `MongoDB`: document summary backend
- `Elasticsearch`: search backend
- `TDD + tests`: service-level unit/integration tests with CI
- `IaC`: Terraform + Kubernetes config
- `Metrics/Monitoring`: Prometheus endpoints and scrape config
- `Microservices`: ingest, indexer, and query services with independent deploy units

## Repository layout

```text
services/
  ingest-service/        # Python FastAPI telemetry gateway -> Kafka
  indexer-service/       # Python FastAPI indexer -> Cassandra/Elastic/Mongo
  query-service-java/    # Java Spring Boot read/query API
jobs/
  spark/                 # Spark Structured Streaming -> Iceberg
  flink/                 # Flink windowed alert reference flow
orchestration/
  airflow/dags/          # Airflow DAG for end-to-end scheduling
analytics/
  dbt/                   # dbt project with staging + marts
infra/
  terraform/             # AWS IaC starter (S3/ECR/CloudWatch)
  k8s/                   # Kubernetes manifests
monitoring/
  prometheus.yml         # Metrics scraping
scripts/
  demo_load.py           # Synthetic event generator
```

## Quick start

```bash
docker compose up --build
```

In a second shell:

```bash
python scripts/demo_load.py --count 75
curl "http://localhost:8080/events/batch" -H "Content-Type: application/json" -d '{"events":[{"event_id":"evt-demo-100","patient_id":"pat-1","procedure_id":"proc-1","robot_arm":"arm_1","step":"suturing","force_newtons":18.2,"velocity_mm_s":11.0,"latency_ms":42,"timestamp":"2026-02-13T18:20:00Z","attributes":{"or_room":"OR-1"}}]}'
curl "http://localhost:8081/search?q=sutur"
curl "http://localhost:8081/patients/pat-1/timeline"
curl "http://localhost:8081/alerts/recent?min_level=high&limit=5"
curl "http://localhost:8081/patients/pat-1/risk-summary"
curl "http://localhost:8081/procedures/proc-1/risk-summary"
curl "http://localhost:8082/api/health"
curl "http://localhost:8082/api/patients/pat-1/summary"
curl "http://localhost:8082/api/alerts/top?limit=3"
```

## Test commands

```bash
cd services/ingest-service && pytest -q
cd services/indexer-service && pytest -q
cd jobs && pytest -q
cd services/query-service-java && mvn test
```

## Engineering notes

- The service defaults to in-memory stores for local reliability; backend toggles allow Cassandra/Elasticsearch/MongoDB profiles without changing API contracts.
- Spark job writes are configured in canonical Iceberg style and designed for checkpointed exactly-once-like processing semantics.
- Terraform intentionally starts compact, so infra can grow iteratively (MSK/EMR/EKS modules can be layered next without rework).
- Ingest service now supports deduplicated and batch workflows while preserving single-event low-latency paths.
