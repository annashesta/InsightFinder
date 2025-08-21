# main.py
"""
Точка входа в систему InsightFinder.
Мультиагентная система на LangChain для автоматического EDA.
"""

import subprocess
import sys
import os

def main():
    # Формируем путь до web_app.py
    ui_path = os.path.join("ui", "web_app.py")
    
    # Запускаем Streamlit
    subprocess.run([sys.executable, "-m", "streamlit", "run", ui_path])

if __name__ == "__main__":
    main()
