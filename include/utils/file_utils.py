import os
from .logger import log
from include.utils.config import EXPORT_DIR


CSV_PATH = os.path.join(EXPORT_DIR, "channel_reporting.csv")

def download_csv():
    """
    Task to confirm that the CSV file is ready for download.
    """
    if os.path.exists(CSV_PATH):
        log.info(f"✅ CSV file is ready for download: {CSV_PATH}")
    else:
        log.error(f"❌ CSV file not found at: {CSV_PATH}")
