# core/logger.py
import logging
import sys
from pathlib import Path

# Создаем папку logs, если её нет
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Путь к общему файлу логов
log_file_path = logs_dir / "app.log"

# Формат логов
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Настройка корневого логгера для записи ВСЕХ логов в файл
# Это обеспечит запись всех сообщений от всех частей приложения
root_logger = logging.getLogger()
# Устанавливаем уровень для корневого логгера
root_logger.setLevel(logging.INFO)

# Проверяем, есть ли уже файловый обработчик для этого файла, чтобы не добавлять дубликаты
file_handler_exists = any(
    isinstance(handler, logging.FileHandler) and Path(handler.baseFilename).resolve() == log_file_path.resolve()
    for handler in root_logger.handlers
)

if not file_handler_exists:
    # Создаем и добавляем файловый обработчик к корневому логгеру
    file_handler = logging.FileHandler(log_file_path, mode='a', encoding='utf-8')
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    print(f"Логирование в файл настроено: {log_file_path}")

def get_logger(name: str, log_file: str | None = None) -> logging.Logger:
    """
    Получает или создает логгер с указанным именем.
    Теперь он будет наследовать настройки корневого логгера (включая запись в app.log),
    а также может добавить дополнительный файловый обработчик для специфичного файла.

    Args:
        name: Имя логгера (например, __name__ или "core.orchestrator").
        log_file: (Опционально) Имя дополнительного файла для записи логов 
                  (например, "orchestrator.log"). Если указан, логи будут 
                  записываться и в этот файл, и в общий app.log.
                  
    Returns:
        Настроенный объект logging.Logger.
    """
    logger = logging.getLogger(name)
    
    # Устанавливаем уровень, если он еще не установлен или ниже нужного
    # Обычно это не нужно, так как уровень установлен у корневого логгера
    # if logger.level == logging.NOTSET:
    #     logger.setLevel(logging.INFO)

    # Проверяем существующие обработчики у этого конкретного логгера
    current_handlers = set((type(h).__name__, getattr(h, 'baseFilename', None)) for h in logger.handlers)

    # Добавляем обработчик для вывода в консоль, если его еще нет 
    # (наследуется от корневого, но можно добавить явно для уверенности)
    console_handler_key = ('StreamHandler', None)
    if console_handler_key not in current_handlers:
        console = logging.StreamHandler(sys.stdout)
        console.setFormatter(formatter)
        logger.addHandler(console)

    # Добавляем дополнительный обработчик для записи в специфичный файл, 
    # если указан файл и обработчик еще не добавлен
    # Это позволяет, например, иметь отдельный orchestrator.log помимо общего app.log
    if log_file:
        specific_log_path = logs_dir / log_file
        specific_handler_key = ('FileHandler', str(specific_log_path.resolve()))
        
        if specific_handler_key not in current_handlers:
            # mode='a' для добавления
            handler = logging.FileHandler(specific_log_path, mode='a', encoding="utf-8")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
    return logger