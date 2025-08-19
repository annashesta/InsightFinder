# agents/analyst_agent.py

# Analyst_Agent (Аналитик)
# - Роль: Планирует последовательность анализа.
# - Особенности:
#   - Использует `AssistantAgent`.
#   - Получает промпт с описанием целевой задачи: *"Найди ключевые различия между группами по бинарной целевой переменной."*
#   - Принимает решения: какой инструмент запустить следующим, основываясь на предыдущих результатах.
#   - Пример логики:  
#     *"Сначала запусти PrimaryFeatureFinder, чтобы найти главный признак. Затем CorrelationAnalysis, чтобы понять линейные связи. После — CategoricalFeatureAnalysis для категориальных данных."    

# agents/analyst_agent.py
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# Загружаем переменные окружения
load_dotenv()

# Промпт для Аналитика
ANALYST_SYSTEM_PROMPT = """Ты — опытный аналитик данных. Твоя задача — исследовать различия между двумя группами по бинарной целевой переменной.
Ты НЕ можешь писать код. Ты можешь только выбирать, какой из доступных инструментов запустить, чтобы получить инсайт.

Доступные инструменты:
{tools}

План:
1. Начни с PrimaryFeatureFinder — чтобы найти самый важный признак.
2. Затем используй CorrelationAnalysis и DescriptiveStatsComparator для числовых признаков.
3. Затем CategoricalFeatureAnalysis для категориальных.
4. В конце — FullModelFeatureImportance для итоговой оценки.

Не запускай один и тот же инструмент дважды.
Когда все ключевые инсайты получены, скажи: "Все необходимые инструменты запущены. Передаю результаты Summarizer."
"""

def create_analyst_agent(tools):
    """
    Создаёт промпт и LLM для Analyst'а.
    Важно: промпт должен включать MessagesPlaceholder для {agent_scratchpad}
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", ANALYST_SYSTEM_PROMPT.format(tools="\n".join([f"- {t.name}: {t.description}" for t in tools]))),
        ("placeholder", "{messages}"),  # Здесь будут user и assistant сообщения
        MessagesPlaceholder(variable_name="agent_scratchpad")  # Критически важно!
    ])
    llm = ChatOpenAI(
        model="qwen2.5-32b-instruct",
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        temperature=0.3,
        max_tokens=4096
    )
    return {"prompt": prompt, "llm": llm}