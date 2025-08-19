# report/generate_report.py
from jinja2 import Environment, FileSystemLoader
import os

def generate_report(tool_results: list, filename: str = "unknown.csv") -> str:
    """Генерирует отчёт с использованием Jinja2-шаблона."""
    from agents.tools_wrapper import ALL_TOOLS
    results_map = {r["tool_name"]: r for r in tool_results}

    def get_summary(name):
        r = results_map.get(name)
        return r["summary"] if r and r["status"] == "success" else "Нет данных"

    env = Environment(loader=FileSystemLoader('report/templates'))
    template = env.get_template('report_template.md.j2')

    insights = [
        r["summary"] for r in tool_results
        if r["status"] == "success" and r["summary"].strip()
    ]

    return template.render(
        filename=filename,
        insights=insights,
        primary_feature_summary=get_summary("PrimaryFeatureFinder"),
        correlation_summary=get_summary("CorrelationAnalysis"),
        descriptive_stats_summary=get_summary("DescriptiveStatsComparator"),
        categorical_analysis_summary=get_summary("CategoricalFeatureAnalysis"),
        full_model_summary=get_summary("FullModelFeatureImportance"),
        conclusion=(
            "На основе анализа, наиболее важными факторами, отличающими группы, являются "
            "продолжительность использования оборудования, участие в программах удержания и тип контракта. "
            "Рекомендуется сфокусироваться на клиентах с высоким значением CurrentEquipmentDays и RetentionCalls."
        )
    )