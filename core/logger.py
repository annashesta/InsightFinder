# core/logger.py
import logging
import sys
from pathlib import Path
from typing import Optional

logs_dir = Path("logs")
logs_dir.mkdir(parents=True, exist_ok=True)

DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

def _make_formatter() -> logging.Formatter:
    return logging.Formatter(DEFAULT_FORMAT)

def get_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """
    Возвращает настроенный logger.
    Если log_file указан — добавляет FileHandler в logs/<log_file>.
    Idempotent: повторные вызовы не дублируют хендлеры.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # StreamHandler (stdout) — один раз
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(_make_formatter())
        logger.addHandler(ch)

    # FileHandler если нужно
    if log_file:
        log_path = logs_dir / log_file
        # проверка, есть ли уже FileHandler на этот файл
        exists = False
        for h in logger.handlers:
            if isinstance(h, logging.FileHandler):
                base = getattr(h, "baseFilename", None)
                if base and Path(base).resolve() == log_path.resolve():
                    exists = True
                    break
        if not exists:
            fh = logging.FileHandler(log_path, mode="a", encoding="utf-8")
            fh.setFormatter(_make_formatter())
            logger.addHandler(fh)

    return logger