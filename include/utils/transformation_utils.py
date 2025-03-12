import pandas as pd
import sqlite3
from .api_utils import send_customer_journeys_to_api
from .db_utils import DB_PATH
from .logger import log


def calculate_customer_journeys():
    """Calculates customer journeys and sends them to the API."""

    
    log.info("Calculating customer journeys")
    conn = sqlite3.connect(DB_PATH)

    conversions_df = pd.read_sql("SELECT * FROM conversions", conn)
    session_sources_df = pd.read_sql("SELECT * FROM session_sources", conn)
    session_costs_df = pd.read_sql("SELECT * FROM session_costs", conn)

    session_data = pd.merge(session_sources_df, session_costs_df, on="session_id", how="left")
    session_data["event_timestamp"] = pd.to_datetime(session_data["event_date"] + " " + session_data["event_time"])
    conversions_df["conv_timestamp"] = pd.to_datetime(conversions_df["conv_date"] + " " + conversions_df["conv_time"])

    customer_journeys = []
    for _, conv_row in conversions_df.iterrows():
        user_id = conv_row["user_id"]
        conv_timestamp = conv_row["conv_timestamp"]
        conv_id = conv_row["conv_id"]

        user_sessions = session_data[(session_data["user_id"] == user_id) & (session_data["event_timestamp"] <= conv_timestamp)]
        if user_sessions.empty:
            continue
        if user_sessions[["holder_engagement", "closer_engagement"]].sum().sum() == 0:
            continue

        for _, session_row in user_sessions.iterrows():
            journey = {
                "conversion_id": conv_id,
                "session_id": session_row["session_id"],
                "timestamp": session_row["event_timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
                "channel_label": session_row["channel_name"],
                "holder_engagement": session_row["holder_engagement"],
                "closer_engagement": session_row["closer_engagement"],
                "conversion": 1 if session_row["session_id"] == user_sessions.iloc[-1]["session_id"] else 0,
                "impression_interaction": session_row["impression_interaction"],
            }
            customer_journeys.append(journey)

    df_cleaned = pd.DataFrame(customer_journeys)
    results, errors = send_customer_journeys_to_api(df_cleaned.to_dict(orient="records"))

    df_results = pd.DataFrame(results)
    df_results.to_sql("attribution_customer_journey", conn, if_exists="replace", index=False)

    conn.commit()
    conn.close()
    log.info("Customer journeys processed and saved successfully!")


def fill_channel_reporting():
    """
    Queries data from multiple tables, transforms it, and populates `channel_reporting`.
    """
    log.info("Filling channel reporting table...")
    conn = sqlite3.connect(DB_PATH)

    # Fetch data from tables
    df_session_sources = pd.read_sql("SELECT * FROM session_sources", conn)
    df_session_costs = pd.read_sql("SELECT * FROM session_costs", conn)
    df_conversions = pd.read_sql("SELECT * FROM conversions", conn)
    df_attribution_customer_journey = pd.read_sql("SELECT * FROM attribution_customer_journey", conn)

    # Ensure correct column names
    df_attribution_customer_journey.rename(columns={"conversion_id": "conv_id"}, inplace=True)

    # Merge session_sources with session_costs
    df_sessions = df_session_sources.merge(df_session_costs, on="session_id", how="left")

    # Merge sessions with attribution_customer_journey
    df_combined = df_sessions.merge(df_attribution_customer_journey, on="session_id", how="inner")

    # Merge with conversions to get revenue
    df_combined = df_combined.merge(df_conversions[["conv_id", "revenue"]], on="conv_id", how="left")

    # Calculate IHC Revenue
    df_combined["ihc_revenue"] = df_combined["ihc"] * df_combined["revenue"]

    # Aggregate data for `channel_reporting`
    df_channel_reporting = df_combined.groupby(["channel_name", "event_date"]).agg(
        cost=("cost", "sum"),
        ihc=("ihc", "sum"),
        ihc_revenue=("ihc_revenue", "sum"),
        total_orders=("conv_id", "nunique")
    ).reset_index()

    # Calculate Cost Per Order (CPO) and Return on Ad Spend (ROAS)
    df_channel_reporting["CPO"] = df_channel_reporting["cost"] / df_channel_reporting["total_orders"]
    df_channel_reporting["ROAS"] = df_channel_reporting["ihc_revenue"] / df_channel_reporting["cost"]

    # Handle NaN values
    df_channel_reporting["CPO"].fillna(0, inplace=True)
    df_channel_reporting["ROAS"].fillna(0, inplace=True)

    log.info("Channel reporting data:")
    log.info(df_channel_reporting)

    # Save results to the `channel_reporting` table
    df_channel_reporting.to_sql("channel_reporting", conn, if_exists="replace", index=False)

    conn.commit()
    conn.close()
    log.info("Channel reporting data saved successfully!")
