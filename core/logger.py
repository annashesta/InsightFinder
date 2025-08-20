import logging
import sys
from pathlib import Path

Path("logs").mkdir(exist_ok=True)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(message)s")

def get_logger(name: str, log_file: str | None = None):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # убираем дублирование хендлеров при повторных вызовах
    if not logger.handlers:
        # консоль всегда
        console = logging.StreamHandler(sys.stdout)
        console.setFormatter(formatter)
        logger.addHandler(console)

        # файл — только если указан
        if log_file:
            handler = logging.FileHandler(f"logs/{log_file}", encoding="utf-8")
            handler.setFormatter(formatter)
            logger.addHandler(handler)

    return logger

analyst_logger = get_logger("Analyst", "analyst.log")
executor_logger = get_logger("Executor", "executor.log")
