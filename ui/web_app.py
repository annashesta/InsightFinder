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

def clear_tmp_directory():
    """Очищает временную директорию tmp"""
    try:
        for file in os.listdir("tmp"):
            file_path = os.path.join("tmp", file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                st.error(f"Ошибка при удалении {file_path}: {e}")
    except Exception as e:
        st.error(f"Ошибка при очистке tmp: {e}")


st.title("InsightFinder — AI агент для анализа данных")

st.subheader("⚙️ Настройки API")
st.write("Важно: неверный или отсутствующий ключ приведёт к ошибкам.")
with st.form("env_form"):
    api_key = st.text_input("Введите OPENAI_API_KEY", type="password")
    base_url = st.text_input("Введите OPENAI_BASE_URL", value="https://openai-hub.neuraldeep.tech")

    submitted = st.form_submit_button("Сохранить настройки")

    if submitted:
        with open(".env", "w", encoding="utf-8") as f:
            f.write(f"OPENAI_API_KEY={api_key}\n")
            f.write(f"OPENAI_BASE_URL={base_url}\n")
        
        st.success("✅ Файл .env успешно создан!")
        logger.info("✅ Установлены новые переменные окружения (API) из формы.")

        # чтобы сразу подхватить в текущем приложении
        os.environ["OPENAI_API_KEY"] = api_key
        os.environ["OPENAI_BASE_URL"] = base_url



file = st.file_uploader("Загрузите CSV-файл", type=["csv"])

st.write("Важно: не пытайтесь изменить файл или таргет, пока идёт текущий анализ. Это может привести к ошибкам.")
if file:
    logger.info("✅ Загружен файл через веб-интерфейс.")
    df = pd.read_csv(file)
    st.write("Предпросмотр:", df.head())

    target_col = st.selectbox("Выберите таргет", df.columns)
    
    st.write("Важно: не пытайтесь начать новый анализ, пока идёт текущий. Это может привести к ошибкам.")
    if st.button("Запустить анализ"):
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
    st.subheader("📑 Итоговый отчёт")
    st.markdown(st.session_state["report"], unsafe_allow_html=True)

    with open(st.session_state["report_path"], "r", encoding="utf-8") as f:
        st.download_button(
            label="📥 Скачать отчёт (.md)",
            data=f.read(),
            file_name=os.path.basename(st.session_state["report_path"]),
            mime="text/markdown"
        )
    # Визуализации, если они есть
    if "history" in st.session_state:
        image_paths = []
    
        # инструмент DistributionVisualizer и InsightDrivenVisualizer
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

        for step in st.session_state["history"]:
            if step["tool_name"] == "InsightDrivenVisualizer" and step["status"] == "success":
                saved_plots = step["details"].get("saved_plots", {})
                if saved_plots:
                    st.subheader("💡 Инсайт-визуализации")
                
                    for feature, plot_info in saved_plots.items():
                        st.markdown(f"### {feature}")
                        st.markdown(plot_info.get("description", ""))
                    
                        # Обработка различных типов графиков
                        for plot_type, path in plot_info.items():
                            if plot_type != "description":  # Пропускаем поле description
                                if isinstance(path, str) and os.path.exists(path):
                                    image_paths.append(path)
                                    with open(path, 'rb') as img_file:
                                        image_bytes = img_file.read()
                                        st.image(image_bytes, use_container_width=True)

    # Создаем ZIP-архив со всеми графиками
        if image_paths:
            st.markdown(f"### 📥 Всего графиков: {len(image_paths)}")
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                for img_path in image_paths:
                    filename = os.path.basename(img_path)
                    zip_file.write(img_path, filename)
        
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