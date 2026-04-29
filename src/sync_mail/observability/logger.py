import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional

# Define log formats
CONCISE_FORMAT = "%(asctime)s - %(levelname)s - %(message)s" # Basic format for stdout
DETAILED_FORMAT = "%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s" # More detailed for file

def configure_logging(level: str = "INFO", log_dir: str = "logs"):
    """
    Configures the root logger with StreamHandler and RotatingFileHandler.

    Args:
        level (str): The minimum logging level for the root logger (e.g., "INFO", "DEBUG").
        log_dir (str): The directory where log files will be stored.
    """
    # Ensure the log directory exists
    import os
    os.makedirs(log_dir, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Prevent adding handlers multiple times if called more than once
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # 1. StreamHandler to STDOUT
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO) # As per plan, STDOUT is INFO level
    formatter = logging.Formatter(CONCISE_FORMAT)
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)

    # 2. RotatingFileHandler to file
    log_file_path = os.path.join(log_dir, "sync-mail.log")
    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=50 * 1024 * 1024,  # 50 MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.ERROR) # As per plan, file is ERROR level
    formatter = logging.Formatter(DETAILED_FORMAT) # Detailed format for file logs
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Important: Avoid logging SQL queries. Loggers within specific modules
    # (e.g., db module) should be configured to filter out SQL.
    # For the root logger, we rely on the user of the API to not log sensitive data.
    # If a specific logger for DB queries is created, it can be configured here.

# Example of how to get a logger (use a specific logger for modules)
# logger = logging.getLogger(__name__)

# Example usage (would be called once at application startup):
# configure_logging(level="DEBUG", log_dir="logs")
# logger.info("Application started.")
# logger.error("This is an error message.")
