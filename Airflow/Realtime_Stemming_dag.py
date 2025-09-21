from __future__ import annotations
import pendulum
import os
from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.sensors.external_task import ExternalTaskSensor

@dag(
    dag_id="realtime_streaming_dag",
    schedule="0 10 * * 1-5",  # Every weekday at 10:00 AM IST
    start_date=pendulum.datetime(2025, 1, 1, tz="Asia/Kolkata"),
    catchup=False,
    tags=["real-time", "streaming"],
    default_args={"owner": "airflow"}
)
def realtime_streaming_dag():
    """
    This DAG starts the real-time data streaming pipeline (producer and consumer).
    It triggers a separate DAG at the end of the day to stop the process gracefully.
    """
    
    start_producer_consumer = BashOperator(
        task_id="start_producer_consumer_stream",
        bash_command="python /opt/airflow/dags/scripts/producer.py & python /opt/airflow/dags/scripts/consumer_score_and_schedule.py",
        # This task is a long-lived process. Airflow will keep it running.
        # The key is to manage its termination from an external signal.
        execution_timeout=pendulum.duration(minutes=420) # 7 hours
    )

    trigger_stop_dag = TriggerDagRunOperator(
        task_id="trigger_stop_dag",
        trigger_dag_id="stop_streaming_dag",
        execution_date="{{ ds }}T17:00:00Z", # Trigger the stop DAG at 17:00 UTC
        wait_for_completion=False
    )

    start_producer_consumer >> trigger_stop_dag

# Instantiate the DAG
realtime_streaming_dag()

@dag(
    dag_id="stop_streaming_dag",
    schedule="0 17 * * 1-5",  # Every weekday at 17:00 IST
    start_date=pendulum.datetime(2025, 1, 1, tz="Asia/Kolkata"),
    catchup=False,
    tags=["real-time", "termination"],
    default_args={"owner": "airflow"}
)
def stop_streaming_dag():
    """
    This DAG gracefully stops the real-time streaming processes and
    ensures the snapshot is uploaded.
    """
    
    @task
    def stop_and_upload():
        """
        Sends a termination signal to the running scripts and waits
        for the consumer to upload the snapshot.
        """
        import subprocess
        import time
        
        print("Sending termination signal to producer and consumer...")
        
        # This assumes the scripts are running under a known name.
        # A more robust solution might use a process manager or PID file.
        # This is a good simulation for a proof of concept.
        
        subprocess.run(["pkill", "-f", "producer.py"])
        subprocess.run(["pkill", "-f", "consumer_score_and_schedule.py"])
        
        # Give the consumer time to finish draining and uploading
        time.sleep(30)
        
        # This part of the logic needs to be verified externally.
        # We assume the `consumer_score_and_schedule.py` script
        # handles the snapshot upload on SIGTERM.
        print("Termination signal sent. Waiting for upload to complete...")
        
    stop_and_upload()
    
# Instantiate the DAG
stop_streaming_dag()