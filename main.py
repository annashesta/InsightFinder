# # main.py
# """
# Точка входа в систему InsightFinder.
# Мультиагентная система на LangChain для автоматического EDA.
# """

# import subprocess
# import sys
# import os

# def main():
#     # Формируем путь до web_app.py
#     ui_path = os.path.join("ui", "web_app.py")
    
#     # Запускаем Streamlit
#     subprocess.run([sys.executable, "-m", "streamlit", "run", ui_path])

# if __name__ == "__main__":
#     main()



"""
Точка входа в систему InsightFinder.
Мультиагентная система на LangChain для автоматического EDA.
"""

import os
import sys


def main():
    """Основная функция запуска."""
    # Получаем абсолютный путь к корневой директории проекта
    project_root = os.path.dirname(os.path.abspath(__file__))

    # Добавляем корневую директорию в sys.path
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        print(f"Добавлен в PYTHONPATH: {project_root}")

    try:
        # Импортируем модуль gradio_app и запускаем интерфейс
        import ui.gradio_app
        print("Запуск Gradio приложения...")
        demo = ui.gradio_app.build_interface()
        demo.launch(server_name="0.0.0.0", server_port=8502)
    except Exception as e:
        print(f"Ошибка при запуске Gradio приложения: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
