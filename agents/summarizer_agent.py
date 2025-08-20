# agents/summarizer_agent.py
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from core.logger import get_logger

load_dotenv()
logger = get_logger(__name__, "summarizer.log")


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

### 3. Сравнение описательных статистик
{descriptive_stats_summary}

### 4. Анализ категориальных признаков
{categorical_analysis_summary}

### 5. Важность признаков из полной модели
{full_model_summary}

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

    insights_list = "\n".join([f"- {s}" for s in insights]) if insights else "Нет данных"

    prompt = ChatPromptTemplate.from_template(SUMMARIZER_PROMPT)
    chain = prompt | llm

    response = chain.invoke({
        "filename": filename,
        "insights_list": insights_list,
        "primary_feature_summary": get_summary("PrimaryFeatureFinder"),
        "correlation_summary": get_summary("CorrelationAnalysis"),
        "descriptive_stats_summary": get_summary("DescriptiveStatsComparator"),
        "categorical_analysis_summary": get_summary("CategoricalFeatureAnalysis"),
        "full_model_summary": get_summary("FullModelFeatureImportance"),
    })

    return response.content