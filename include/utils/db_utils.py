import sqlite3
import pandas as pd
from include.utils.config import DB_PATH,SQL_PATH
from .logger import log

def execute_sql_script():
    """Executes the SQL script to drop and recreate tables."""
    log.info("Executing SQL script...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    with open(SQL_PATH, "r") as sql_file:
        sql_script = sql_file.read()

    cursor.executescript(sql_script)
    conn.commit()
    conn.close()
    log.info("SQL script executed successfully!")

def insert_data(df_conversions, df_session_sources, df_session_costs):
    """Inserts data into SQLite tables."""
    log.info("Inserting data into SQLite tables...")
    conn = sqlite3.connect(DB_PATH)

    df_conversions.to_sql("conversions", conn, if_exists="replace", index=False)
    df_session_sources.to_sql("session_sources", conn, if_exists="replace", index=False)
    df_session_costs.to_sql("session_costs", conn, if_exists="replace", index=False)

    conn.commit()
    conn.close()
    log.info("Data inserted successfully!")
