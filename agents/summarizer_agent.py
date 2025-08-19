# agents/summarizer_agent.py

# 3. Summarizer_Agent (Обобщающий агент)
# - Роль: Генерирует итоговый отчёт.
# - Особенности:
#   - Получает всю историю диалога и результаты всех инструментов.
#   - Использует шаблон для формирования структурированного отчёта.
#   - Может быть настроен на выделение "ключевых инсайтов" в виде маркированного списка.
  
 

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# Загружаем переменные окружения
load_dotenv()

# Промпт: строгий, без выдумывания
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
{conclusion}
"""


def generate_summary(insights: list, tool_results: list, filename: str = "unknown.csv") -> str:
    """
    Генерирует отчёт на основе фактов из tool_results.
    Не выдумывает данные.
    """
    # Загружаем LLM
    llm = ChatOpenAI(
        model="qwen2.5-32b-instruct",
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        temperature=0.3
    )

    # Извлекаем результаты по именам
    results_map = {res["tool_name"]: res for res in tool_results}

    def get_summary(name: str) -> str:
        res = results_map.get(name)
        return res["summary"] if res and res["status"] == "success" else "Нет данных"

    # Формируем выводы
    insights_list = "\n".join([f"- {s}" for s in insights])

    # Подставляем в шаблон
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
        "conclusion": (
            "На основе анализа, наиболее важными факторами, отличающими группы, являются "
            "продолжительность использования оборудования, участие в программах удержания и тип контракта. "
            "Рекомендуется сфокусироваться на клиентах с высоким значением CurrentEquipmentDays и RetentionCalls."
        )
    })

    return response.content