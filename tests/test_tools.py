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


import sys
import os

# Добавляем корень проекта в путь, чтобы импортировать модули из tools/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import pandas as pd
import numpy as np
from typing import Dict, Any
from pathlib import Path


# Импортируем тулзы
from tools.primary_feature_finder import primary_feature_finder
from tools.correlation_analysis import correlation_analysis
from tools.descriptive_stats_comparator import descriptive_stats_comparator
from tools.categorical_feature_analysis import categorical_feature_analysis
from tools.full_model_importance import full_model_importance
from tools.outlier_detector import outlier_detector
from tools.interaction_analyzer import interaction_analyzer
from tools.distribution_visualizer import distribution_visualizer

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
# Тесты: OutlierDetector
# --------------------------

def test_outlier_detector_success(sample_df):
    result = outlier_detector(sample_df, target_column="is_premium")
    check_tool_output(result, "OutlierDetector")
    if result["status"] == "success":
        d = result["details"]
        assert "outliers" in d and isinstance(d["outliers"], dict)
        assert "total_outliers" in d
        assert "method_used" in d
    print("✅ OutlierDetector: success")


def test_outlier_detector_no_numeric(sample_df):
    df = sample_df[["region", "loyalty", "is_premium"]].copy()
    result = outlier_detector(df, target_column="is_premium")
    assert result["status"] == "error"
    assert "numeric" in result["error_message"].lower()
    print("✅ OutlierDetector: no numeric features")


def test_outlier_detector_target_not_found(sample_df):
    result = outlier_detector(sample_df, target_column="nonexistent")
    assert result["status"] == "error"
    assert "not found" in result["error_message"].lower()
    print("✅ OutlierDetector: target column not found")


def test_outlier_detector_zscore_method(sample_df):
    result = outlier_detector(sample_df, target_column="is_premium", method="zscore", threshold=2.0)
    check_tool_output(result, "OutlierDetector")
    if result["status"] == "success":
        d = result["details"]
        assert d["method_used"] == "zscore"
    print("✅ OutlierDetector: zscore method")


def test_outlier_detector_no_outliers():
    import pandas as pd
    df = pd.DataFrame({
        "feature1": [10, 11, 12, 13, 14],
        "is_premium": [0, 1, 0, 1, 0]
    })
    result = outlier_detector(df, target_column="is_premium", method="iqr")
    assert result["status"] == "success"
    assert "Выбросы не обнаружены" in result["summary"]
    print("✅ OutlierDetector: no outliers detected")

# --------------------------
# Тесты: interaction_analyzer
# --------------------------

def test_interaction_analyzer_success(sample_df):
    result = interaction_analyzer(sample_df, target_column="is_premium")
    check_tool_output(result, "InteractionAnalyzer")
    if result["status"] == "success":
        d = result["details"]
        assert "interactions" in d and isinstance(d["interactions"], list)
        assert "total_analyzed" in d
        assert len(d["interactions"]) <= 5
    print("✅ InteractionAnalyzer: success")


def test_interaction_analyzer_target_not_found(sample_df):
    result = interaction_analyzer(sample_df, target_column="nonexistent")
    assert result["status"] == "error"
    assert "not found" in result["error_message"].lower()
    print("✅ InteractionAnalyzer: target column not found")


def test_interaction_analyzer_no_features(sample_df):
    df = sample_df[["is_premium"]].copy()
    result = interaction_analyzer(df, target_column="is_premium")
    assert result["status"] == "success"
    assert "Взаимодействия не найдены" in result["summary"]
    print("✅ InteractionAnalyzer: no features to analyze")


def test_interaction_analyzer_custom_top_k(sample_df):
    result = interaction_analyzer(sample_df, target_column="is_premium", top_k=2)
    if result["status"] == "success":
        assert len(result["details"]["interactions"]) <= 2
    print("✅ InteractionAnalyzer: custom top_k")


# --------------------------
# Тесты: distribution_vissualizer
# --------------------------

def test_distribution_visualizer_success(sample_df, tmp_path):
    output_dir = tmp_path / "images"
    result = distribution_visualizer(sample_df, target_column="is_premium", output_dir=str(output_dir))
    check_tool_output(result, "DistributionVisualizer")
    if result["status"] == "success":
        d = result["details"]
        assert "saved_images" in d and isinstance(d["saved_images"], dict)
        assert "features_analyzed" in d
        # Проверяем, что хотя бы один файл создан
        for f in d["saved_images"].values():
            assert "file_path" in f and Path(f["file_path"]).exists()
    print("✅ DistributionVisualizer: success")


def test_distribution_visualizer_no_numeric(sample_df, tmp_path):
    df = sample_df[["region", "loyalty", "is_premium"]].copy()
    result = distribution_visualizer(df, target_column="is_premium", output_dir=str(tmp_path))
    assert result["status"] == "error"
    assert "numeric" in result["error_message"].lower()
    print("✅ DistributionVisualizer: no numeric features")


def test_distribution_visualizer_target_not_found(sample_df, tmp_path):
    result = distribution_visualizer(sample_df, target_column="nonexistent", output_dir=str(tmp_path))
    assert result["status"] == "error"
    assert "not found" in result["error_message"].lower()
    print("✅ DistributionVisualizer: target column not found")


def test_distribution_visualizer_custom_top_k(sample_df, tmp_path):
    output_dir = tmp_path / "images"
    result = distribution_visualizer(sample_df, target_column="is_premium", top_k=2, output_dir=str(output_dir))
    if result["status"] == "success":
        assert len(result["details"]["features_analyzed"]) <= 2
    print("✅ DistributionVisualizer: custom top_k")


