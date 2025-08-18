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

# Загружаем переменные из .env
load_dotenv()

SUMMARIZER_PROMPT = """
Ты — эксперт по аналитике. На основе результатов нескольких инструментов сгенерируй человекочитаемый отчёт в формате Markdown.

Цель: ответить на вопрос: «Какие характеристики и паттерны поведения наиболее сильно отличают группу 1 от группы 0?»

Результаты инструментов:
{results}

Формат отчёта:
# Аналитический отчёт для файла {filename}

## Ключевые выводы
- ...

## Детальный анализ
### 1. Поиск главного признака
...

### 2. Корреляционный анализ
...

### 3. Сравнение описательных статистик
...

### 4. Анализ категориальных признаков
...

### 5. Важность признаков из полной модели
...

## Заключение
...
"""


def generate_summary(results: str, filename: str = "unknown.csv") -> str:
    """
    Генерирует итоговый отчёт на основе результатов анализа.
    """
    prompt = ChatPromptTemplate.from_template(SUMMARIZER_PROMPT)
    llm = ChatOpenAI(
        model="qwen2.5-32b-instruct",
        api_key=os.getenv("OPENAI_API_KEY"),           # ← из .env
        base_url=os.getenv("OPENAI_BASE_URL"),         # ← из .env
        temperature=0.3
    )
    chain = prompt | llm
    response = chain.invoke({"results": results, "filename": filename})
    return response.content