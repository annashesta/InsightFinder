# web_app.py

import streamlit as st
import pandas as pd
from core.pipeline import analyze_dataset
import os
import glob
import base64
import io
import zipfile
from core.logger import get_logger

logger = get_logger(__name__, "orchestrator.log")


st.markdown(
    """
    <style>
    @media print {
        /* Применяется только при печати/сохранлении в PDF */
        
        /* Предотвращаем разрывы страниц внутри изображений и их подписей */
        .element-container:has(> img), /* Контейнер изображения Streamlit */
        .stImage, /* Класс изображения Streamlit */
        .stImage + div { /* Контейнер подписи, если он есть */ 
             /* orphans и widows - стандартные CSS свойства для печати */
            orphans: 2; /* Минимум 2 линии текста/элемента до разрыва */
            widows: 2;  /* Минимум 2 линии текста/элемента после разрыва */
            
            /* page-break-inside - устарело, но поддерживается лучше в некоторых браузерах */
            page-break-inside: avoid; 
            /* break-inside - современный стандарт */
            break-inside: avoid;
        }

        /* Дополнительно: можно немного уменьшить изображения для печати, если они велики */
        /* .stImage img { max-width: 95%; } */
        
        /* Дополнительно: убедиться, что подписи остаются с изображением */
        /* .stImage + div { page-break-before: avoid; break-before: avoid; } */
    }
    </style>
    """,
    unsafe_allow_html=True
)


try:
    st.image("insightFinderLogo.png", width=600)
except Exception as e:
    # Если файл не найден, просто продолжаем
    logger.debug(f"Логотип не найден или не может быть загружен: {e}")
    # st.title("InsightFinder — AI агент для анализа данных")

# Основной заголовок
st.title("InsightFinder — AI агент для анализа данных")

def clear_tmp_directory():
    """Очищает временную директорию tmp"""
    try:
        tmp_dir = "tmp"
        if os.path.exists(tmp_dir):
            for file in os.listdir(tmp_dir):
                file_path = os.path.join(tmp_dir, file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    st.error(f"Ошибка при удалении {file_path}: {e}")
    except Exception as e:
        st.error(f"Ошибка при очистке tmp: {e}")


st.subheader("⚙️ Настройки API")
st.write("Важно: неверный или отсутствующий ключ приведёт к ошибкам.")
with st.form("env_form"):
    api_key = st.text_input("Введите OPENAI_API_KEY", type="password")
    base_url = st.text_input("Введите OPENAI_BASE_URL", value="https://openai-hub.neuraldeep.tech  ")
    model_name = st.text_input("Введите OPENAI_MODEL", value="qwen2.5-32b-instruct") # Значение по умолчанию

    submitted = st.form_submit_button("Сохранить настройки")

    if submitted:
        with open(".env", "w", encoding="utf-8") as f:
            f.write(f"OPENAI_API_KEY={api_key}\n")
            f.write(f"OPENAI_BASE_URL={base_url}\n")
            f.write(f"OPENAI_MODEL={model_name}\n")
        
        st.success("✅ Файл .env успешно создан!")
        logger.info("✅ Установлены новые переменные окружения (API и MODEL) из формы.")

        # чтобы сразу подхватить в текущем приложении
        os.environ["OPENAI_API_KEY"] = api_key
        os.environ["OPENAI_BASE_URL"] = base_url
        os.environ["OPENAI_MODEL"] = model_name


file = st.file_uploader("Загрузите CSV-файл", type=["csv"])

st.write("Важно: не пытайтесь изменить файл или таргет, пока идёт текущий анализ. Это может привести к ошибкам.")
if file:
    logger.info("✅ Загружен файл через веб-интерфейс.")
    df = pd.read_csv(file)
    st.write("Предпросмотр:", df.head())

    target_col = st.selectbox("Выберите таргет", sorted(df.columns))
    
    st.write("Важно: не пытайтесь начать новый анализ, пока идёт текущий. Это может привести к ошибкам.")
    
    def is_binary_column(series):
        """Проверяет, является ли серия бинарной (содержит только 2 уникальных значения)."""
        try:
            # Удаляем NaN, если они есть
            unique_values = series.dropna().unique()
            # Проверяем, что уникальных значений ровно 2
            if len(unique_values) != 2:
                return False, []
            
            # Дополнительно можно проверить, являются ли значения 0/1, True/False, Yes/No и т.п.
            # Но для простоты ограничимся количеством уникальных значений.
            return True, unique_values.tolist()
        except Exception:
            return False, []

    if st.button("Запустить анализ"):
        # Проверка на бинарность
        is_binary, unique_vals = is_binary_column(df[target_col])
        if not is_binary:
            st.error(f"❌ Выбранный столбец '{target_col}' не является бинарным. "
                     f"Пожалуйста, выберите столбец с ровно двумя уникальными значениями.")
            logger.warning(f"❌ Попытка запуска анализа с не бинарным таргетом '{target_col}'. "
                          f"Уникальные значения: {unique_vals}")
        else:
            # Если таргет бинарный, продолжаем анализ 
            os.makedirs("tmp", exist_ok=True)
            tmp_path = os.path.join("tmp", file.name)

            with open(tmp_path, "wb") as f:
                f.write(file.getbuffer())

            # создаём "плейсхолдер" для статуса
            status_placeholder = st.empty()
            status_placeholder.info("⏳ Анализ запущен...")

            try:
                report_path, history, report = analyze_dataset(tmp_path, target_col)

                # сохраняем в сессию
                st.session_state["report"] = report
                st.session_state["report_path"] = report_path
                st.session_state["history"] = history

            finally:
                status_placeholder.empty()
                # Очищаем временную директорию после завершения
                clear_tmp_directory()
                logger.info("✅ Временная директория tmp очищена.")


# показываем отчет и кнопку скачивания, если они есть
if "report" in st.session_state:
    st.markdown(st.session_state["report"], unsafe_allow_html=True)
    
    image_paths = [] # Инициализируем список заранее

    # Визуализации, если они есть
    if "history" in st.session_state:
        image_paths = []
    
        # инструмент DistributionVisualizer
        for step in st.session_state["history"]:
            if step["tool_name"] == "DistributionVisualizer" and step["status"] == "success":
                visualizations = step["details"].get("visualizations", {})
                if visualizations:
                    st.subheader("📊 Визуализации распределений")
                    for feature, viz in visualizations.items():
                        st.markdown(f"**{feature}** — {viz['description']}")
                        img_bytes = base64.b64decode(viz["image_base64"])
                    
                        # Сохраняем во временный файл для ZIP
                        temp_path = os.path.join("tmp", f"distribution_{feature}.png")
                        with open(temp_path, 'wb') as f:
                            f.write(img_bytes)
                        image_paths.append(temp_path)
                    
                        # Отображаем изображение
                        st.image(img_bytes, use_container_width=True)

        # Логика для InsightDrivenVisualizer
        for step in st.session_state["history"]:
            if step["tool_name"] == "InsightDrivenVisualizer" and step["status"] == "success":
                saved_plots = step["details"].get("saved_plots", {})
                if saved_plots:
                    st.subheader("💡 Инсайт-визуализации")
                
                    images_dir = "report/output/images/"
                    if os.path.exists(images_dir):
                        # Сначала соберем все пути к изображениям и их "родительские" ключи из details
                        plot_info_map = {}
                        for feature_key, plot_data in saved_plots.items():
                             for plot_type_key, file_path in plot_data.items():
                                 if plot_type_key != "description" and isinstance(file_path, str) and os.path.exists(file_path):
                                     # Используем нормализованный путь как ключ для сопоставления
                                     normalized_path = os.path.normpath(file_path)
                                     plot_info_map[normalized_path] = {
                                         "feature": feature_key,
                                         "type": plot_type_key,
                                         "description": plot_data.get("description", "")
                                     }
                        for root, dirs, files in os.walk(images_dir):
                            for file in files:
                                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                                    img_path = os.path.join(root, file)
                                    image_paths.append(img_path)
                                    
                                    # Формируем подпись
                                    caption_parts = [file] # По умолчанию имя файла
                                    norm_img_path = os.path.normpath(img_path)
                                    if norm_img_path in plot_info_map:
                                        info = plot_info_map[norm_img_path]
                                        # Пример подписи: "desc_MonthlyRevenue_hist.png - Визуализация для MonthlyRevenue из DescriptiveStatsComparator (Гистограмма)"
                                        detailed_caption = f"{file} - {info['description']} ({info['type']})"
                                        caption_parts = [detailed_caption]
                                        
                                    # Отображаем изображение
                                    st.image(img_path, caption=" | ".join(caption_parts), use_container_width=True)

    st.subheader("📑 Итоговый отчёт")
    with open(st.session_state["report_path"], "r", encoding="utf-8") as f:
        st.download_button(
            label="📥 Скачать отчёт (.md)",
            data=f.read(),
            file_name=os.path.basename(st.session_state["report_path"]),
            mime="text/markdown"
        )
        
    # Создаем ZIP-архив со всеми графиками
    if image_paths:
        # Убираем дубликаты, если они есть
        image_paths = list(set(image_paths)) 
        st.markdown(f"### 📥 Всего графиков: {len(image_paths)}")
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for img_path in image_paths:
                # Имя файла в архиве без полного пути
                arcname = os.path.relpath(img_path, "report/output") 
                # Убедимся, что файл существует перед добавлением
                if os.path.exists(img_path):
                     zip_file.write(img_path, arcname)
                else:
                     logger.warning(f"Файл изображения не найден при создании ZIP: {img_path}")
    
        zip_buffer.seek(0)
        st.download_button(
            label="📥 Скачать все графики (.zip)",
            data=zip_buffer,
            file_name="visualizations.zip",
            mime="application/zip"
        )

    st.subheader("📜 Логи агентов")

    log_files = glob.glob("logs/*.log")

    if log_files:
        for log_file in log_files:
            with open(log_file, "r", encoding="utf-8") as f:
                st.download_button(
                    label=f"📥 Скачать {os.path.basename(log_file)}",
                    data=f.read(),
                    file_name=os.path.basename(log_file),
                    mime="text/plain"
                )
    logger.info("✅ Выведен финальный отчет")