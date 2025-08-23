# tests/test_edge_cases.py

# Теты на негативные сценарии
# Запуск python tests/test_edge_cases.py

# tests/test_edge_cases.py

import sys
import os

# Добавляем корень проекта в путь для импорта из tools/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import numpy as np
from tools.primary_feature_finder import primary_feature_finder
from tools.correlation_analysis import correlation_analysis
from tools.descriptive_stats_comparator import descriptive_stats_comparator
from tools.categorical_feature_analysis import categorical_feature_analysis
from tools.full_model_importance import full_model_importance


def test_missing_target_column():
    """Тест: целевой столбец отсутствует в данных."""
    df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    tools = [
        primary_feature_finder,
        correlation_analysis,
        descriptive_stats_comparator,
        categorical_feature_analysis,
        full_model_importance
    ]
    for tool in tools:
        result = tool(df, "target")
        assert result["status"] == "error", f"{tool.__name__} не вернул ошибку при отсутствии целевой переменной"
        assert "not found" in result["error_message"].lower(), f"Нет упоминания 'not found': {result['error_message']}"
    print("✅ Все тулзы корректно обрабатывают отсутствие целевой переменной")


def test_empty_dataframe():
    """Тест: пустой DataFrame (нет строк и столбцов)."""
    df = pd.DataFrame()
    tools = [
        primary_feature_finder,
        correlation_analysis,
        descriptive_stats_comparator,
        categorical_feature_analysis,
        full_model_importance
    ]
    for tool in tools:
        result = tool(df, "target")
        assert result["status"] == "error", f"{tool.__name__} не вернул ошибку на пустом DataFrame"
    print("✅ Все тулзы корректно обрабатывают пустой DataFrame")


def test_single_column_dataframe():
    """Тест: DataFrame содержит только целевую переменную (нет признаков)."""
    df = pd.DataFrame({"target": [0, 1, 0, 1]})
    tools = [
        primary_feature_finder,
        correlation_analysis,
        descriptive_stats_comparator,
        categorical_feature_analysis,
        full_model_importance
    ]
    for tool in tools:
        result = tool(df, "target")
        assert result["status"] == "error", f"{tool.__name__} не вернул ошибку при отсутствии признаков"
        
        # Гибкая проверка: подойдут любые варианты
        error_msg = result["error_message"].lower()
        assert any(keyword in error_msg for keyword in [
            "feature", "признак", "column", "столбец", "only target", "dataset has only"
        ]), f"Ошибка не содержит ключевых слов: {result['error_message']}"
    print("✅ Все тулзы корректно обрабатывают отсутствие признаков")


def test_non_binary_target():
    """Тест: целевая переменная не бинарная (3 класса)."""
    df = pd.DataFrame({
        "feature": [1, 2, 3, 4, 5],
        "target": [0, 1, 2, 0, 1]  # 3 класса
    })
    tools = [
        correlation_analysis,
        primary_feature_finder,
        full_model_importance
    ]
    for tool in tools:
        result = tool(df, "target")
        assert result["status"] == "error", f"{tool.__name__} не вернул ошибку на не-бинарной целевой переменной"
        assert any(keyword in result["error_message"].lower() for keyword in [
            "binary", "not binary", "двоичная", "бинарная"
        ]), f"Ошибка не указывает на проблему с бинарностью: {result['error_message']}"
    print("✅ Тулзы корректно обрабатывают не-бинарную целевую переменную")


def test_numeric_only_for_correlation():
    """Тест: в данных нет числовых признаков — correlation_analysis должен вернуть ошибку."""
    df = pd.DataFrame({
        "category": ["A", "B", "A", "B"],
        "target": [0, 1, 0, 1]
    })
    result = correlation_analysis(df, "target")
    assert result["status"] == "error"
    assert any(k in result["error_message"].lower() for k in ["numeric", "числовые"])
    print("✅ correlation_analysis корректно обрабатывает отсутствие числовых признаков")


def test_categorical_only_for_categorical_analysis():
    """Тест: в данных нет категориальных признаков — categorical_feature_analysis должен вернуть ошибку."""
    df = pd.DataFrame({
        "num1": [1.0, 2.0, 3.0],
        "num2": [4, 5, 6],
        "target": [0, 1, 0]
    })
    result = categorical_feature_analysis(df, "target")
    assert result["status"] == "error"
    assert any(k in result["error_message"].lower() for k in ["categorical", "категориальные"])
    print("✅ categorical_feature_analysis корректно обрабатывает отсутствие категориальных признаков")


def test_all():
    """Запускает все тесты."""
    test_missing_target_column()
    test_empty_dataframe()
    test_single_column_dataframe()
    test_non_binary_target()
    test_numeric_only_for_correlation()
    test_categorical_only_for_categorical_analysis()
    print("\n🎉 Все негативные тесты пройдены!")


if __name__ == "__main__":
    test_all()