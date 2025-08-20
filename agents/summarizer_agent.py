# agents/summarizer_agent.py
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from core.logger import get_logger

load_dotenv()
logger = get_logger(__name__, "summarizer.log")


def _format_categorical_details(result):
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


def _format_correlation_details(result):
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


def _format_stats_details(result):
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


def _format_model_details(result):
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

### 5. Важность признаков из полной модели
{full_model_summary}
{model_details}

## Заключение
Сформулируй общий вывод на основе всех предыдущих разделов.
Объясни, какие характеристики и паттерны поведения наиболее сильно отличают группу 1 от группы 0.
Если данных недостаточно — напиши "Недостаточно данных".
"""


def generate_summary(insights: list, tool_results: list, filename: str = "unknown.csv") -> str:
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
        "full_model_summary": get_summary("FullModelFeatureImportance"),
        "model_details": _format_model_details(model_result),
    })

    return response.content