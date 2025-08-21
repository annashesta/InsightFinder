# web_app.py

import streamlit as st
import pandas as pd
from core.pipeline import analyze_dataset
import os
import glob
import base64
import io

st.title("InsightFinder — AI агент для анализа данных")

file = st.file_uploader("Загрузите CSV-файл", type=["csv"])
if file:
    df = pd.read_csv(file)
    st.write("Предпросмотр:", df.head())

    target_col = st.selectbox("Выберите таргет", df.columns)

    if st.button("Запустить анализ"):
        os.makedirs("tmp", exist_ok=True)
        tmp_path = os.path.join("tmp", file.name)

        with open(tmp_path, "wb") as f:
            f.write(file.getbuffer())

        # создаём "плейсхолдер" для статуса
        status_placeholder = st.empty()
        status_placeholder.info("⏳ Анализ запущен...")

        report_path, history, report = analyze_dataset(tmp_path, target_col)

        status_placeholder.empty()

        # сохраняем в сессию
        st.session_state["report"] = report
        st.session_state["report_path"] = report_path
        st.session_state["history"] = history


# Визуализации, если они есть
if "history" in st.session_state:
    for step in st.session_state["history"]:
        if step["tool_name"] == "DistributionVisualizer" and step["status"] == "success":
            visualizations = step["details"].get("visualizations", {})
            if visualizations:
                st.subheader("📊 Визуализации распределений")
                for feature, viz in visualizations.items():
                    st.markdown(f"**{feature}** — {viz['description']}")
                    # декодируем Base64 в байты
                    img_bytes = base64.b64decode(viz["image_base64"])
                    st.image(io.BytesIO(img_bytes), use_container_width=True)



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