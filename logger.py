import logging
import logging.config
import os

# Ensure the logs directory exists
os.makedirs("/app/logs", exist_ok=True)

# Define the configuration dictionary
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
    },
    "handlers": {
        "file_handler": {
            "class": "logging.FileHandler",
            "formatter": "standard",
            "filename": "/app/logs/app.log",  # Change the path to the logs directory
            "mode": "a",
        },
        "console_handler": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["file_handler", "console_handler"],
            "level": "INFO",
            "propagate": True
        }
    }
}

# Apply the logging configuration
logging.config.dictConfig(LOGGING_CONFIG)

# Get the root logger
logger = logging.getLogger(__name__)