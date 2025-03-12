# data_generator.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)

# Generate synthetic user IDs
user_ids = [f"user_{i}" for i in range(1, 101)]  # 100 unique users

# Generate valid conversions data (No future timestamps)
num_conversions = 80
conversion_dates = [datetime(2025, 3, 9) - timedelta(days=np.random.randint(1, 3)) for _ in range(num_conversions)]
conversions_data = {
    "conv_id": [f"conv_{i}" for i in range(num_conversions)],
    "user_id": np.random.choice(user_ids, num_conversions),
    "conv_date": [dt.strftime("%Y-%m-%d") for dt in conversion_dates],
    "conv_time": [dt.strftime("%H:%M:%S") for dt in conversion_dates],
    "revenue": np.round(np.random.uniform(10, 500, num_conversions), 2),
}
df_conversions = pd.DataFrame(conversions_data)

# Generate valid session sources data (Ensuring events happen before conversion)
num_sessions = 500
session_dates = [datetime(2025, 3, 9) - timedelta(days=np.random.randint(2, 5)) for _ in range(num_sessions)]
channels = ["Google Ads", "Facebook", "Email", "SEO", "Direct", "TikTok"]
session_data = {
    "session_id": [f"session_{i}" for i in range(num_sessions)],
    "user_id": np.random.choice(user_ids, num_sessions),
    "event_date": [dt.strftime("%Y-%m-%d") for dt in session_dates],
    "event_time": [dt.strftime("%H:%M:%S") for dt in session_dates],
    "channel_name": np.random.choice(channels, num_sessions),
    "holder_engagement": np.random.choice([0, 1], num_sessions, p=[0.7, 0.3]),
    "closer_engagement": np.random.choice([0, 1], num_sessions, p=[0.8, 0.2]),
    "impression_interaction": np.random.choice([0, 1], num_sessions, p=[0.85, 0.15]),
}
df_session_sources = pd.DataFrame(session_data)

# Generate session costs data
session_cost_data = {
    "session_id": df_session_sources["session_id"],
    "cost": np.round(np.random.uniform(1, 50, num_sessions), 2),
}
df_session_costs = pd.DataFrame(session_cost_data)