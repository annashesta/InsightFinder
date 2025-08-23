# core/logger.py
import logging
import sys
from pathlib import Path

Path("logs").mkdir(exist_ok=True)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def get_logger(name: str, log_file: str | None = None) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    logger.addHandler(console)

    if log_file:
        handler = logging.FileHandler(f"logs/{log_file}", encoding="utf-8")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger