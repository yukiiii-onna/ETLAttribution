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
from utils.file_utils import download_csv
from utils.time_utils import set_default_time_range, get_time_range  # Import new functions
from include.data_generator import df_conversions, df_session_sources, df_session_costs

# Default arguments
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
    description="A refactored DAG with modular functions and time-range filtering",
    tags=["example"],
)

# **Set time range task**
set_time_range_task = PythonOperator(
    task_id="set_time_range_task",
    python_callable=set_default_time_range,
    dag=dag,
)

# **Retrieve the time range after setting it**
START_DATE, END_DATE = get_time_range()

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
    op_kwargs={"start_date": START_DATE, "end_date": END_DATE},
    dag=dag,
)

fill_channel_reporting_task = PythonOperator(
    task_id="fill_channel_reporting_task",
    python_callable=fill_channel_reporting,  # Do NOT use lambda
    op_kwargs={"start_date": START_DATE, "end_date": END_DATE},  # Pass arguments properly
    dag=dag,
)

download_csv_task = PythonOperator(
    task_id="download_csv_task",
    python_callable=download_csv,
    dag=dag,
)

# **Update dependencies**
[
    set_time_range_task >>
    execute_sql_task >> 
    insert_data_task >> 
    calculate_journeys_task >> 
    fill_channel_reporting_task >> 
    download_csv_task
    
    ]
