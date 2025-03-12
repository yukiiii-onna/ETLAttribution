import logging
import sys

# Configure logger
def get_logger(name="AirflowTask"):
    """
    Creates and returns a logger with a specific format.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Check if handlers exist to avoid duplicate logs
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False

    return logger

# Initialize a default logger instance
log = get_logger()
