# tests/test_to_html.py

import base64
import tempfile
from pathlib import Path

import pytest

from report.to_html import markdown_to_html_with_images


def test_markdown_to_html_with_images(tmp_path: Path):
    # 1. создаём временный PNG файл
    img_path = tmp_path / "test.png"
    # простой 1x1 прозрачный PNG
    png_bytes = base64.b64decode(
        b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAA"
        b"AAC0lEQVR42mP8/x8AAwMCAO+/+mIAAAAASUVORK5CYII="
    )
    img_path.write_bytes(png_bytes)

    # 2. создаём markdown с картинкой
    md_content = f"![AltText](images/{img_path.name})"

    # 3. запускаем преобразование
    html = markdown_to_html_with_images(md_content, base_images_dir=tmp_path)

    # 4. проверяем, что в html встроилось data:image/png;base64
    assert "data:image/png;base64," in html, "Картинка не встроилась в HTML"
    assert "<img" in html and "AltText" in html
