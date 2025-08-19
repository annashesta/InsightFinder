# main.py
# С нашим API не работает (( ,
# Можно использовать ollama, но тогда нужно во всех файлах директории agents скорректировать импорт и модель на ollama.


import os
import pandas as pd
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Проверка API
assert os.getenv("OPENAI_API_KEY"), "Установите OPENAI_API_KEY в .env"
assert os.getenv("OPENAI_BASE_URL"), "Установите OPENAI_BASE_URL в .env"

# Добавляем корень проекта в путь
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from agents.analyst_agent import create_analyst_agent
from agents.executor_agent import create_executor_agent
from agents.summarizer_agent import generate_summary
from agents.tools_wrapper import set_current_data, ALL_TOOLS


def main(data_path: str, target_column: str, output_report: str = "report.md"):
    """
    Основная функция: запускает мультиагентный анализ и генерирует отчёт.
    """
    # 1. Загружаем данные
    print(f"📁 Загружаем данные из {data_path}...")
    df = pd.read_csv(data_path)
    print(f"✅ Загружено: {df.shape[0]} строк, {df.shape[1]} столбцов")

    # 2. Передаём данные в тулзы
    set_current_data(df, target_column)

    # 3. Создаём агентов
    print("\n🧠 Создаём агентскую систему...")
    analyst = create_analyst_agent(ALL_TOOLS)
    executor = create_executor_agent(ALL_TOOLS, analyst["prompt"], analyst["llm"])

    # 4. Запускаем анализ
    print("\n🔍 Запуск анализа агентами...\n")
    result = executor.invoke({
        "messages": [
            {
                "role": "user",
                "content": f"Проанализируй данные и найди, чем группа 1 отличается от группы 0 по признаку '{target_column}'."
            }
        ]
    })

    # 5. Генерируем отчёт
    print("\n📝 Генерация итогового отчёта...")
    full_result_str = str(result)
    summary = generate_summary(full_result_str, filename=data_path.split("/")[-1])

    # 6. Сохраняем
    with open(output_report, "w", encoding="utf-8") as f:
        f.write(summary)
    print(f"\n🎉 Отчёт успешно сохранён: {output_report}")


if __name__ == "__main__":
    main(
        data_path="data/telecom_eda_data.csv",
        target_column="Churn",
        output_report="report.md"
    )