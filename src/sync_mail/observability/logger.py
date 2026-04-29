import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional

# Formats
CONCISE_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DETAILED_FORMAT = "%(asctime)s - %(levelname)s - [%(name)s:%(lineno)d] - [Batch: %(batch_id)s] [PK: %(primary_key)s] - %(message)s"

class ContextFormatter(logging.Formatter):
    """
    Custom formatter that ensures 'batch_id' and 'primary_key' exist in the record
    to avoid KeyErrors when using them in the format string.
    """
    def format(self, record):
        if not hasattr(record, "batch_id"):
            record.batch_id = "N/A"
        if not hasattr(record, "primary_key"):
            record.primary_key = "N/A"
        return super().format(record)

def configure_logging():
    """
    Configures the root logger with STDOUT and RotatingFileHandler.
    Settings are pulled from environment variables:
    - SYNC_MAIL_LOG_LEVEL: Default root level (default: INFO)
    - SYNC_MAIL_LOG_DIR: Directory for logs (default: logs)
    """
    level = os.environ.get("SYNC_MAIL_LOG_LEVEL", "INFO").upper()
    log_dir = os.environ.get("SYNC_MAIL_LOG_DIR", "logs")
    
    os.makedirs(log_dir, exist_ok=True)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers to avoid duplicates
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    # 1. StreamHandler to STDOUT (INFO)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(logging.Formatter(CONCISE_FORMAT))
    root_logger.addHandler(stdout_handler)
    
    # 2. RotatingFileHandler to logs/sync-mail.log (ERROR)
    log_file = os.path.join(log_dir, "sync-mail.log")
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=50 * 1024 * 1024, # 50 MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(ContextFormatter(DETAILED_FORMAT))
    root_logger.addHandler(file_handler)
    
    # Contract: No SQL text should be logged by default.
    # We set sqlalchemy and pymysql loggers to WARNING to avoid query noise.
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("pymysql").setLevel(logging.WARNING)

    root_logger.debug(f"Logging configured. STDOUT: INFO, File: ERROR ({log_file})")
