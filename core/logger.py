# core/logger.py
import logging
import sys
from pathlib import Path

# Создаем папку logs, если её нет
Path("logs").mkdir(exist_ok=True)

# Формат логов
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def get_logger(name: str, log_file: str | None = None) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # удаляем все предыдущие обработчики
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

    # Обработчик для вывода в консоль
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    logger.addHandler(console)

    # Обработчик для записи в файл (с перезаписью)
    if log_file:
        # Явно указываем mode='w' — перезапись, а не дописывание
        handler = logging.FileHandler(f"logs/{log_file}", mode='w', encoding="utf-8")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger