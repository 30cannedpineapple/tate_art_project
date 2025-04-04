import os
import logging

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from google.cloud import storage
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateExternalTableOperator, BigQueryCreateEmptyDatasetOperator
import pyarrow.csv as pv
import pyarrow.parquet as pq

PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BUCKET = os.environ.get("GCP_GCS_BUCKET")

artwork_file = "artwork_data.csv"
artist_file = "artist_data.csv"
artwork_url = f"https://raw.githubusercontent.com/tategallery/collection/refs/heads/master/{artwork_file}"
artist_url = f"https://raw.githubusercontent.com/tategallery/collection/refs/heads/master/{artist_file}"
path_to_local_home = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", 'tate_data_all')



# NOTE: takes 20 mins, at an upload speed of 800kbps. Faster if your internet has a better upload speed
def upload_to_gcs(bucket, object_name, local_file):
    """
    Ref: https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-python
    :param bucket: GCS bucket name
    :param object_name: target path & file-name
    :param local_file: source path & file-name
    :return:
    """
    # WORKAROUND to prevent timeout for files > 6 MB on 800 kbps upload speed.
    # (Ref: https://github.com/googleapis/python-storage/issues/74)
    storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB
    storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB
    # End of Workaround

    client = storage.Client()
    bucket = client.bucket(bucket)

    blob = bucket.blob(object_name)
    blob.upload_from_filename(local_file)


default_args = {
    "owner": "airflow",
    "start_date": days_ago(1),
    "depends_on_past": False,
    "retries": 1,
}

# NOTE: DAG declaration - using a Context Manager (an implicit way)
with DAG(
    dag_id="data_ingestion_gcs_dag",
    schedule_interval="@daily",
    default_args=default_args,
    catchup=False,
    max_active_runs=1,
    tags=['dtc-de'],
) as dag:

    download_dataset_task = BashOperator(
        task_id="download_dataset_task",
        bash_command=(f"curl -sSL {artwork_url} > {path_to_local_home}/{artwork_file} && "
                      f"curl -sSL {artist_url} > {path_to_local_home}/{artist_file} "
        )
    )

    create_empty_dataset_task = BigQueryCreateEmptyDatasetOperator(
        task_id = "create_empty_dataset_task",
        dataset_id = BIGQUERY_DATASET,
        project_id = PROJECT_ID,
        location = 'US',
        exists_ok=True,
    )

    # TODO: Homework - research and try XCOM to communicate output values between 2 tasks/operators
    local_to_gcs_task1 = PythonOperator(
        task_id="local_to_gcs_task1",
        python_callable=upload_to_gcs,
        op_kwargs={
            "bucket": BUCKET,
            "object_name": f"raw/{artist_file}",
            "local_file": f"{path_to_local_home}/{artist_file}",
        },
    )

    local_to_gcs_task2 = PythonOperator(
        task_id="local_to_gcs_task2",
        python_callable=upload_to_gcs,
        op_kwargs={
            "bucket": BUCKET,
            "object_name": f"raw/{artwork_file}",
            "local_file": f"{path_to_local_home}/{artwork_file}",
        },
    )

    bigquery_external_table_task1 = BigQueryCreateExternalTableOperator(
        task_id="bigquery_external_table_task1",
        table_resource={
            "tableReference": {
                "projectId": PROJECT_ID,
                "datasetId": BIGQUERY_DATASET,
                "tableId": "artwork_external_table",
            },
            "externalDataConfiguration": {
                "sourceFormat": "CSV",
                "sourceUris": [f"gs://{BUCKET}/raw/{artwork_file}"],
            },
            "autodetect": True,
        },
        
    )

    bigquery_external_table_task2 = BigQueryCreateExternalTableOperator(
        task_id="bigquery_external_table_task2",
        table_resource={
            "tableReference": {
                "projectId": PROJECT_ID,
                "datasetId": BIGQUERY_DATASET,
                "tableId": "artist_external_table",
            },
            "externalDataConfiguration": {
                "sourceFormat": "CSV",
                "sourceUris": [f"gs://{BUCKET}/raw/{artist_file}"],
            },
            "autodetect": True,
        },
       
    )

    download_dataset_task >> create_empty_dataset_task >> [local_to_gcs_task1, local_to_gcs_task2] 
    local_to_gcs_task2 >> bigquery_external_table_task1
    local_to_gcs_task1 >> bigquery_external_table_task2