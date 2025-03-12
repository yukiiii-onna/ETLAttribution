from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
import sys
import os

# Add include folder to Python path
sys.path.insert(0, os.path.abspath("/usr/local/airflow/include"))

# Import utility functions
from utils.db_utils import execute_sql_script, insert_data
from utils.transformation_utils import calculate_customer_journeys, fill_channel_reporting
from include.data_generator import df_conversions, df_session_sources, df_session_costs

default_args = {
    "owner": "Astro",
    "retries": 3,
    "start_date": datetime(2024, 1, 1),
}

dag = DAG(
    dag_id="refactored_attribution_dag",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
    description="A refactored DAG with modular functions",
    tags=["example"],
)

execute_sql_task = PythonOperator(
    task_id="execute_sql_task",
    python_callable=execute_sql_script,
    dag=dag,
)

insert_data_task = PythonOperator(
    task_id="insert_data_task",
    python_callable=lambda: insert_data(df_conversions, df_session_sources, df_session_costs),
    dag=dag,
)

calculate_journeys_task = PythonOperator(
    task_id="calculate_journeys_task",
    python_callable=calculate_customer_journeys,
    dag=dag,
)

fill_channel_reporting_task = PythonOperator(
    task_id="fill_channel_reporting_task",
    python_callable=fill_channel_reporting,
    dag=dag,
)

# Set task dependencies
execute_sql_task >> insert_data_task >> calculate_journeys_task >> fill_channel_reporting_task

