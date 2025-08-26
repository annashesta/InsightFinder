# # web_app.py резервный UI

# import streamlit as st
# import pandas as pd
# from core.pipeline import analyze_dataset
# import os
# import glob
# import base64
# import io
# import zipfile
# from core.logger import get_logger
# from pathlib import Path

# try:
#     from openai import OpenAI
#     OPENAI_AVAILABLE = True
# except ImportError:
#     OPENAI_AVAILABLE = False
#     st.warning("Библиотека 'openai' не установлена. Установите её для функции выбора модели: `pip install openai`")


# logger = get_logger(__name__, "orchestrator.log")


# # CSS для улучшения печати и центрирования логотипа
# st.markdown(
#     """
#     <style>
#     /* Центрирование логотипа */
#     .logo-container {
#         display: flex;
#         justify-content: center;
#         width: 100%;
#         margin-bottom: 1rem;
#     }
    
#     @media print {
#         /* Применяется только при печати/сохранении в PDF */
        
#         /* Предотвращаем разрывы страниц внутри изображений и их подписей */
#         .element-container:has(> img), /* Контейнер изображения Streamlit */
#         .stImage, /* Класс изображения Streamlit */
#         .stImage + div { /* Контейнер подписи, если он есть */ 
#              /* orphans и widows - стандартные CSS свойства для печати */
#             orphans: 2; /* Минимум 2 линии текста/элемента до разрыва */
#             widows: 2;  /* Минимум 2 линии текста/элемента после разрыва */
            
#             /* page-break-inside - устарело, но поддерживается лучше в некоторых браузерах */
#             page-break-inside: avoid; 
#             /* break-inside - современный стандарт */
#             break-inside: avoid;
#         }

#         /* Дополнительно: можно немного уменьшить изображения для печати, если они велики */
#         /* .stImage img { max-width: 90%; } */
        
#         /* Дополнительно: убедиться, что подписи остаются с изображением */
#         /* .stImage + div { page-break-before: avoid; break-before: avoid; } */
#     }
#     </style>
#     """,
#     unsafe_allow_html=True
# )



# st.markdown('<div class="logo-container">', unsafe_allow_html=True)
# st.image("insightFinderLogo.png", width=600)
# st.markdown('</div>', unsafe_allow_html=True)
# st.title("InsightFinder — AI агент для анализа данных")
# # Основной заголовок

# def clear_tmp_directory():
#     """Очищает временную директорию tmp"""
#     try:
#         tmp_dir = "tmp"
#         if os.path.exists(tmp_dir):
#             for file in os.listdir(tmp_dir):
#                 file_path = os.path.join(tmp_dir, file)
#                 try:
#                     if os.path.isfile(file_path):
#                         os.unlink(file_path)
#                 except Exception as e:
#                     st.error(f"Ошибка при удалении {file_path}: {e}")
#     except Exception as e:
#         st.error(f"Ошибка при очистке tmp: {e}")



# st.subheader("⚙️ Настройки API")
# st.write("Важно: неверный или отсутствующий ключ приведёт к ошибкам.")

# # ИЗМЕНЕНО: Используем session_state для хранения временных значений
# # Инициализируем session_state один раз в начале скрипта или здесь, если ещё не инициализирован
# if "available_models" not in st.session_state:
#     st.session_state["available_models"] = []
# if "selected_model" not in st.session_state:
#     # Используем значение из .env или значение по умолчанию
#     st.session_state["selected_model"] = os.getenv("OPENAI_MODEL", "qwen2.5-32b-instruct")
# # Также храним API ключ и URL в session_state для доступа внутри формы
# if "tmp_api_key" not in st.session_state:
#     st.session_state["tmp_api_key"] = os.getenv("OPENAI_API_KEY", "")
# if "tmp_base_url" not in st.session_state:
#     st.session_state["tmp_base_url"] = os.getenv("OPENAI_BASE_URL", "https://openai-hub.neuraldeep.tech")

# with st.form("env_form"):
#     api_key = st.text_input(
#         "Введите OPENAI_API_KEY", 
#         type="password", 
#         key="api_key_input",
#         value=st.session_state["tmp_api_key"] # Используем значение из session_state
#     )
#     # Обновляем session_state при каждом изменении
#     st.session_state["tmp_api_key"] = api_key 

#     base_url = st.text_input(
#         "Введите OPENAI_BASE_URL", 
#         value=st.session_state["tmp_base_url"], # Используем значение из session_state
#         key="base_url_input"
#     )
#     # Обновляем session_state при каждом изменении
#     st.session_state["tmp_base_url"] = base_url

#     # Кнопка внутри формы, но не является Submit кнопкой
#     fetch_models_clicked = st.form_submit_button("🔄 Получить список моделей")
    
#     # Логика получения моделей внутри формы
#     if fetch_models_clicked:
#         if not api_key or not base_url:
#              st.error("❌ Пожалуйста, введите API ключ и URL.")
#         else:
#             if OPENAI_AVAILABLE:
#                 try:
#                     # Используем значения напрямую из виджетов внутри формы
#                     client = OpenAI(api_key=api_key, base_url=base_url.rstrip('/') + "/v1")
#                     models_response = client.models.list()
#                     model_ids = [model.id for model in models_response.data]
#                     if model_ids:
#                         st.session_state["available_models"] = sorted(model_ids)
#                         # Если текущая выбранная модель не в списке, сбрасываем
#                         if st.session_state["selected_model"] not in model_ids:
#                             st.session_state["selected_model"] = model_ids[0]
#                         st.success(f"✅ Получен список из {len(model_ids)} моделей.")
#                         # st.rerun() внутри формы может быть нестабильным, 
#                         # поэтому обновляем UI на следующей итерации
#                     else:
#                         st.warning("⚠️ Список моделей пуст.")
#                 except Exception as e:
#                     st.error(f"❌ Ошибка при получении списка моделей: {e}")
#             else:
#                 st.error("❌ Библиотека 'openai' не установлена.")

#     # Поле выбора модели из списка или поле ввода, если список пуст/еще не загружен
#     if st.session_state["available_models"]:
#         # Если список моделей загружен, показываем selectbox
#         selected_model = st.selectbox(
#             "Выберите OPENAI_MODEL",
#             options=st.session_state["available_models"],
#             index=st.session_state["available_models"].index(st.session_state["selected_model"]) if st.session_state["selected_model"] in st.session_state["available_models"] else 0,
#             key="model_selectbox"
#         )
#         # Обновляем session_state при выборе
#         st.session_state["selected_model"] = selected_model
#     else:
#         # Если список еще не загружен, показываем text_input
#         selected_model = st.text_input(
#             "Введите OPENAI_MODEL", 
#             value=st.session_state["selected_model"], 
#             key="model_text_input"
#         )
#         # Обновляем session_state при вводе
#         st.session_state["selected_model"] = selected_model

#     submitted = st.form_submit_button("💾 Сохранить настройки")

#     if submitted:
#         # Сохраняем выбранную модель из selectbox/text_input
#         model_to_save = selected_model
        
#         with open(".env", "w", encoding="utf-8") as f:
#             f.write(f"OPENAI_API_KEY={api_key}\n")
#             f.write(f"OPENAI_BASE_URL={base_url}\n")
#             f.write(f"OPENAI_MODEL={model_to_save}\n") # Используем выбранную модель
        
#         st.success("✅ Файл .env успешно создан!")
#         logger.info("✅ Установлены новые переменные окружения (API и MODEL) из формы.")

#         # чтобы сразу подхватить в текущем приложении
#         os.environ["OPENAI_API_KEY"] = api_key
#         os.environ["OPENAI_BASE_URL"] = base_url
#         os.environ["OPENAI_MODEL"] = model_to_save # Используем выбранную модель


# file = st.file_uploader("Загрузите CSV-файл", type=["csv"])

# st.write("Важно: не пытайтесь изменить файл или таргет, пока идёт текущий анализ. Это может привести к ошибкам.")
# if file:
#     logger.info("✅ Загружен файл через веб-интерфейс.")
#     df = pd.read_csv(file)
#     st.write("Предпросмотр:", df.head())

#     target_col = st.selectbox("Выберите таргет", sorted(df.columns))
    
#     st.write("Важно: не пытайтесь начать новый анализ, пока идёт текущий. Это может привести к ошибкам.")
    
#     def is_binary_column(series):
#         """Проверяет, является ли серия бинарной (содержит только 2 уникальных значения)."""
#         try:
#             # Удаляем NaN, если они есть
#             unique_values = series.dropna().unique()
#             # Проверяем, что уникальных значений ровно 2
#             if len(unique_values) != 2:
#                 return False, []
            
#             # Дополнительно можно проверить, являются ли значения 0/1, True/False, Yes/No и т.п.
#             # Но для простоты ограничимся количеством уникальных значений.
#             return True, unique_values.tolist()
#         except Exception:
#             return False, []

#     if st.button("Запустить анализ"):
#         # Проверка на бинарность
#         is_binary, unique_vals = is_binary_column(df[target_col])
#         if not is_binary:
#             st.error(f"❌ Выбранный столбец '{target_col}' не является бинарным. "
#                      f"Пожалуйста, выберите столбец с ровно двумя уникальными значениями.")
#             logger.warning(f"❌ Попытка запуска анализа с не бинарным таргетом '{target_col}'. "
#                           f"Уникальные значения: {unique_vals}")
#         else:
#             # Если таргет бинарный, продолжаем анализ 
#             os.makedirs("tmp", exist_ok=True)
#             tmp_path = os.path.join("tmp", file.name)

#             with open(tmp_path, "wb") as f:
#                 f.write(file.getbuffer())

#             # создаём "плейсхолдер" для статуса
#             status_placeholder = st.empty()
#             status_placeholder.info("⏳ Анализ запущен...")

#             try:
#                 report_path, history, report = analyze_dataset(tmp_path, target_col)

#                 # сохраняем в сессию
#                 st.session_state["report"] = report
#                 st.session_state["report_path"] = report_path
#                 st.session_state["history"] = history

#             finally:
#                 status_placeholder.empty()
#                 # Очищаем временную директорию после завершения
#                 clear_tmp_directory()
#                 logger.info("✅ Временная директория tmp очищена.")


# def display_markdown_report(report_path, images_dir="report/output/images"):
#     """Отображает Markdown отчет с встроенными изображениями"""
#     try:
#         # Чтение отчета
#         with open(report_path, "r", encoding="utf-8") as f:
#             report_content = f.read()
        
#         # Функция для преобразования изображений
#         def embed_images(match):
#             alt_text = match.group(1)
#             img_filename = match.group(2)
            
#             # Поиск полного пути к изображению
#             img_path = None
#             for root, dirs, files in os.walk(images_dir):
#                 if img_filename in files:
#                     img_path = os.path.join(root, img_filename)
#                     break
            
#             if img_path and os.path.exists(img_path):
#                 try:
#                     with open(img_path, "rb") as img_file:
#                         img_base64 = base64.b64encode(img_file.read()).decode()
#                     return f'![{alt_text}](data:image/png;base64,{img_base64})'
#                 except Exception as e:
#                     st.warning(f"Ошибка загрузки {img_path}: {e}")
            
#             return match.group(0)  # Оригинальная строка если изображение не найдено
        
#         # Обработка изображений
#         import re
#         pattern = r'!\[(.*?)\]\(([^)]+)\)'
#         processed_content = re.sub(pattern, embed_images, report_content)
        
#         # Отображение
#         st.markdown(processed_content, unsafe_allow_html=True)
        
#     except Exception as e:
#         st.error(f"Ошибка при отображении отчета: {e}")
        
# # показываем отчет и кнопку скачивания, если они есть
# if "report_path" in st.session_state:
#     st.subheader("📑 Итоговый отчёт с графиками")
#     display_markdown_report(st.session_state["report_path"], images_dir="report/output/images")

#     image_paths = [] # Инициализируем список заранее

#     # Визуализации, если они есть
#     if "history" in st.session_state:
#         image_paths = []
    
#         # инструмент DistributionVisualizer
#         for step in st.session_state["history"]:
#             if step["tool_name"] == "DistributionVisualizer" and step["status"] == "success":
#                 visualizations = step["details"].get("visualizations", {})
#                 if visualizations:
#                     st.subheader("📊 Визуализации распределений")
#                     for feature, viz in visualizations.items():
#                         st.markdown(f"**{feature}** — {viz['description']}")
#                         img_bytes = base64.b64decode(viz["image_base64"])
                    
#                         # Сохраняем во временный файл для ZIP
#                         temp_path = os.path.join("tmp", f"distribution_{feature}.png")
#                         with open(temp_path, 'wb') as f:
#                             f.write(img_bytes)
#                         image_paths.append(temp_path)
                    
#                         # Отображаем изображение
#                         st.image(img_bytes, use_container_width=True)

#         # Логика для InsightDrivenVisualizer
#         for step in st.session_state["history"]:
#             if step["tool_name"] == "InsightDrivenVisualizer" and step["status"] == "success":
#                 saved_plots = step["details"].get("saved_plots", {})
#                 if saved_plots:
#                     st.subheader("💡 Инсайт-визуализации")
                
#                     images_dir = "report/output/images/"
#                     if os.path.exists(images_dir):
#                         # Сначала соберем все пути к изображениям и их "родительские" ключи из details
#                         plot_info_map = {}
#                         for feature_key, plot_data in saved_plots.items():
#                              for plot_type_key, file_path in plot_data.items():
#                                  if plot_type_key != "description" and isinstance(file_path, str) and os.path.exists(file_path):
#                                      # Используем нормализованный путь как ключ для сопоставления
#                                      normalized_path = os.path.normpath(file_path)
#                                      plot_info_map[normalized_path] = {
#                                          "feature": feature_key,
#                                          "type": plot_type_key,
#                                          "description": plot_data.get("description", "")
#                                      }
#                         for root, dirs, files in os.walk(images_dir):
#                             for file in files:
#                                 if file.lower().endswith(('.png', '.jpg', '.jpeg')):
#                                     img_path = os.path.join(root, file)
#                                     image_paths.append(img_path)
                                    
#                                     # Формируем подпись
#                                     caption_parts = [file] # По умолчанию имя файла
#                                     norm_img_path = os.path.normpath(img_path)
#                                     if norm_img_path in plot_info_map:
#                                         info = plot_info_map[norm_img_path]
#                                         # Пример подписи: "desc_MonthlyRevenue_hist.png - Визуализация для MonthlyRevenue из DescriptiveStatsComparator (Гистограмма)"
#                                         detailed_caption = f"{file} - {info['description']} ({info['type']})"
#                                         caption_parts = [detailed_caption]
                                        
#                                     # Отображаем изображение
#                                     st.image(img_path, caption=" | ".join(caption_parts), use_container_width=True)

#     # Кнопка скачивания отчета 
#     st.subheader("📥 Скачать отчёт")
#     with open(st.session_state["report_path"], "r", encoding="utf-8") as f:
#         st.download_button(
#             label="📥 Скачать отчёт (.md)",
#             data=f.read(),
#             file_name=os.path.basename(st.session_state["report_path"]),
#             mime="text/markdown"
#         )

#     # Создаем ZIP-архив со всеми графиками
#     if image_paths:
#         # Убираем дубликаты, если они есть
#         image_paths = list(set(image_paths)) 
#         st.markdown(f"### 📥 Всего графиков: {len(image_paths)}")
#         zip_buffer = io.BytesIO()
#         with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
#             for img_path in image_paths:
#                 # Имя файла в архиве без полного пути
#                 arcname = os.path.relpath(img_path, "report/output") 
#                 # Убедимся, что файл существует перед добавлением
#                 if os.path.exists(img_path):
#                      zip_file.write(img_path, arcname)
#                 else:
#                      logger.warning(f"Файл изображения не найден при создании ZIP: {img_path}")
    
#         zip_buffer.seek(0)
#         st.download_button(
#             label="📥 Скачать все графики (.zip)",
#             data=zip_buffer,
#             file_name="visualizations.zip",
#             mime="application/zip"
#         )

#     st.subheader("📜 Логи агентов")

#     log_files = glob.glob("logs/*.log")

#     if log_files:
#         for log_file in log_files:
#             with open(log_file, "r", encoding="utf-8") as f:
#                 st.download_button(
#                     label=f"📥 Скачать {os.path.basename(log_file)}",
#                     data=f.read(),
#                     file_name=os.path.basename(log_file),
#                     mime="text/plain"
#                 )
#     logger.info("✅ Выведен финальный отчет")

#     st.markdown("---") # Разделитель
#     st.markdown(
#         "**Чтобы сохранить отчет в PDF:** Нажмите ⋮ (три точки)"
#         "в правом верхнем углу и выберите 'Print', или нажмите `Ctrl+P`."
#     )
