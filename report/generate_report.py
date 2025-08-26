# report/generate_report.py
"""Модуль для сохранения отчетов в формате Markdown."""

from pathlib import Path
from datetime import datetime

REPORTS_DIR = Path("report/output")
REPORTS_DIR.mkdir(exist_ok=True)


def save_report(content: str, filename: str = None) -> str:
    """
    Сохраняет содержимое отчета в файл.

    Args:
        content: Текст отчета.
        filename: Имя файла. Если не указано, генерируется автоматически.

    Returns:
        Путь к сохраненному файлу.
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"insightfinder_report_{timestamp}.md"

    filepath = REPORTS_DIR / filename

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return str(filepath)
