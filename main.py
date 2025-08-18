# main.py
import pandas as pd
from agents.tools_wrapper import set_current_data, ALL_TOOLS
from agents.analyst import create_analyst_agent
from agents.executor import create_executor_agent
from agents.summarizer import generate_summary


from dotenv import load_dotenv
import os

load_dotenv()

# Проверка наличия ключа
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY не найден в .env файле!")
if not os.getenv("OPENAI_BASE_URL"):
    raise ValueError("OPENAI_BASE_URL не найден в .env файле!")


def main(data_path: str, target_column: str, output_report: str = "report.md"):
    # 1. Загружаем данные
    df = pd.read_csv(data_path)
    print(f"✅ Загружено: {df.shape[0]} строк, {df.shape[1]} столбцов")

    # 2. Передаём данные в тулзы
    set_current_data(df, target_column)

    # 3. Создаём агентов
    analyst = create_analyst_agent(ALL_TOOLS)
    executor = create_executor_agent(ALL_TOOLS, analyst["prompt"], analyst["llm"])

    # 4. Запускаем анализ
    print("\n🔍 Запуск агентской системы...\n")
    result = executor.invoke({
        "messages": [
            {"role": "user", "content": f"Проанализируй данные и найди, чем группа 1 отличается от группы 0 по признаку '{target_column}'."}
        ]
    })

    # 5. Генерируем отчёт
    print("\n📝 Генерация отчёта...")
    summary = generate_summary(str(result), filename=data_path.split("/")[-1])

    # 6. Сохраняем
    with open(output_report, "w", encoding="utf-8") as f:
        f.write(summary)
    print(f"\n✅ Отчёт сохранён: {output_report}")

if __name__ == "__main__":
    main("data/telecom_eda_data.csv", target_column="Churn", output_report="report.md")