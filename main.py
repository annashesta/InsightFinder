# # main.py

# # "Поскольку сервер API не поддерживает tool_choice="auto", для оркестрации агентов был реализован кастомный цикл, 
# # в котором Аналитик выбирает инструмент по имени, 
# # а Исполнитель вызывает соответствующую функцию. 
# # Это обеспечивает полный контроль над процессом и гарантирует работу системы."


# from core.data_loader import load_data
# from core.orchestrator import run_analysis_pipeline
# from report.generate_report import generate_report
# from dotenv import load_dotenv
# import os

# load_dotenv()

# def main(data_path: str, target_column: str, output_report: str = "report.md"):
#     # 1. Загрузка данных
#     df = load_data(data_path)
#     print(f"✅ Загружено: {df.shape[0]} строк, {df.shape[1]} столбцов")

#     # 2. Запуск анализа
#     results = run_analysis_pipeline(df, target_column)

#     # 3. Генерация отчёта
#     report = generate_report(results, filename=data_path.split("/")[-1])

#     # 4. Сохранение
#     with open(output_report, "w", encoding="utf-8") as f:
#         f.write(report)
#     print(f"✅ Отчёт сохранён: {output_report}")

# if __name__ == "__main__":
#     main("data/telecom_eda_data.csv", "Churn")

from core.orchestrator import run_simple_orchestration
import pandas as pd

def main():
    # Загружаем тестовый CSV (можно заменить на свой)
    df = pd.DataFrame({
        "feature1": [1, 2, 3, 4],
        "feature2": [10, 20, 30, 40],
        "target": [0, 1, 0, 1]
    })
    
    history, report = run_simple_orchestration(df, target_column="target")

    print("\n=== Итоговый отчёт ===\n")
    print(report)


if __name__ == "__main__":
    main()