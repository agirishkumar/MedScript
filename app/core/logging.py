# app/core/logging.py

import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging():
    """
    Set up logging for the application.

    Creates a logs directory if it doesn't exist.
    Configures the root logger to log at the INFO level.
    Creates a custom logger with name "app" and sets its level to INFO.
    Creates two handlers: a StreamHandler for console output and a RotatingFileHandler for file output.
    Creates a formatter for the handlers and adds it to each handler.
    Adds the handlers to the logger.
    Returns the logger.
    """
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Configure root logger
    logging.basicConfig(level=logging.INFO)

    # Create a custom logger
    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)

    # Create handlers
    console_handler = logging.StreamHandler()
    file_handler = RotatingFileHandler(
        f"{log_dir}/app.log", maxBytes=10485760, backupCount=5
    )

    # Create formatters and add it to handlers
    log_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(log_format)
    file_handler.setFormatter(log_format)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

# Create a global logger instance
logger = setup_logging()