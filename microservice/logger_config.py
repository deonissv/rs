import os
from pathlib import Path

CWD = Path(__file__).parent
LOG_DIR = "logs"
LOG_FILE = "logs.jsonl"

LOGGER_NAME = "logger"
LOG_FORMAT = '{"timestamp": "%(asctime)s", %(message)s}'


if not os.path.exists(CWD / LOG_DIR):
    os.makedirs(CWD / LOG_DIR)

logs_target = CWD / LOG_DIR / LOG_FILE

logging_schema = {
    "version": 1,
    "formatters": {
        "standard": {
            "class": "logging.Formatter",
            "format": LOG_FORMAT,
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "standard",
            "level": "NOTSET",
            "filename": logs_target,
            "mode": "a",
            "encoding": "utf-8",
            "maxBytes": 2147483648,
            "backupCount": 4,
        },
    },
    "loggers": {
        LOGGER_NAME: {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        }
    },
    "root": {"level": "INFO", "handlers": ["file"]},
}
