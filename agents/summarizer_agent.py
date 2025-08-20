# agents/summarizer_agent.py
import os
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from core.logger import get_logger

load_dotenv()
logger = get_logger(__name__, "summarizer.log")


def _format_categorical_details(result: Optional[Dict[str, Any]]) -> str:
    """Форматирует детали категориальных признаков."""
    if not result or result["status"] != "success":
        return ""
    
    details = result.get("details", {})
    significant_features = details.get("significant_features", {})
    
    if not significant_features:
        return ""
    
    lines = ["\n**Значимые категориальные признаки:**"]
    for feature, stats in significant_features.items():
        p_val = stats.get('p_value', 'N/A')
        chi2 = stats.get('chi2', 'N/A')
        lines.append(f"- {feature}: p-value={p_val:.2e}, chi2={chi2:.2f}")
    
    return "\n".join(lines)


def _format_correlation_details(result: Optional[Dict[str, Any]]) -> str:
    """Форматирует детали корреляционного анализа."""
    if not result or result["status"] != "success":
        return ""
    
    details = result.get("details", {})
    top_pos = details.get("top_positive", {})
    top_neg = details.get("top_negative", {})
    
    lines = []
    if top_pos:
        lines.append("\n**Топ положительных корреляций:**")
        for feature, corr in top_pos.items():
            lines.append(f"- {feature}: {corr:.3f}")
    
    if top_neg:
        lines.append("\n**Топ отрицательных корреляций:**")
        for feature, corr in top_neg.items():
            lines.append(f"- {feature}: {corr:.3f}")
    
    return "\n".join(lines)


def _format_stats_details(result: Optional[Dict[str, Any]]) -> str:
    """Форматирует детали сравнения статистик."""
    if not result or result["status"] != "success":
        return ""
    
    details = result.get("details", {})
    diffs = details.get("significant_differences", [])
    
    if not diffs:
        return ""
    
    lines = ["\n**Значимые различия по статистикам:**"]
    for diff in diffs:
        feature_stat = diff.get("feature_stat", "N/A")
        val_0 = diff.get("group_0", "N/A")
        val_1 = diff.get("group_1", "N/A")
        rel_diff = diff.get("relative_difference", "N/A")
        rel_diff_pct = rel_diff * 100 if rel_diff != "N/A" else "N/A"
        lines.append(f"- {feature_stat}: группа 0={val_0:.3f}, группа 1={val_1:.3f}, разница={rel_diff_pct:.1f}%")
    
    return "\n".join(lines)


def _format_model_details(result: Optional[Dict[str, Any]]) -> str:
    """Форматирует детали важности признаков."""
    if not result or result["status"] != "success":
        return ""
    
    details = result.get("details", {})
    importances = details.get("feature_importances", {})
    
    if not importances:
        return ""
    
    lines = ["\n**Важность признаков по Random Forest:**"]
    for feature, importance in importances.items():
        lines.append(f"- {feature}: {importance:.4f}")
    
    return "\n".join(lines)


def _format_visualization_details(result: Optional[Dict[str, Any]]) -> str:
    """Форматирует визуализации для отчёта."""
    if not result or result["status"] != "success":
        return ""
    
    details = result.get("details", {})
    visualizations = details.get("visualizations", {})
    
    if not visualizations:
        return ""
    
    lines = ["\n**Визуализации распределений:**"]
    for feature, viz_data in visualizations.items():
        image_base64 = viz_data.get("image_base64", "")
        description = viz_data.get("description", "")
        lines.append(f"\n### Распределение {feature}")
        lines.append(f"*{description}*")
        lines.append(f"![{feature}](data:image/png;base64,{image_base64})")
    
    return "\n".join(lines)


def _format_outlier_details(result: Optional[Dict[str, Any]]) -> str:
    """Форматирует детали обнаружения выбросов."""
    if not result or result["status"] != "success":
        return ""
    
    details = result.get("details", {})
    outliers = details.get("outliers", {})
    
    if not outliers:
        return ""
    
    lines = ["\n**Обнаруженные выбросы:**"]
    lines.append("| Признак | Количество выбросов | Процент | Метод |")
    lines.append("|---------|-------------------|---------|-------|")
    for feature, stats in outliers.items():
        count = stats.get('count', 'N/A')
        percentage = stats.get('percentage', 'N/A')
        method = stats.get('method', 'N/A')
        lines.append(f"| {feature} | {count} | {percentage:.2f}% | {method} |")
    
    return "\n".join(lines)


def _format_interaction_details(result: Optional[Dict[str, Any]]) -> str:
    """Форматирует детали анализа взаимодействий."""
    if not result or result["status"] != "success":
        return ""
    
    details = result.get("details", {})
    interactions = details.get("interactions", [])
    
    if not interactions:
        return ""
    
    lines = ["\n**Анализ взаимодействий:**"]
    lines.append("| Признак | Тип | Значение | Метрика |")
    lines.append("|---------|-----|----------|---------|")
    for interaction in interactions:
        feature = interaction.get('feature', 'N/A')
        type_ = interaction.get('type', 'N/A')
        value = interaction.get('value', 'N/A')
        metric = interaction.get('metric', 'N/A')
        
        # Обработка значения в зависимости от метрики и типа
        if metric == "p_value":
            try:
                # Пробуем преобразовать в число для форматирования
                p_val = float(value)
                value_str = f"p={p_val:.2e}"
            except (ValueError, TypeError):
                # Если не удалось, оставляем как есть
                value_str = f"p={value}"
                
            chi2 = interaction.get('chi2')
            if chi2 is not None:
                try:
                    chi2_val = float(chi2)
                    value_str += f", χ²={chi2_val:.2f}"
                except (ValueError, TypeError):
                    value_str += f", χ²={chi2}"
        else:
            # Для корреляции и других метрик
            try:
                # Пробуем преобразовать в число для форматирования
                corr_val = float(value)
                value_str = f"{corr_val:.3f}"
            except (ValueError, TypeError):
                # Если не удалось, оставляем как есть
                value_str = f"{value}"
            
        lines.append(f"| {feature} | {type_} | {value_str} | {metric} |")
    
    return "\n".join(lines)



SUMMARIZER_PROMPT = """
Ты — эксперт по аналитике. На основе результатов инструментов сгенерируй отчёт.
Ты НЕ можешь выдумывать данные. Если раздел отсутствует — напиши "Нет данных".

Цель: ответить на вопрос: «Какие характеристики и паттерны поведения наиболее сильно отличают группу 1 от группы 0?»

Формат отчёта:
# Аналитический отчёт для файла {filename}

## Ключевые выводы
{insights_list}

## Детальный анализ
### 1. Поиск главного признака
{primary_feature_summary}

### 2. Корреляционный анализ
{correlation_summary}
{correlation_details}

### 3. Сравнение описательных статистик
{descriptive_stats_summary}
{stats_details}

### 4. Анализ категориальных признаков
{categorical_analysis_summary}
{categorical_details}

### 5. Анализ распределений
{visualization_summary}
{visualization_details}

### 6. Обнаружение выбросов
{outlier_summary}
{outlier_details}

### 7. Анализ взаимодействий
{interaction_summary}
{interaction_details}

### 8. Важность признаков из полной модели
{full_model_summary}
{model_details}

## Заключение
Сформулируй общий вывод на основе всех предыдущих разделов.
Объясни, какие характеристики и паттерны поведения наиболее сильно отличают группу 1 от группы 0.
Если данных недостаточно — напиши "Недостаточно данных".
"""


def generate_summary(
    insights: List[str], 
    tool_results: List[Dict[str, Any]], 
    filename: str = "unknown.csv"
) -> str:
    """Генерирует итоговый аналитический отчёт на основе результатов инструментов."""
    logger.info(f"📝 Summarizer Agent инициализирован для файла {filename}")

    llm = ChatOpenAI(
        model="qwen2.5-32b-instruct",
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        temperature=0.3
    )

    results_map = {res["tool_name"]: res for res in tool_results}

    def get_summary(name: str) -> str:
        res = results_map.get(name)
        return res["summary"] if res and res["status"] == "success" else "Нет данных"

    # Получаем полные результаты для деталей
    correlation_result = results_map.get("CorrelationAnalysis")
    stats_result = results_map.get("DescriptiveStatsComparator")
    categorical_result = results_map.get("CategoricalFeatureAnalysis")
    model_result = results_map.get("FullModelFeatureImportance")
    visualization_result = results_map.get("DistributionVisualizer")
    outlier_result = results_map.get("OutlierDetector")
    interaction_result = results_map.get("InteractionAnalyzer")

    insights_list = "\n".join([f"- {s}" for s in insights]) if insights else "Нет данных"

    prompt = ChatPromptTemplate.from_template(SUMMARIZER_PROMPT)
    chain = prompt | llm

    response = chain.invoke({
        "filename": filename,
        "insights_list": insights_list,
        "primary_feature_summary": get_summary("PrimaryFeatureFinder"),
        "correlation_summary": get_summary("CorrelationAnalysis"),
        "correlation_details": _format_correlation_details(correlation_result),
        "descriptive_stats_summary": get_summary("DescriptiveStatsComparator"),
        "stats_details": _format_stats_details(stats_result),
        "categorical_analysis_summary": get_summary("CategoricalFeatureAnalysis"),
        "categorical_details": _format_categorical_details(categorical_result),
        "visualization_summary": get_summary("DistributionVisualizer"),
        "visualization_details": _format_visualization_details(visualization_result),
        "outlier_summary": get_summary("OutlierDetector"),
        "outlier_details": _format_outlier_details(outlier_result),
        "interaction_summary": get_summary("InteractionAnalyzer"),
        "interaction_details": _format_interaction_details(interaction_result),
        "full_model_summary": get_summary("FullModelFeatureImportance"),
        "model_details": _format_model_details(model_result),
    })

    return response.content
