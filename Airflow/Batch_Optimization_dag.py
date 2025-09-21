from __future__ import annotations
import pendulum
from airflow.decorators import dag, task
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.operators.bash import BashOperator

@dag(
    dag_id="batch_optimization_dag",
    schedule="0 18 * * 1-5",  # Every weekday at 18:00 IST
    start_date=pendulum.datetime(2025, 1, 1, tz="Asia/Kolkata"),
    catchup=False,
    tags=["batch", "optimization"],
    default_args={"owner": "airflow"}
)
def batch_optimization_dag():
    """
    This DAG handles the nightly batch optimization pipeline. It waits for the
    real-time snapshot to be uploaded and then runs the MILP solver.
    """
    
    wait_for_snapshot_upload = ExternalTaskSensor(
        task_id="wait_for_snapshot_upload",
        external_dag_id="realtime_streaming_dag",
        external_task_id="start_producer_consumer_stream",
        # Wait for the external DAG to have a success state
        allowed_states=["success"],
        # The external DAG should be a specific past run
        execution_delta=pendulum.duration(hours=1)
    )

    run_milp_solver = BashOperator(
        task_id="run_milp_solver",
        bash_command="python /opt/airflow/dags/scripts/milp_solver.py"
    )

    wait_for_snapshot_upload >> run_milp_solver

# Instantiate the DAG
batch_optimization_dag()