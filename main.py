# main.py
"""
Точка входа в систему InsightFinder. Используя Gradio.
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
