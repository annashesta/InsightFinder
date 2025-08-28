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
    """Форматирует визуализации для отчёта, используя пути к файлам."""
    if not result or result["status"] != "success":
        return ""
    
    details = result.get("details", {})
    saved_images = details.get("saved_images", {})
    
    if not saved_images:
        return ""
    
    lines = ["\n**Визуализации распределений:**"]
    for feature, image_data in saved_images.items():
        relative_path = image_data.get("relative_path", "")
        description = image_data.get("description", "")
        lines.append(f"\n### Распределение {feature}")
        lines.append(f"*{description}*")
        # Вставляем изображение по относительному пути
        if relative_path:
            lines.append(f"![{feature}]({relative_path})")
    
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


def _format_insight_visualization_details(result: Optional[Dict[str, Any]]) -> str:
    """Форматирует детали InsightDrivenVisualizer для отчёта."""
    if not result or result["status"] != "success":
        return ""
    
    details = result.get("details", {})
    saved_plots = details.get("saved_plots", {})
    
    if not saved_plots:
        return ""
    
    lines = ["\n**Инсайт-ориентированные визуализации:**"]
    for plot_key, plot_data in saved_plots.items():
        description = plot_data.get("description", "")
        lines.append(f"\n### {description}")
        
        # Добавляем пути к изображениям
        for plot_type, filepath in plot_data.items():
            if plot_type != "description" and filepath and isinstance(filepath, str) and filepath.endswith('.png'):
                # Извлекаем относительный путь для Markdown
                # Предполагаем, что файлы сохраняются в report/output/images/
                # filepath может быть, например: report/output/images/desc_MonthlyRevenue_min_boxplot.png
                # Нам нужен путь относительно report/output, т.е. images/desc_MonthlyRevenue_min_boxplot.png
                try:
                    # Находим индекс начала 'images/' в пути
                    images_idx = filepath.index('images/')
                    relative_path = filepath[images_idx:]
                except ValueError:
                    # Если 'images/' не найден, используем весь путь от report/output
                    try:
                        report_idx = filepath.index('report/output/')
                        relative_path = filepath[report_idx + len('report/output/'):]
                    except ValueError:
                        # Если и это не найдено, используем как есть
                        relative_path = filepath
                        
                lines.append(f"![{plot_key}_{plot_type}]({relative_path})")
    
    return "\n".join(lines)


SUMMARIZER_PROMPT = """
Ты — старший аналитик данных. Твоя задача — на основе предоставленных сырых данных и результатов работы инструментов (статистика, визуализации, модели) сгенерировать четкий, структурированный и исключительно точный аналитический отчет.

**Главный принцип: Все утверждения в отчете ДОЛЖНЫ иметь подтверждение в предоставленных данных. Запрещено выдумывать данные, дополнять своими или ссылаться на несуществующие графики.**

**Качество выводов: Итоговый отчет содержит нетривиальные и полезные выводы о данных. Избегай поверхностных или очевидных утверждений. Каждый вывод должен давать новое знание о структуре данных или взаимосвязях.**

**Проверка графиков:**
*   Перед тем как упомянуть или сослаться на график (например, "см. график boxplot_MonthlyRevenue"), ТЩАТЕЛЬНО ПРОВЕРЬ, присутствует ли путь к этому файлу в данных инструмента `DistributionVisualizer`, `InsightDrivenVisualizer` или других инструментов, которые генерируют графики.
*   **Ссылайся на график ТОЛЬКО если он действительно был создан и путь к нему указан в `details` соответствующего инструмента.**
*   Если данных о графике нет или путь отсутствует, **никак не упоминай этот график** в отчете.

**Формат данных:** Там, где это возможно и уместно (например, для перечисления корреляций, статистик, признаков), представляйте информацию в структурированном виде, таком как таблицы или маркированные списки с заголовками столбцов. Это облегчает восприятие и сравнение данных.

**Формат ссылок на графики:** Если график подтвержден, ссылайся на него по его относительному пути, например: `![Описание графика](images/boxplot_MonthlyRevenue.png)`. Используй Markdown-синтаксис для вставки изображений.
**ВАЖНО: подписывай каждый график его названием, чтобы человек сам смог его найти скачав zip с графиками (например Визуализация: cat_MadeCallToRetentionTeam_stacked_bar.png)**

**Цель исследования:** Выявить и описать ключевые характеристики и паттерны поведения, которые наиболее значительно дифференцируют группу 1 (целевая) от группы 0 (контрольная).

**Структура и требования к отчету:**

# Аналитический отчёт по данным из файла: {filename}

## Ключевые выводы
{insights_list}

### 1. Ключевой дифференцирующий признак
*   **{primary_feature_summary}**
*   Назови признак, который *наиболее сильно* различает группы согласно результатам анализа. Приведи конкретные значения (например, среднее значение признака в группе 1: X, в группе 0: Y). Проинтерпретируй, что это может означать в контексте исследования. **Если для этого признака есть подтвержденный график (например, boxplot), вставь его.**

### 2. Анализ корреляций
*   **{correlation_summary}**
*   **{correlation_details}**
*   Выдели только самые сильные и статистически значимые корреляции, имеющие отношение к целевой переменной.
*   Проинтерпретируй, что эти корреляции могут означать в контексте исследования. **Если есть подтвержденные графики (например, heatmap корреляций), вставь их.**

### 3. Сравнительный анализ статистик
*   **{descriptive_stats_summary}**
*   **{stats_details}**
*   Сравни основные метрики (среднее, медиана, стандартное отклонение и прочие) по ключевым непрерывным признакам между группами. Акцентируй внимание на признаках с наибольшей разницей. Проинтерпретируй, что эти различия могут означать. **Если есть подтвержденные графики (например, boxplots или histograms для этих признаков), вставь их.**

### 4. Анализ категориальных признаков
*   **{categorical_analysis_summary}**
*   **{categorical_details}**
*   Опиши, как распределяются категории между группами. Укажи, какие категории статистически значимо преобладают в группе 1 или группе 0 (например, "В группе 1 доля категории 'A' составляет 40%, что в 2 раза выше, чем в группе 0 (20%)"). **Если есть подтвержденные графики (например, stacked bar charts), вставь их.**

### 5. Анализ распределений и визуализация
*   **{visualization_summary}**
*   **{visualization_details}**
*   Интерпретируй предоставленные графики (например, гистограммы, boxplots). Опиши форму распределений, наличие мод и визуально заметные различия между группами. Укажи, на какие графики стоит обратить внимание и почему. **Вставь ТОЛЬКО те графики, которые подтверждены данными инструментов.**

### 6. Выбросы и аномалии
*   **{outlier_summary}**
*   **{outlier_details}**
*   Сообщите о наличии выбросов, если они обнаружены. Укажи, в какой группе и на каких признаках они сконцентрированы, и как это может повлиять на анализ. **Графики для этого раздела (если генерировались) также должны быть проверены и вставлены только при наличии подтверждения.**

### 7. Анализ взаимодействия признаков
*   **{interaction_summary}**
*   **{interaction_details}**
*   Опиши, если были обнаружены признаки, чье влияние на целевую переменную усиливается/ослабевает в зависимости от других факторов. **Если для иллюстрации были созданы графики (например, interaction plots), и они подтверждены, вставь их.** Если таких признаков нет или данные отсутствуют — пропусти этот пункт полностью.

### 8. Важность признаков (модель)
*   **{full_model_summary}**
*   **{model_details}**
*   Ранжируй признаки по их важности в предсказании принадлежности к группе, согласно результатам ML-модели. Проинтерпретируй, что это может означать. **Если есть подтвержденный график важности признаков (например, bar chart), вставь его.**

### 9. Инсайт-ориентированные визуализации
{insight_viz_summary}
{insight_viz_details}
**Вставь ТОЛЬКО те графики, которые были созданы инструментом `InsightDrivenVisualizer` и подтверждены в его `details`.**

## Заключение и рекомендации
*   **Синтез выводов:** Обобщи все вышесказанное, четко ответив на вопрос: «Какие характеристики и паттерны поведения наиболее сильно отличают группу 1 от группы 0?». Перечисли ТОП-3 признака.
*   **Следующие шаги:** На основе выводов предложи возможные направления для дальнейшего анализа или гипотезы для проверки.
** Важно:** Нельзя упоминать в отчёте инструменты, которые не использовались или не дали результатов. Например, если не было данных для анализа взаимодействий, просто не включай пункт 7 в итоговый отчёт, не упоминай его вообще. Соблюдай сквозную структуру (если исключил пункт 7, перенумеруй пункты, чтобы не было пропусков).
"""


def generate_summary(
    insights: List[str], 
    tool_results: List[Dict[str, Any]], 
    filename: str = "unknown.csv"
) -> str:
    """Генерирует итоговый аналитический отчёт на основе результатов инструментов."""
    logger.info(f"📝 Summarizer Agent инициализирован для файла {filename}")

    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL"),
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
    insight_viz_result = results_map.get("InsightDrivenVisualizer")

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
        # Новые поля для InsightDrivenVisualizer
        "insight_viz_summary": get_summary("InsightDrivenVisualizer"),
        "insight_viz_details": _format_insight_visualization_details(insight_viz_result),
    })

    return response.content
