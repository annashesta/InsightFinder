# ui/gradio_app.py
"""
Gradio UI для InsightFinder.
"""

import os
import io
import zipfile
import re
import base64
import tempfile
from pathlib import Path
from typing import Tuple, List, Optional

import gradio as gr
import pandas as pd

from core.pipeline import analyze_dataset
from core.logger import get_logger
from core.utils import find_binary_target

# --- Импорт OpenAI ---
try:
    from openai import OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print(
        "Библиотека 'openai' не установлена. "
        "Установите её для функции выбора модели: `pip install openai`"
    )

logger = get_logger(__name__, "gradio_app.log")


# --- Обработка изображений ---
class MarkdownImageProcessor:
    """Обрабатывает Markdown, находя изображения и встраивая их как base64."""

    def __init__(self, base_images_dir: str = "report/output/images"):
        """
        Инициализирует процессор.

        Args:
            base_images_dir: Базовая директория для поиска изображений.
        """
        self.base_images_dir = Path(base_images_dir).resolve()
        logger.debug(
            f"MarkdownImageProcessor инициализирован с base_images_dir: "
            f"{self.base_images_dir}"
        )

    def _image_to_base64(self, image_path: Path) -> Optional[str]:
        """
        Читает изображение и возвращает его в виде строки base64.

        Args:
            image_path: Путь к файлу изображения.

        Returns:
            Строка данных изображения в формате base64 или None в случае ошибки.
        """
        try:
            if not image_path.exists():
                logger.warning(f"Файл изображения не найден: {image_path}")
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
                    f"Неподдерживаемый формат изображения: {suffix} "
                    f"для файла {image_path}"
                )
                return None

            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            return f"data:{mime_type};base64,{encoded_string}"
        except Exception as e:
            logger.error(
                f"Ошибка при кодировании изображения {image_path} в base64: {e}"
            )
            return None

    def process_markdown(self, markdown_content: str) -> Tuple[str, List]:
        """
        Обрабатывает Markdown, находя изображения, кодируя их в base64 и
        заменяя ссылки на HTML-теги <img>.

        Args:
            markdown_content: Исходный Markdown текст.

        Returns:
            Кортеж из (обработанный HTML/Markdown текст, пустой список).
            Второй элемент для совместимости.
        """
        images_found_for_gallery = []

        def replace_image_tag(match):
            alt_text = match.group(1).strip()
            img_path_str = match.group(2).strip()
            logger.debug(
                f"Найдена ссылка на изображение: alt='{alt_text}', "
                f"path='{img_path_str}'"
            )

            clean_path_str = img_path_str
            if clean_path_str.startswith("images/"):
                clean_path_str = clean_path_str[len("images/"):]
            elif clean_path_str.startswith("report/output/images/"):
                clean_path_str = clean_path_str[len("report/output/images/"):]
            elif "report/output/images/" in clean_path_str:
                parts = clean_path_str.split("report/output/images/")
                if len(parts) > 1:
                    clean_path_str = parts[1]

            img_full_path = self.base_images_dir / clean_path_str
            data_url = self._image_to_base64(img_full_path)

            if data_url:
                logger.debug(f"Изображение встроено: {img_full_path}")
                return (
                    f'<p style="text-align: center;">'
                    f'<img src="{data_url}" alt="{alt_text}" '
                    f'style="max-width: 100%; height: auto;" />'
                    f'</p>'
                    f'<p style="text-align: center; font-size: 0.9em;">'
                    f'<em>{alt_text}</em></p>'
                )
            else:
                logger.warning(
                    f"Изображение не встроено, оставлен placeholder: {img_path_str}"
                )
                return (
                    f'<p style="text-align: center; font-style: italic;">'
                    f'[Изображение не найдено: {alt_text}]</p>'
                )

        pattern = r"!\[(.*?)\]\(([^)]+)\)"
        processed_content = re.sub(
            pattern, replace_image_tag, markdown_content, flags=re.DOTALL
        )
        return processed_content, images_found_for_gallery


# --- Функции LLM ---
def call_llm_for_qa(
        report_text: str, question: str, api_key: str, base_url: str, model: str
) -> str:
    """
    Вызывает LLM для ответа на вопрос по отчету.

    Args:
        report_text: Текст отчета.
        question: Вопрос пользователя.
        api_key: API ключ.
        base_url: Базовый URL.
        model: Модель для использования.

    Returns:
        Ответ от LLM.
    """
    if not OPENAI_AVAILABLE:
        return "❌ Библиотека 'openai' не установлена."

    if not api_key or not base_url or not model:
        return "❌ Необходимо заполнить все параметры API (ключ, URL, модель)."

    try:
        client = OpenAI(api_key=api_key, base_url=base_url.rstrip("/") + "/v1")
        prompt = f"""
Отчет:
{report_text}

Вопрос пользователя: {question}

Ответь на вопрос пользователя, используя ТОЛЬКО информацию из \
предоставленного выше отчета. 
Будь кратким и точным. Если информация в отчете отсутствует, честно скажи об этом.
"""
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=1024,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Ошибка вызова LLM: {e}")
        return f"❌ Ошибка при вызове LLM: {str(e)}"


def call_llm_to_determine_target(
        question: str, columns: List[str], api_key: str, base_url: str, model: str
) -> str:
    """
    Вызывает LLM для определения таргета на основе вопроса.

    Args:
        question: Вопрос пользователя.
        columns: Список колонок датасета.
        api_key: API ключ.
        base_url: Базовый URL.
        model: Модель для использования.

    Returns:
        Предполагаемый таргет.
    """
    if not OPENAI_AVAILABLE:
        return columns[0] if columns else ""

    if not api_key or not base_url or not model:
        return columns[0] if columns else ""

    try:
        client = OpenAI(api_key=api_key, base_url=base_url.rstrip("/") + "/v1")
        columns_str = "\n".join([f"- {col}" for col in columns])
        prompt = f"""
Ты помощник по анализу данных. Пользователь задал вопрос по датасету.
Тебе нужно определить, какая колонка в датасете является целевой переменной \
(таргетом) для анализа, основываясь на вопросе пользователя.

Список колонок в датасете:
{columns_str}

Вопрос пользователя: {question}

Ответь ТОЛЬКО названием одной колонки из списка, которая, по твоему мнению, 
является целевой переменной для ответа на этот вопрос. 
Если не уверен, выбери наиболее подходящую.

Название колонки:
"""
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=100,
        )
        target = response.choices[0].message.content.strip()
        if target in columns:
            return target
        else:
            return columns[0] if columns else ""
    except Exception as e:
        logger.error(f"Ошибка вызова LLM для определения таргета: {e}")
        return columns[0] if columns else ""


# --- Основная логика Gradio ---
def run_analysis(
        file_obj,
        api_key: str,
        base_url: str,
        model: str,
        question_for_target: str,
) -> Tuple[str, str, List, str, str]:
    """
    Запускает анализ датасета.

    Args:
        file_obj: Объект файла Gradio.
        api_key: API ключ.
        base_url: Базовый URL.
        model: Модель.
        question_for_target: Вопрос для определения таргета.

    Returns:
        Кортеж: (статус, путь_к_отчету, изображения, текст_отчета, история)
    """
    if not file_obj:
        return "❌ Файл не загружен.", "", [], "", ""

    if not question_for_target:
        return (
            "❌ Пожалуйста, задайте вопрос для автоматического определения таргета.",
            "", [], "", ""
        )

    try:
        df = pd.read_csv(file_obj.name)
        logger.info("✅ Загружен файл через Gradio UI.")

        binary_cols = [col for col in df.columns if df[col].nunique() == 2]
        if binary_cols:
            determined_target = call_llm_to_determine_target(
                question_for_target, binary_cols, api_key, base_url, model
            )
            if determined_target in binary_cols:
                target_col = determined_target
                logger.info(f"🎯 Таргет определен LLM: '{target_col}'")
            else:
                target_col = binary_cols[0]
                logger.info(
                    f"🎯 Таргет по умолчанию (первая бинарная): '{target_col}'"
                )
        else:
            target_col = find_binary_target(df)
            logger.info(f"🎯 Найден бинарный таргет: '{target_col}'")

        unique_vals = df[target_col].dropna().unique()
        if len(unique_vals) != 2:
            return (
                f"❌ Определенный столбец '{target_col}' не является бинарным. "
                f"Уникальные значения: {unique_vals}.",
                "", [], "", ""
            )

        with tempfile.NamedTemporaryFile(
                mode="w", delete=False, suffix=".csv", encoding="utf-8"
        ) as tmpfile:
            df.to_csv(tmpfile.name, index=False)
            tmp_path = tmpfile.name

        report_path, history, report_text = analyze_dataset(tmp_path, target_col)
        logger.info("✅ Анализ завершен.")

        os.unlink(tmp_path)

        processor = MarkdownImageProcessor()
        processed_markdown, images = processor.process_markdown(report_text)

        return (
            "✅ Анализ завершен!",
            report_path,
            images,
            report_text,
            str(history),
        )
    except Exception as e:
        logger.error(f"Ошибка в run_analysis: {e}")
        return f"❌ Ошибка: {str(e)}", "", [], "", ""


def answer_question(
        question: str, report_text: str, api_key: str, base_url: str, model: str
) -> str:
    """Отвечает на вопрос по отчету."""
    if not question:
        return "Пожалуйста, введите вопрос."
    if not report_text:
        return "Сначала необходимо выполнить анализ и получить отчет."

    logger.info(f"❓ Вопрос по отчету: {question}")
    answer = call_llm_for_qa(report_text, question, api_key, base_url, model)
    logger.info("✅ Ответ на вопрос получен.")
    return answer


def create_zip_with_images(report_text: str) -> Optional[str]:
    """Создает ZIP архив с изображениями из отчета."""
    if not report_text:
        return None

    try:
        pattern = r"!\[.*?\]\((.*?)\)"
        image_paths = re.findall(pattern, report_text)

        if not image_paths:
            return None

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            base_images_dir = Path("report/output/images")
            added_files = set()

            for img_path_str in image_paths:
                clean_path_str = img_path_str
                if clean_path_str.startswith("images/"):
                    clean_path_str = clean_path_str[len("images/"):]
                elif clean_path_str.startswith("report/output/images/"):
                    clean_path_str = clean_path_str[len("report/output/images/"):]
                elif "report/output/images/" in clean_path_str:
                    parts = clean_path_str.split("report/output/images/")
                    if len(parts) > 1:
                        clean_path_str = parts[1]

                img_full_path = base_images_dir / clean_path_str
                if img_full_path.exists() and img_full_path not in added_files:
                    arcname = Path(clean_path_str).name
                    zip_file.write(img_full_path, arcname)
                    added_files.add(img_full_path)

        zip_buffer.seek(0)

        with tempfile.NamedTemporaryFile(
                delete=False, suffix=".zip"
        ) as tmp_zip:
            tmp_zip.write(zip_buffer.getvalue())
            return tmp_zip.name
    except Exception as e:
        logger.error(f"Ошибка создания ZIP с изображениями: {e}")
        return None


def fetch_models(api_key: str, base_url: str):
    """Получает список моделей от API."""
    if not api_key or not base_url:
        return gr.update(choices=[], value="", interactive=True)
    try:
        client = OpenAI(api_key=api_key, base_url=base_url.rstrip("/") + "/v1")
        models_response = client.models.list()
        model_ids = sorted([model.id for model in models_response.data])
        return gr.update(
            choices=model_ids,
            value=model_ids[0] if model_ids else "",
            interactive=True,
        )
    except Exception as e:
        logger.error(f"Ошибка получения моделей: {e}")
        return gr.update(choices=[], value="", interactive=True)


def save_api_settings(api_key: str, base_url: str, model: str) -> str:
    """Сохраняет настройки API в .env файл."""
    try:
        with open(".env", "w", encoding="utf-8") as f:
            f.write(f"OPENAI_API_KEY={api_key}\n")
            f.write(f"OPENAI_BASE_URL={base_url}\n")
            f.write(f"OPENAI_MODEL={model}\n")

        os.environ["OPENAI_API_KEY"] = api_key
        os.environ["OPENAI_BASE_URL"] = base_url
        os.environ["OPENAI_MODEL"] = model

        logger.info("✅ Настройки API сохранены в .env")
        return "✅ Настройки API успешно сохранены!"
    except Exception as e:
        logger.error(f"Ошибка сохранения настроек API: {e}")
        return f"❌ Ошибка сохранения настроек: {str(e)}"


# --- Gradio Интерфейс ---
def build_interface():
    """Создает Gradio интерфейс."""
    with gr.Blocks(title="InsightFinder") as demo:
        gr.Markdown("# InsightFinder — AI агент для анализа данных")
        # gr.Image("insightFinderLogo.png", elem_id="logo", show_label=False,
        # container=False, height=100)

        report_text_state = gr.State("")
        history_state = gr.State("")

        with gr.Tab("Анализ"):
            with gr.Row():
                with gr.Column(scale=1):
                    file_input = gr.File(
                        label="📁 Загрузите CSV-файл", file_types=[".csv"]
                    )

                    with gr.Accordion("⚙️ Настройки API", open=True):
                        api_key_input = gr.Textbox(
                            label="OPENAI_API_KEY",
                            type="password",
                            value=os.getenv("OPENAI_API_KEY", ""),
                        )
                        base_url_input = gr.Textbox(
                            label="OPENAI_BASE_URL",
                            value=os.getenv(
                                "OPENAI_BASE_URL",
                                "https://openai-hub.neuraldeep.tech  "
                            ).strip(),
                        )

                        fetch_models_btn = gr.Button("🔄 Получить список моделей")

                        if OPENAI_AVAILABLE:
                            initial_models = []
                            initial_model = os.getenv(
                                "OPENAI_MODEL", "qwen2.5-32b-instruct"
                            )
                            try:
                                client = OpenAI(
                                    api_key=os.getenv("OPENAI_API_KEY", ""),
                                    base_url=os.getenv(
                                        "OPENAI_BASE_URL",
                                        "https://openai-hub.neuraldeep.tech  "
                                    ).rstrip("/") + "/v1",
                                )
                                models_response = client.models.list()
                                initial_models = sorted(
                                    [model.id for model in models_response.data]
                                )
                                if (initial_model not in initial_models and
                                        initial_models):
                                    initial_model = initial_models[0]
                            except Exception as e:
                                logger.debug(f"Не удалось получить модели: {e}")

                            model_dropdown = gr.Dropdown(
                                choices=initial_models,
                                value=initial_model,
                                label="OPENAI_MODEL",
                                interactive=True,
                            )
                        else:
                            model_input = gr.Textbox(
                                label="OPENAI_MODEL",
                                value=os.getenv(
                                    "OPENAI_MODEL", "qwen2.5-32b-instruct"
                                ),
                            )

                        save_settings_btn = gr.Button("💾 Сохранить настройки")
                        settings_status = gr.Textbox(
                            label="", interactive=False, visible=False
                        )

                    question_for_target_input = gr.Textbox(
                        label="❓ Задайте вопрос для автоматического "
                              "определения таргета",
                        placeholder="Например: Какие факторы влияют на отток "
                                    "клиентов?",
                    )

                    run_btn = gr.Button("🚀 Запустить анализ", variant="primary")

                with gr.Column(scale=2):
                    status_output = gr.Textbox(label="Статус", interactive=False)
                    report_markdown = gr.Markdown(
                        label="📑 Итоговый отчёт", visible=False
                    )
                    images_gallery = gr.Gallery(
                        label="📊 Графики",
                        columns=2,
                        height="auto",
                        object_fit="contain",
                        visible=False,
                    )

                    with gr.Row(visible=False) as download_row:
                        report_download = gr.File(label="📥 Скачать отчёт (.md)")
                        images_zip_download = gr.File(
                            label="📥 Скачать графики (.zip)"
                        )

                    with gr.Group(visible=False) as qa_section:
                        gr.Markdown("### Задать вопрос по отчету")

                        question_input = gr.Textbox(
                            label="Ваш вопрос",
                            placeholder="Введите свой вопрос",
                        )
                        ask_btn = gr.Button("Получить ответ")
                        answer_output = gr.Textbox(
                            label="Ответ", interactive=False, lines=5
                        )

        # --- Обработчики событий ---
        fetch_models_btn.click(
            fetch_models,
            inputs=[api_key_input, base_url_input],
            outputs=[model_dropdown if OPENAI_AVAILABLE else model_input],
        )

        def save_and_show_status(api_key, base_url, model):
            status_message = save_api_settings(api_key, base_url, model)
            return status_message, gr.update(visible=True)

        def hide_status():
            return gr.update(visible=False)

        save_settings_btn.click(
            save_and_show_status,
            inputs=[
                api_key_input,
                base_url_input,
                model_dropdown if OPENAI_AVAILABLE else model_input,
            ],
            outputs=[settings_status, settings_status],
        ).then(
            hide_status,
            None,
            settings_status,
            queue=False,
        )

        def on_run_analysis(file_obj, api_key, base_url, model, question_for_target):
            (
                status,
                report_path,
                images,
                report_text,
                history,
            ) = run_analysis(
                file_obj, api_key, base_url, model, question_for_target
            )

            zip_path = create_zip_with_images(report_text)

            report_visible = bool(report_text)
            images_visible = bool(images)
            download_visible = bool(report_path or zip_path)
            qa_visible = bool(report_text)

            return (
                status,
                report_text if report_text else "Отчет не сгенерирован.",
                gr.update(visible=report_visible),
                images,
                gr.update(visible=images_visible),
                report_path if report_path and os.path.exists(
                    report_path) else None,
                zip_path if zip_path and os.path.exists(zip_path) else None,
                gr.update(visible=download_visible),
                gr.update(visible=qa_visible),
                report_text,
                history,
            )

        run_btn.click(
            on_run_analysis,
            inputs=[
                file_input,
                api_key_input,
                base_url_input,
                model_dropdown if OPENAI_AVAILABLE else model_input,
                question_for_target_input,
            ],
            outputs=[
                status_output,
                report_markdown,
                report_markdown,
                images_gallery,
                images_gallery,
                report_download,
                images_zip_download,
                download_row,
                qa_section,
                report_text_state,
                history_state,
            ],
        )

        def on_ask_question(question, report_text, api_key, base_url, model):
            answer = answer_question(question, report_text, api_key, base_url, model)
            return answer

        ask_btn.click(
            on_ask_question,
            inputs=[
                question_input,
                report_text_state,
                api_key_input,
                base_url_input,
                model_dropdown if OPENAI_AVAILABLE else model_input,
            ],
            outputs=[answer_output],
        )

    return demo


# --- Точка входа ---
if __name__ == "__main__":
    Path("tmp").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    Path("report/output/images").mkdir(parents=True, exist_ok=True)

    demo = build_interface()
    demo.launch(server_name="0.0.0.0", server_port=8502)