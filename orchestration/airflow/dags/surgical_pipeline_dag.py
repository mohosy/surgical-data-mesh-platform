from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator


with DAG(
    dag_id="surgical_data_mesh_daily",
    start_date=datetime(2026, 1, 1),
    schedule="@hourly",
    catchup=False,
    tags=["surgical", "streaming", "lakehouse"],
) as dag:
    run_stream_job = BashOperator(
        task_id="run_spark_stream_job",
        bash_command="python jobs/spark/stream_to_iceberg.py",
    )

    run_dbt = BashOperator(
        task_id="run_dbt_models",
        bash_command="cd analytics/dbt && dbt run --profiles-dir .",
    )

    run_tests = BashOperator(
        task_id="run_data_tests",
        bash_command="cd analytics/dbt && dbt test --profiles-dir .",
    )

    run_stream_job >> run_dbt >> run_tests
