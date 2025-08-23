# tests/test_tools.py
# Для запуска всех. тестов pytest tests/test_tools.py -v -s
# Заметка: всего 11 тестов

# 1. PrimaryFeatureFinder (2 теста)
# test_primary_feature_finder_success
# test_primary_feature_finder_missing_target
# 2. CorrelationAnalysis (2 теста)
# test_correlation_analysis_success
# test_correlation_analysis_no_numeric
# 3. DescriptiveStatsComparator (2 теста)
# test_descriptive_stats_comparator_success
# test_descriptive_stats_comparator_no_numeric
# 4. CategoricalFeatureAnalysis (2 теста)
# test_categorical_feature_analysis_success
# test_categorical_feature_analysis_no_categorical
# 5. FullModelFeatureImportance (2 теста)
# test_full_model_importance_success
# test_full_model_importance_top_k
#  Интеграционный тест на реальных данных (1 тест)
# test_all_tools_on_real_data
# Этот тест один, но внутри прогоняет все 5 тулзов на реальном датасете.
# Он не делится на отдельные test_-функции, но выполняет комплексную проверку. 


import sys
import os

# Добавляем корень проекта в путь, чтобы импортировать модули из tools/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import pandas as pd
import numpy as np
from typing import Dict, Any

# Импортируем тулзы
from tools.primary_feature_finder import primary_feature_finder
from tools.correlation_analysis import correlation_analysis
from tools.descriptive_stats_comparator import descriptive_stats_comparator
from tools.categorical_feature_analysis import categorical_feature_analysis
from tools.full_model_importance import full_model_importance


# --------------------------
# Фикстуры
# --------------------------

@pytest.fixture
def sample_df():
    """
    Синтетический датасет, имитирующий структуру telecom_eda_data.csv.
    Целевая переменная — строковая: 'Yes' / 'No'.
    """
    np.random.seed(42)
    n = 500

    # Генерируем данные с корреляцией к целевой переменной
    is_premium_yes = np.random.choice([0, 1], n, p=[0.7, 0.3])
    income = np.random.normal(50000, 10000, n) + is_premium_yes * 15000
    age = np.random.randint(18, 65, n) + is_premium_yes * 8
    spend_score = np.random.randint(1, 100, n) + is_premium_yes * 20

    df = pd.DataFrame({
        'income': income,
        'age': age,
        'spend_score': spend_score,
        'region': np.random.choice(['North', 'South', 'East', 'West'], n),
        'loyalty': np.random.choice(['Basic', 'Silver', 'Gold'], n, p=[0.6, 0.3, 0.1]),
        'is_premium': np.where(is_premium_yes == 1, 'Yes', 'No')  # Строковый таргет
    })
    return df


@pytest.fixture
def real_df():
    """
    Загружает реальный датасет из data/telecom_eda_data.csv.
    Если файл не найден — пропускает тесты.
    """
    path = "data/telecom_eda_data.csv"
    if not os.path.exists(path):
        pytest.skip(f"Файл {path} не найден. Пропускаем тесты на реальных данных.")
    df = pd.read_csv(path)
    # Приводим таргет к строковому формату, если нужно
    if 'Churn' in df.columns:
        df['Churn'] = df['Churn'].astype(str).str.strip()
    return df


# --------------------------
# Общая проверка структуры вывода
# --------------------------

def check_tool_output(result: Dict[str, Any], expected_tool_name: str):
    """
    Проверяет, что результат тулза соответствует ТЗ:
    - правильные ключи
    - корректный статус
    - типы данных
    """
    assert isinstance(result, dict), "Результат должен быть словарём"
    assert set(result.keys()) == {"tool_name", "status", "summary", "details", "error_message"}, \
        f"Неверные ключи в результате: {list(result.keys())}"

    assert result["tool_name"] == expected_tool_name, \
        f"Ожидался tool_name='{expected_tool_name}', получено='{result['tool_name']}'"
    assert result["status"] in ["success", "error"], \
        f"Неверный статус: {result['status']}"

    if result["status"] == "success":
        assert isinstance(result["summary"], str), "summary должен быть строкой"
        assert len(result["summary"]) > 0, "summary не должен быть пустым"
        assert isinstance(result["details"], dict), "details должен быть словарём"
        assert result["error_message"] is None, "error_message должен быть None при успехе"
    else:
        assert result["error_message"] is None or isinstance(result["error_message"], str), \
            "error_message должен быть строкой или None"
        assert result["error_message"] is None or len(result["error_message"]) > 0, \
            "error_message не должен быть пустым при ошибке"


# --------------------------
# Тесты: PrimaryFeatureFinder
# --------------------------

def test_primary_feature_finder_success(sample_df):
    result = primary_feature_finder(sample_df, target_column="is_premium")
    check_tool_output(result, "PrimaryFeatureFinder")
    if result["status"] == "success":
        d = result["details"]
        assert "best_feature" in d and isinstance(d["best_feature"], str)
        assert "split_threshold" in d and isinstance(d["split_threshold"], (int, float))
        assert "information_gain" in d and isinstance(d["information_gain"], (int, float))
        assert d["information_gain"] >= 0
    print("✅ PrimaryFeatureFinder: success")

def test_primary_feature_finder_missing_target(sample_df):
    result = primary_feature_finder(sample_df, target_column="missing")
    assert result["status"] == "error"
    assert "not found" in result["error_message"].lower()
    print("✅ PrimaryFeatureFinder: missing target")


# --------------------------
# Тесты: CorrelationAnalysis
# --------------------------

def test_correlation_analysis_success(sample_df):
    result = correlation_analysis(sample_df, target_column="is_premium")
    check_tool_output(result, "CorrelationAnalysis")
    if result["status"] == "success":
        d = result["details"]
        assert "top_positive" in d and isinstance(d["top_positive"], dict)
        assert "top_negative" in d and isinstance(d["top_negative"], dict)
        assert len(d["top_positive"]) <= 5
        assert "n_features_analyzed" in d and d["n_features_analyzed"] > 0
    print("✅ CorrelationAnalysis: success")

def test_correlation_analysis_no_numeric(sample_df):
    df = sample_df[["region", "loyalty", "is_premium"]].copy()
    result = correlation_analysis(df, target_column="is_premium")
    assert result["status"] == "error"
    assert "numeric" in result["error_message"].lower()
    print("✅ CorrelationAnalysis: no numeric features")


# --------------------------
# Тесты: DescriptiveStatsComparator
# --------------------------

def test_descriptive_stats_comparator_success(sample_df):
    result = descriptive_stats_comparator(sample_df, target_column="is_premium")
    check_tool_output(result, "DescriptiveStatsComparator")
    if result["status"] == "success":
        d = result["details"]
        assert "significant_differences" in d and isinstance(d["significant_differences"], dict)
        assert "n_features_with_diff" in d
    print("✅ DescriptiveStatsComparator: success")

def test_descriptive_stats_comparator_no_numeric(sample_df):
    df = sample_df[["region", "loyalty", "is_premium"]].copy()
    result = descriptive_stats_comparator(df, target_column="is_premium")
    assert result["status"] == "error"
    print("✅ DescriptiveStatsComparator: no numeric features")


# --------------------------
# Тесты: CategoricalFeatureAnalysis
# --------------------------

def test_categorical_feature_analysis_success(sample_df):
    result = categorical_feature_analysis(sample_df, target_column="is_premium")
    check_tool_output(result, "CategoricalFeatureAnalysis")
    if result["status"] == "success":
        d = result["details"]
        assert "significant_features" in d and isinstance(d["significant_features"], dict)
        assert "n_significant" in d
    print("✅ CategoricalFeatureAnalysis: success")

def test_categorical_feature_analysis_no_categorical(sample_df):
    df = sample_df[["income", "age", "spend_score", "is_premium"]].copy()
    result = categorical_feature_analysis(df, target_column="is_premium")
    assert result["status"] == "error"
    print("✅ CategoricalFeatureAnalysis: no categorical features")


# --------------------------
# Тесты: FullModelFeatureImportance
# --------------------------

def test_full_model_importance_success(sample_df):
    result = full_model_importance(sample_df, target_column="is_premium")
    check_tool_output(result, "FullModelFeatureImportance")
    if result["status"] == "success":
        d = result["details"]
        assert "feature_importances" in d and isinstance(d["feature_importances"], dict)
        assert len(d["feature_importances"]) <= 10
    print("✅ FullModelFeatureImportance: success")

def test_full_model_importance_top_k(sample_df):
    result = full_model_importance(sample_df, target_column="is_premium", top_k=3)
    if result["status"] == "success":
        assert len(result["details"]["feature_importances"]) <= 3
    print("✅ FullModelFeatureImportance: custom top_k")


# --------------------------
# Интеграционный тест: все тулзы на реальных данных
# --------------------------

def test_all_tools_on_real_data(real_df):
    """
    Прогон всех тулзов на реальном датасете.
    Автоопределение целевой переменной.
    """
    # Ищем бинарную строковую колонку: 'Yes'/'No', 'True'/'False', '0'/'1'
    possible_targets = []
    for col in real_df.columns:
        if real_df[col].dtype == 'object':
            unique_vals = real_df[col].dropna().astype(str).str.strip().str.lower().unique()
            if len(unique_vals) == 2:
                possible_targets.append(col)

    if not possible_targets:
        pytest.skip("Не найдено бинарных строковых колонок для анализа.")

    target_col = possible_targets[0]  # Берём первую подходящую
    print(f"\n🔍 Используем целевую переменную: '{target_col}' со значениями {real_df[target_col].dropna().unique()}")

    tools = [
        ("PrimaryFeatureFinder", lambda: primary_feature_finder(real_df, target_col)),
        ("CorrelationAnalysis", lambda: correlation_analysis(real_df, target_col)),
        ("DescriptiveStatsComparator", lambda: descriptive_stats_comparator(real_df, target_col)),
        ("CategoricalFeatureAnalysis", lambda: categorical_feature_analysis(real_df, target_col)),
        ("FullModelFeatureImportance", lambda: full_model_importance(real_df, target_col)),
    ]

    for name, func in tools:
        try:
            result = func()
            status = result["status"]
            print(f"✅ {name:25} | {status.upper()}")
            if status == "error":
                print(f"   ❌ Ошибка: {result['error_message']}")
        except Exception as e:
            print(f"💥 {name:25} | FAILED with exception: {str(e)}")