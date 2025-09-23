# report/to_html.py
"""
Модуль для преобразования Markdown-отчета в HTML с встроенными изображениями.
"""
import re
import base64
import logging
from pathlib import Path
from typing import Optional
from markdown_it import MarkdownIt

# Настройка логгера для этого модуля
logger = logging.getLogger(__name__)

# парсерр markdown
md_parser = MarkdownIt("commonmark", {"breaks": True}).enable("table")

def _image_to_base64(image_path: Path) -> Optional[str]:
    """
    Читает изображение и возвращает его в виде строки base64.

    Args:
        image_path: Путь к файлу изображения.

    Returns:
        Строка данных изображения в формате base64 или None в случае ошибки.
    """
    try:
        if not image_path.exists():
            logger.warning(f"Файл изображения не найден при конвертации в HTML: {image_path}")
            return None
        
        suffix = image_path.suffix.lower()
        if suffix == ".png":
            mime_type = "image/png"
        elif suffix in [".jpg", ".jpeg"]:
            mime_type = "image/jpeg"
        else:
            logger.warning(f"Неподдерживаемый формат изображения: {suffix} в файле {image_path}")
            return None

        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        return f"data:{mime_type};base64,{encoded_string}"

    except Exception as e:
        logger.error(f"Ошибка кодирования изображения {image_path}: {e}")
        return None


def markdown_to_html_with_images(
    markdown_content: str, base_images_dir: str = "report/output/images"
) -> str:
    """
    Конвертирует Markdown в HTML, встраивая локальные изображения как base64.
    Использует markdown-it-py для парсинга (поддержка GitHub-style таблиц).
    """
    images_dir_path = Path(base_images_dir).resolve()
    logger.info(f"Начало конвертации Markdown в HTML. Папка с изображениями: {images_dir_path}")

    # 1. Подмена изображений на base64
    def replace_markdown_image_tag(match):
        alt_text = match.group(1).strip()
        img_path_str = match.group(2).strip()

        if 'images/' in img_path_str:
            clean_path_str = img_path_str.split('images/')[-1]
        else:
            clean_path_str = Path(img_path_str).name
            
        img_full_path = images_dir_path / clean_path_str
        data_url = _image_to_base64(img_full_path)
        
        if data_url:
            return f'<img src="{data_url}" alt="{alt_text}" class="insightfinder-report-image" data-original-alt="{alt_text}">'
        else:
            logger.warning(f"Не удалось встроить изображение: {img_path_str}")
            return f'[Изображение не найдено: {alt_text}]'

    md_image_pattern = r'!\[(.*?)\]\(([^)]+)\)'
    processed_md = re.sub(md_image_pattern, replace_markdown_image_tag, markdown_content)

    # 2. Рендерим HTML с помощью markdown-it-py
    html_body = md_parser.render(processed_md)

    # 3. Оборачиваем <img> в <figure>
    def wrap_images(match):
        img_tag = match.group(0)
        alt_match = re.search(r'data-original-alt="([^"]*)"', img_tag)
        alt_text = alt_match.group(1) if alt_match else ""
        return (
            f'<figure class="insightfinder-figure">{img_tag}'
            f'<figcaption class="insightfinder-figcaption">{alt_text}</figcaption></figure>'
        )
    
    html_body = re.sub(r'<img[^>]+class="insightfinder-report-image"[^>]*>', wrap_images, html_body)
    
    # 4. Добавляем стили
    styled_html = f"""
    <style>
      #insightfinder-report-container {{
        background-color: #ffffff !important; color: #333333 !important; padding: 30px;
        border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 16px; line-height: 1.6; max-width: 100%; margin: 0 auto;
      }}
      h1 {{ color: #2c3e50 !important; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
      h2 {{ color: #34495e !important; border-bottom: 1px solid #bdc3c7; padding-bottom: 8px; }}
      table {{ border-collapse: collapse; width: 100%; margin: 1.5em 0; }}
      th, td {{ border: 1px solid #dfe2e5; padding: 12px 15px; text-align: left; }}
      th {{ background-color: #f1f8ff !important; }}
      tr:nth-child(even) {{ background-color: #fafbfc; }}
      .insightfinder-report-image {{ max-width: 100%; height: auto; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
      figure {{ margin: 1.5em 0; text-align: center; }}
      figcaption {{ font-size: 0.9em; font-style: italic; color: #6a737d; margin-top: 10px; }}
    </style>
    <div id="insightfinder-report-container">
        {html_body}
    </div>
    """

    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>InsightFinder Report</title>
    </head>
    <body>
        {styled_html}
    </body>
    </html>
    """
    logger.info("Конвертация Markdown в HTML успешно завершена.")
    return full_html
