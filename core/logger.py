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
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Переменная для отслеживания, был ли уже настроен корневой логгер в этом процессе
_root_logger_configured = False

def _setup_root_logger():
    """Настраивает корневой логгер для записи в app.log с перезаписью."""
    global _root_logger_configured
    if _root_logger_configured:
        return

    # Удаляем существующие FileHandler для app.log
    handlers_to_remove = [
        h for h in root_logger.handlers 
        if isinstance(h, logging.FileHandler) and 
           Path(h.baseFilename).resolve() == log_file_path.resolve()
    ]
    for handler in handlers_to_remove:
        handler.close()
        root_logger.removeHandler(handler)

    # Создаем новый FileHandler с mode='w' для перезаписи
    file_handler = logging.FileHandler(log_file_path, mode='w', encoding='utf-8')
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Добавляем обработчик для консоли, если его еще нет
    if not any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
    _root_logger_configured = True
    print(f"Логирование в файл настроено (перезапись): {log_file_path}")

# Настраиваем корневой логгер при импорте модуля
_setup_root_logger()

def get_logger(name: str, log_file: str | None = None) -> logging.Logger:
    """
    Получает или создает логгер с указанным именем.
    Логгер будет наследовать настройки корневого логгера (включая запись в app.log),
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
    
    # Добавляем дополнительный обработчик для записи в специфичный файл, 
    # если указан файл. Этот файл также будет перезаписываться при каждом запуске.
    if log_file:
        specific_log_path = logs_dir / log_file
        # Проверяем, есть ли уже обработчик для этого конкретного файла
        handler_exists = any(
            isinstance(h, logging.FileHandler) and 
            Path(h.baseFilename).resolve() == specific_log_path.resolve()
            for h in logger.handlers
        )
        
        if not handler_exists:
            # mode='w' для перезаписи
            try:
                handler = logging.FileHandler(specific_log_path, mode='w', encoding="utf-8")
                handler.setFormatter(formatter)
                logger.addHandler(handler)
            except Exception as e:
                # Если не удалось создать файл, записываем ошибку в корневой логгер
                root_logger.error(f"Не удалось создать лог-файл {specific_log_path}: {e}")
            
    return logger