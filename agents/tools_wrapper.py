# agents/tools_wrapper.py
from typing import Dict, Any
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

# Импортируем ваши тулзы
from tools.primary_feature_finder import primary_feature_finder
from tools.correlation_analysis import correlation_analysis
from tools.descriptive_stats_comparator import descriptive_stats_comparator
from tools.categorical_feature_analysis import categorical_feature_analysis
from tools.full_model_importance import full_model_importance

# Глобальные переменные для передачи данных
CURRENT_DF = None
CURRENT_TARGET = None


def set_current_data(df, target_column: str):
    """Устанавливает глобальные данные, доступные всем тулзам."""
    global CURRENT_DF, CURRENT_TARGET
    CURRENT_DF = df
    CURRENT_TARGET = target_column


class PrimaryFeatureFinderTool(BaseTool):
    name: str = "PrimaryFeatureFinder"
    description: str = "Находит самый важный признак, разделяющий группы по целевой переменной, с помощью дерева глубины 1."
    return_direct: bool = False

    def _run(self) -> dict:
        if CURRENT_DF is None or CURRENT_TARGET is None:
            return {
                "tool_name": self.name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": "Ошибка: данные не загружены."
            }
        result = primary_feature_finder(CURRENT_DF, CURRENT_TARGET)
        return result


class CorrelationAnalysisTool(BaseTool):
    name: str = "CorrelationAnalysis"
    description: str = "Анализирует корреляцию числовых признаков с бинарной целевой переменной (point-biserial)."
    return_direct: bool = False

    def _run(self) -> dict:
        if CURRENT_DF is None or CURRENT_TARGET is None:
            return {
                "tool_name": self.name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": "Ошибка: данные не загружены."
            }
        result = correlation_analysis(CURRENT_DF, CURRENT_TARGET)
        return result


class DescriptiveStatsComparatorTool(BaseTool):
    name: str = "DescriptiveStatsComparator"
    description: str = "Сравнивает средние и медианы по группам (0 и 1), находит значимые различия (>20%)."
    return_direct: bool = False

    def _run(self) -> dict:
        if CURRENT_DF is None or CURRENT_TARGET is None:
            return {
                "tool_name": self.name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": "Ошибка: данные не загружены."
            }
        result = descriptive_stats_comparator(CURRENT_DF, CURRENT_TARGET)
        return result


class CategoricalFeatureAnalysisTool(BaseTool):
    name: str = "CategoricalFeatureAnalysis"
    description: str = "Проверяет связь категориальных признаков с целевой переменной через тест Хи-квадрат."
    return_direct: bool = False

    def _run(self) -> dict:
        if CURRENT_DF is None or CURRENT_TARGET is None:
            return {
                "tool_name": self.name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": "Ошибка: данные не загружены."
            }
        result = categorical_feature_analysis(CURRENT_DF, CURRENT_TARGET)
        return result


class FullModelFeatureImportanceTool(BaseTool):
    name: str = "FullModelFeatureImportance"
    description: str = "Обучает Random Forest и возвращает топ-10 важных признаков."
    return_direct: bool = False

    def _run(self) -> dict:
        if CURRENT_DF is None or CURRENT_TARGET is None:
            return {
                "tool_name": self.name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": "Ошибка: данные не загружены."
            }
        result = full_model_importance(CURRENT_DF, CURRENT_TARGET)
        return result


# Список всех тулзов
ALL_TOOLS = [
    PrimaryFeatureFinderTool(),
    CorrelationAnalysisTool(),
    DescriptiveStatsComparatorTool(),
    CategoricalFeatureAnalysisTool(),
    FullModelFeatureImportanceTool(),
]