# tests/test_tools.py
import pytest
import pandas as pd
import numpy as np
import os
from typing import Dict, Any

# Импортируем тулзы
from tools.primary_feature_finder import primary_feature_finder
from tools.correlation_analysis import correlation_analysis
from tools.descriptive_stats_comparator import descriptive_stats_comparator
from tools.categorical_feature_analysis import categorical_feature_analysis
from tools.full_model_importance import full_model_importance


# Фикстуры


@pytest.fixture
def sample_df():
    """Синтетический датасет с числовыми и категориальными признаками."""
    np.random.seed(42)
    n = 500
    df = pd.DataFrame({
        'income': np.random.normal(50000, 10000, n) + np.random.choice([0, 15000], n, p=[0.7, 0.3]),
        'age': np.random.randint(18, 65, n) + np.random.choice([0, 8], n, p=[0.7, 0.3]),
        'spend_score': np.random.randint(1, 100, n),
        'region': np.random.choice(['North', 'South', 'East', 'West'], n),
        'loyalty': np.random.choice(['Basic', 'Silver', 'Gold'], n, p=[0.6, 0.3, 0.1]),
        'is_premium': np.random.choice([0, 1], n, p=[0.7, 0.3])
    })
    return df

@pytest.fixture
def real_df():
    """Загружает реальный датасет из data/telecom_eda_data.csv"""
    path = "data/telecom_eda_data.csv"
    if not os.path.exists(path):
        pytest.skip(f"Файл {path} не найден. Пропускаем тесты на реальных данных.")
    return pd.read_csv(path)

# --------------------------
# Общие проверки
# --------------------------

def check_tool_output(result: Dict[str, Any], expected_tool_name: str):
    """Проверяет, что результат тулза имеет правильную структуру."""
    assert isinstance(result, dict), "Результат должен быть словарём"
    assert "tool_name" in result
    assert "status" in result
    assert "summary" in result
    assert "details" in result
    assert "error_message" in result

    assert result["tool_name"] == expected_tool_name
    assert result["status"] in ["success", "error"]

    if result["status"] == "success":
        assert isinstance(result["summary"], str)
        assert len(result["summary"]) > 0
        assert isinstance(result["details"], dict)
        assert result["error_message"] is None
    else:
        assert isinstance(result["error_message"], str)
        assert len(result["error_message"]) > 0


# Тесты для каждого тулза

# 1. primary_feature_finder

def test_primary_feature_finder_success(sample_df):
    result = primary_feature_finder(sample_df, target_column="is_premium")
    check_tool_output(result, "PrimaryFeatureFinder")
    if result["status"] == "success":
        d = result["details"]
        assert "best_feature" in d
        assert "split_threshold" in d
        assert "information_gain" in d
        assert d["information_gain"] >= 0
    print("✅ primary_feature_finder: success")

def test_primary_feature_finder_missing_target(sample_df):
    result = primary_feature_finder(sample_df, target_column="missing")
    assert result["status"] == "error"
    assert "not found" in result["error_message"]
    print("✅ primary_feature_finder: missing target")



# 2. correlation_analysis

def test_correlation_analysis_success(sample_df):
    result = correlation_analysis(sample_df, target_column="is_premium")
    check_tool_output(result, "CorrelationAnalysis")
    if result["status"] == "success":
        d = result["details"]
        assert "top_positive" in d
        assert "top_negative" in d
        assert len(d["top_positive"]) <= 5
        assert d["n_features_analyzed"] > 0
    print("✅ correlation_analysis: success")

def test_correlation_analysis_no_numeric(sample_df):
    df_no_num = sample_df.select_dtypes(include=['object']).copy()
    df_no_num["is_premium"] = sample_df["is_premium"]
    result = correlation_analysis(df_no_num, target_column="is_premium")
    assert result["status"] == "error"
    assert "numeric" in result["error_message"]
    print("✅ correlation_analysis: no numeric features")


#  3. descriptive_stats_comparator

def test_descriptive_stats_comparator_success(sample_df):
    result = descriptive_stats_comparator(sample_df, target_column="is_premium")
    check_tool_output(result, "DescriptiveStatsComparator")
    if result["status"] == "success":
        d = result["details"]
        assert "significant_differences" in d
        assert isinstance(d["significant_differences"], dict)
    print("✅ descriptive_stats_comparator: success")

def test_descriptive_stats_comparator_no_numeric(sample_df):
    df_cat = sample_df.select_dtypes(include=['object']).copy()
    df_cat["is_premium"] = sample_df["is_premium"]
    result = descriptive_stats_comparator(df_cat, target_column="is_premium")
    assert result["status"] == "error"
    print("✅ descriptive_stats_comparator: no numeric")


# 4.  categorical_feature_analysis

def test_categorical_feature_analysis_success(sample_df):
    result = categorical_feature_analysis(sample_df, target_column="is_premium")
    check_tool_output(result, "CategoricalFeatureAnalysis")
    if result["status"] == "success":
        d = result["details"]
        assert "significant_features" in d
        assert isinstance(d["significant_features"], dict)
    print("✅ categorical_feature_analysis: success")

def test_categorical_feature_analysis_no_categorical(sample_df):
    df_num = sample_df.select_dtypes(include=['number']).copy()
    df_num["is_premium"] = sample_df["is_premium"]
    result = categorical_feature_analysis(df_num, target_column="is_premium")
    assert result["status"] == "error"
    print("✅ categorical_feature_analysis: no categorical")


# 5. full_model_importance

def test_full_model_importance_success(sample_df):
    result = full_model_importance(sample_df, target_column="is_premium")
    check_tool_output(result, "FullModelFeatureImportance")
    if result["status"] == "success":
        d = result["details"]
        assert "feature_importances" in d
        assert isinstance(d["feature_importances"], dict)
        assert len(d["feature_importances"]) <= 10
    print("✅ full_model_importance: success")

def test_full_model_importance_top_k(sample_df):
    result = full_model_importance(sample_df, target_column="is_premium", top_k=5)
    if result["status"] == "success":
        assert len(result["details"]["feature_importances"]) <= 5
    print("✅ full_model_importance: custom top_k")

# --------------------------
# Тесты на реальных данных 
# --------------------------

def test_all_tools_on_real_data(real_df):
    """Прогон всех тулзов на реальном датасете."""
    target_col = "churn"  # Предполагаем, что в telecom_eda_data.csv есть столбец 'churn'
    if target_col not in real_df.columns:
        target_col = real_df.columns[-1]  # Попробуем последний
        print(f"⚠️ Целевая переменная не найдена как 'churn', используем: {target_col}")

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
            print(f"✅ {name}: {result['status']}")
            if result["status"] == "error":
                print(f"   ❌ Ошибка: {result['error_message']}")
        except Exception as e:
            print(f"💥 {name}: Исключение: {str(e)}")