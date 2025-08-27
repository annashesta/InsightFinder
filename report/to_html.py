# report/to_html.py
"""
Модуль для преобразования Markdown-отчета в HTML с встроенными изображениями.
"""

import re
import base64
import logging
from pathlib import Path
from typing import Optional

# Настройка логгера для этого модуля
logger = logging.getLogger(__name__)


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
            logger.warning(f"Файл изображения не найден для HTML: {image_path}")
            return None

        suffix = image_path.suffix.lower()
        if suffix == ".png":
            mime_type = "image/png"
        elif suffix in [".jpg", ".jpeg"]:
            mime_type = "image/jpeg"
        elif suffix == ".gif":
            mime_type = "image/gif"
        else:
            logger.warning(
                f"Неподдерживаемый формат изображения для HTML: {suffix} "
                f"для файла {image_path}"
            )
            return None

        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        return f"data:{mime_type};base64,{encoded_string}"
    except Exception as e:
        logger.error(
            f"Ошибка при кодировании изображения {image_path} в base64 для HTML: {e}"
        )
        return None


def markdown_to_html_with_images(
    markdown_content: str, base_images_dir: str = "report/output/images"
) -> str:
    """
    Преобразует Markdown-текст в HTML, встраивая изображения как base64.

    Args:
        markdown_content: Исходный Markdown текст.
        base_images_dir: Базовая директория для поиска изображений.

    Returns:
        HTML-строка с встроенными изображениями.
    """
    images_dir_path = Path(base_images_dir).resolve()
    logger.info(f"Преобразование Markdown в HTML. Images dir: {images_dir_path}")

    # Обработка изображений в Markdown перед преобразованием
    def replace_markdown_image_tag(match):
        alt_text = match.group(1).strip()
        img_path_str = match.group(2).strip()
        logger.debug(
            f"Найдена ссылка на изображение для HTML (Markdown): alt='{alt_text}', "
            f"path='{img_path_str}'"
        )

        # Очищаем путь от префиксов
        clean_path_str = img_path_str
        if clean_path_str.startswith("images/"):
            clean_path_str = clean_path_str[len("images/"):]
        elif clean_path_str.startswith("report/output/images/"):
            clean_path_str = clean_path_str[len("report/output/images/"):]
        elif "report/output/images/" in clean_path_str:
            parts = clean_path_str.split("report/output/images/")
            if len(parts) > 1:
                clean_path_str = parts[1]

        img_full_path = images_dir_path / clean_path_str

        data_url = _image_to_base64(img_full_path)
        
        if data_url:
            logger.debug(f"Изображение встроено в Markdown перед HTML: {img_full_path}")
            return f'<img src="{data_url}" alt="{alt_text}" class="insightfinder-report-image" data-original-alt="{alt_text}">'
        else:
            logger.warning(f"Изображение не встроено в Markdown, оставлен placeholder: {img_path_str}")
            return f'[Изображение не найдено: {alt_text}]'

    md_image_pattern = r'!\[(.*?)\]\(([^)]+)\)'
    processed_md_for_html = re.sub(md_image_pattern, replace_markdown_image_tag, markdown_content, flags=re.DOTALL)

    def process_lists(text):
        lines = text.split('\n')
        processed_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Проверяем начало маркированного списка
            if re.match(r'^\* ', line):
                list_items = []
                while i < len(lines) and re.match(r'^\* ', lines[i]):
                    # Убираем маркер '* ' и добавляем элемент
                    list_items.append(lines[i][2:])
                    i += 1
                # Формируем один HTML-список для всех собранных элементов
                html_list = '<ul>\n' + '\n'.join([f'  <li>{item}</li>' for item in list_items]) + '\n</ul>'
                processed_lines.append(html_list)
                continue # Продолжаем со следующей строки после списка
            
            # Проверяем начало нумерованного списка
            if re.match(r'^\d+\. ', line):
                list_items = []
                while i < len(lines) and re.match(r'^\d+\. ', lines[i]):
                    # Убираем маркер '1. ' и добавляем элемент
                    list_items.append(lines[i][lines[i].find('. ') + 2:])
                    i += 1
                # Формируем один HTML-список для всех собранных элементов
                html_list = '<ol>\n' + '\n'.join([f'  <li>{item}</li>' for item in list_items]) + '\n</ol>'
                processed_lines.append(html_list)
                continue # Продолжаем со следующей строки после списка
                
            # Если строка не является частью списка, добавляем её как есть
            processed_lines.append(line)
            i += 1
            
        return '\n'.join(processed_lines)

    # Применяем логику обработки списков
    html_with_processed_lists = process_lists(processed_md_for_html)

    # Преобразование оставшихся базовых элементов Markdown в HTML
    # Заголовки
    html_from_md = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html_with_processed_lists, flags=re.MULTILINE)
    html_from_md = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html_from_md, flags=re.MULTILINE)
    html_from_md = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html_from_md, flags=re.MULTILINE)
    html_from_md = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html_from_md, flags=re.MULTILINE)
    
    # Жирный и курсив (делаем до кода, чтобы не сломать `` ` ``)
    html_from_md = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_from_md)
    html_from_md = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html_from_md)
    
    # Код (inline)
    html_from_md = re.sub(r'`(.+?)`', r'<code>\1</code>', html_from_md)
    
    # Горизонтальная линия
    html_from_md = re.sub(r'^---$', r'<hr>', html_from_md, flags=re.MULTILINE)
    
    # Ссылки
    html_from_md = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html_from_md)
    
    # Блочные кодовые фрагменты (fenced code blocks)
    html_from_md = re.sub(r'```(\w*)\n(.*?)\n```', r'<pre><code class="language-\1">\2</code></pre>', html_from_md, flags=re.DOTALL)
    
    # Специальная обработка таблиц
    def process_table(match):
        table_text = match.group(0)
        lines = table_text.strip().split('\n')
        
        if len(lines) < 2:
            return table_text

        headers = [header.strip() for header in lines[0].strip('|').split('|') if header.strip()]
        
        data_rows = []
        for line in lines[1:]:
            if re.fullmatch(r'\s*\|?(?:\s*-+\s*\|)*\s*', line):
                continue
            cells = [cell.strip() for cell in line.strip('|').split('|') if cell.strip()]
            if cells:
                data_rows.append(cells)
        
        html_table = '<table>\n'
        if headers:
            html_table += '  <thead>\n  <tr>\n'
            for header in headers:
                html_table += f'    <th>{header}</th>\n'
            html_table += '  </tr>\n  </thead>\n'
        
        html_table += '  <tbody>\n'
        for row in data_rows:
            html_table += '  <tr>\n'
            for cell in row:
                html_table += f'    <td>{cell}</td>\n'
            html_table += '  </tr>\n'
        html_table += '  </tbody>\n'
        html_table += '</table>'
        
        return html_table

    table_pattern = r'(?:^\|.*$\n){2,}'
    html_with_tables = re.sub(table_pattern, process_table, html_from_md, flags=re.MULTILINE)

    # Пост-обработка HTML: стилизация изображений
    def wrap_images(match):
        img_tag = match.group(0)
        alt_match = re.search(r'alt="([^"]*)"', img_tag) or re.search(r'data-original-alt="([^"]*)"', img_tag)
        alt_text = alt_match.group(1) if alt_match else ""
        
        return (
            f'<figure class="insightfinder-figure">'
            f'{img_tag}'
            f'<figcaption class="insightfinder-figcaption">{alt_text}</figcaption>'
            f'</figure>'
        )
    
    html_with_styled_images = re.sub(r'<img[^>]+class="insightfinder-report-image"[^>]*>', wrap_images, html_with_tables)
    
    # Добавляем улучшенные стили
    styled_html = f"""
    <style>
    /* Общие стили для отчета */
    #insightfinder-report-container {{
        background-color: #ffffff !important;
        color: #333333 !important;
        padding: 30px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 16px;
        line-height: 1.6;
        max-width: 100%;
        margin: 0 auto;
    }}

    /* Заголовки */
    #insightfinder-report-container h1 {{
        color: #2c3e50 !important;
        border-bottom: 2px solid #3498db;
        padding-bottom: 10px;
        margin-top: 1.5em;
        margin-bottom: 0.8em;
        font-weight: 600;
    }}
    #insightfinder-report-container h2 {{
        color: #34495e !important;
        border-bottom: 1px solid #bdc3c7;
        padding-bottom: 8px;
        margin-top: 1.3em;
        margin-bottom: 0.7em;
        font-weight: 500;
    }}
    #insightfinder-report-container h3, 
    #insightfinder-report-container h4 {{
        color: #2c3e50 !important;
        margin-top: 1.2em;
        margin-bottom: 0.6em;
        font-weight: 500;
    }}

    /* Параграфы */
    #insightfinder-report-container p {{
        color: #333333 !important;
        margin: 0.8em 0;
        text-align: justify;
    }}

    /* Списки */
    #insightfinder-report-container ul, 
    #insightfinder-report-container ol {{
        margin: 0.8em 0;
        padding-left: 1.5em;
    }}
    #insightfinder-report-container li {{
        margin: 0.3em 0;
    }}

    /* Ссылки */
    #insightfinder-report-container a {{
        color: #3498db !important;
        text-decoration: none;
    }}
    #insightfinder-report-container a:hover {{
        text-decoration: underline;
    }}

    /* Код */
    #insightfinder-report-container code {{
        background-color: #f8f9fa !important;
        padding: 2px 6px;
        border-radius: 4px;
        font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
        font-size: 0.9em;
        color: #e74c3c !important;
    }}
    #insightfinder-report-container pre {{
        background-color: #f8f9fa !important;
        padding: 15px;
        border-radius: 6px;
        overflow-x: auto;
        border: 1px solid #e1e4e8;
        margin: 1em 0;
    }}
    #insightfinder-report-container pre code {{
        background-color: transparent;
        color: inherit;
        padding: 0;
    }}

    /* Таблицы */
    #insightfinder-report-container table {{
        border-collapse: collapse;
        width: 100%;
        margin: 1.5em 0;
        font-size: 0.95em;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }}
    #insightfinder-report-container th, 
    #insightfinder-report-container td {{
        border: 1px solid #dfe2e5;
        padding: 12px 15px;
        text-align: left;
    }}
    #insightfinder-report-container th {{
        background-color: #f1f8ff !important;
        font-weight: 600;
        color: #24292e;
    }}
    #insightfinder-report-container tr:nth-child(even) {{
        background-color: #fafbfc;
    }}
    #insightfinder-report-container tr:hover {{
        background-color: #f6f8fa;
    }}

    /* Изображения */
    #insightfinder-report-container .insightfinder-report-image {{
        max-width: 100%;
        height: auto;
        border: 1px solid #d1d5da;
        border-radius: 6px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transform: scale(0.8); /* Уменьшаем на 20% */
    }}
    
    /* Подписи к изображениям */
    #insightfinder-report-container figure {{
        margin: 1.5em 0;
        text-align: center;
    }}
    #insightfinder-report-container figcaption {{
        font-size: 0.9em;
        font-style: italic;
        color: #6a737d;
        margin-top: 10px;
    }}

    /* Горизонтальная линия */
    #insightfinder-report-container hr {{
        border: 0;
        height: 1px;
        background: #e1e4e8;
        margin: 2em 0;
    }}

    /* Цитаты */
    #insightfinder-report-container blockquote {{
        margin: 1em 0;
        padding: 0.5em 1em;
        border-left: 4px solid #3498db;
        background-color: #f8f9fa;
        color: #586069;
    }}
    </style>
    {html_with_styled_images}
    """

    # Обернем в основной контейнер
    full_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Отчет InsightFinder</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Roboto+Mono&display=swap" rel="stylesheet">
</head>
<body>
    <div id="insightfinder-report-container">
{styled_html}
    </div>
</body>
</html>
"""
    logger.info("Преобразование Markdown в HTML завершено.")
    return full_html
