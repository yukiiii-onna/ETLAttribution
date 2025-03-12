from airflow.models import Variable
from datetime import datetime, timedelta
from .logger import log

def set_default_time_range():
    """
    Sets default values for START_DATE and END_DATE in Airflow Variables
    if they are not already set.
    """
    default_start_date = (datetime.today() - timedelta(days=7)).strftime("%Y-%m-%d")  # Last 7 days
    default_end_date = datetime.today().strftime("%Y-%m-%d")  # Today's date

    # Check if the variables exist and set them if not
    if not Variable.get("START_DATE", default_var=None):
        Variable.set("START_DATE", default_start_date)
        log.info(f"START_DATE set to {default_start_date}")
    else:
        log.info(f"START_DATE already set: {Variable.get('START_DATE')}")

    if not Variable.get("END_DATE", default_var=None):
        Variable.set("END_DATE", default_end_date)
        log.info(f"END_DATE set to {default_end_date}")
    else:
        log.info(f"END_DATE already set: {Variable.get('END_DATE')}")

def get_time_range():
    """
    Retrieves the START_DATE and END_DATE from Airflow Variables.
    If the variables do not exist, sets default values.
    """
    try:
        start_date = Variable.get("START_DATE")
        end_date = Variable.get("END_DATE")
    except KeyError:
        log.warning("START_DATE or END_DATE does not exist. Setting default values...")
        set_default_time_range()  # Set defaults if missing
        start_date = Variable.get("START_DATE")
        end_date = Variable.get("END_DATE")

    log.info(f"Using time range: {start_date} to {end_date}")
    return start_date, end_date
