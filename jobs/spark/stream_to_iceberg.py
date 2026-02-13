"""Spark Structured Streaming job.

Reads telemetry from Kafka and writes append-only rows to an Iceberg table.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_date
from pyspark.sql.types import (
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)


def build_spark() -> SparkSession:
    return (
        SparkSession.builder.appName("surgical-telemetry-stream")
        .config("spark.sql.catalog.local", "org.apache.iceberg.spark.SparkCatalog")
        .config("spark.sql.catalog.local.type", "hadoop")
        .config("spark.sql.catalog.local.warehouse", "s3a://surgical-lakehouse/warehouse")
        .getOrCreate()
    )


def run() -> None:
    spark = build_spark()

    schema = StructType(
        [
            StructField("event_id", StringType()),
            StructField("patient_id", StringType()),
            StructField("procedure_id", StringType()),
            StructField("robot_arm", StringType()),
            StructField("step", StringType()),
            StructField("force_newtons", DoubleType()),
            StructField("velocity_mm_s", DoubleType()),
            StructField("latency_ms", IntegerType()),
            StructField("error_code", StringType()),
            StructField("timestamp", TimestampType()),
        ]
    )

    raw = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", "kafka:9092")
        .option("subscribe", "surgical.telemetry.raw")
        .option("startingOffsets", "latest")
        .load()
    )

    parsed = raw.select(from_json(col("value").cast("string"), schema).alias("e")).select("e.*")
    enriched = parsed.withColumn("event_day", to_date(col("timestamp")))

    # Requires Iceberg runtime jar on cluster. This demonstrates the canonical write pattern.
    (
        enriched.writeStream.format("iceberg")
        .outputMode("append")
        .option("path", "local.db.surgical_events")
        .option("checkpointLocation", "s3a://surgical-lakehouse/checkpoints/surgical_events")
        .trigger(processingTime="5 seconds")
        .start()
        .awaitTermination()
    )


if __name__ == "__main__":
    run()
