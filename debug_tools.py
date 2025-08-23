# debug_tools.py
# Ручная проверка вывода 
# Запуск: python debug_tools.py


import pandas as pd
from tools.primary_feature_finder import primary_feature_finder
from tools.correlation_analysis import correlation_analysis
from tools.descriptive_stats_comparator import descriptive_stats_comparator
from tools.categorical_feature_analysis import categorical_feature_analysis
from tools.full_model_importance import full_model_importance

# Загружаем реальный датасет
df = pd.read_csv("data/telecom_eda_data.csv")

# Проверяем столбцы
print("Доступные столбцы:", df.columns.tolist())
print("Пример значений Churn:", df["Churn"].dropna().unique())

# Используем правильное имя целевой переменной
target_column = "Churn"

tools = [
    ("PrimaryFeatureFinder", primary_feature_finder),
    ("CorrelationAnalysis", correlation_analysis),
    ("DescriptiveStatsComparator", descriptive_stats_comparator),
    ("CategoricalFeatureAnalysis", categorical_feature_analysis),
    ("FullModelFeatureImportance", full_model_importance)
]

for name, func in tools:
    print(f"\n🔍 Запуск: {name}")
    result = func(df, target_column=target_column)
    print("Статус:", result["status"])
    if result["status"] == "success":
        print("Краткий вывод:", result["summary"])
        print("Детали:", list(result["details"].keys()))
    else:
        print("Ошибка:", result["error_message"])