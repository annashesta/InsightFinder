# agents/analyst_agent.py
import os
from typing import List

from dotenv import load_dotenv
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from core.logger import get_logger

load_dotenv()
logger = get_logger(__name__)


class NextStep(BaseModel):
    """Модель для описания следующего шага."""
    tool: str = Field(description="Название инструмента или 'STOP'")
    reason: str = Field(description="Зачем он нужен")


class AnalystResponse(BaseModel):
    """Модель для ответа аналитика."""
    logic: str = Field(description="Обоснование выбора шага")
    next_step: NextStep


# === Промпт БЕЗ фигурных скобок и JSON-примеров ===
# Внимание: тройные фигурные скобки {{{...}}} используются для экранирования JSON-примера
# в f-string шаблоне LangChain. Это НЕ ошибка.
ANALYST_SYSTEM_PROMPT = """Ты — опытный аналитик данных. Твоя задача — исследовать различия между двумя группами по бинарной целевой переменной.
Ты НЕ можешь писать код. Ты можешь только выбирать, какой из доступных инструментов запустить, чтобы получить инсайт.

Доступные инструменты:
{tools}

План:
1. Начни с PrimaryFeatureFinder — чтобы найти самый важный признак.
2. Затем используй CorrelationAnalysis и DescriptiveStatsComparator для числовых признаков.
3. Затем CategoricalFeatureAnalysis для категориальных.
4. Добавь DistributionVisualizer для визуализации распределений.
5. Используй OutlierDetector для поиска аномалий.
6. Примени InteractionAnalyzer для анализа взаимодействий.
7. В конце — FullModelFeatureImportance для итоговой оценки.

Правила:
- Отвечай ТОЛЬКО в строгом JSON-формате.
- Не используй Markdown, XML, HTML или теги вроде    <think> .
- Формат ответа: объект с полями "logic" и "next_step", где next_step содержит "tool" и "reason".
- Если все шаги сделаны, верни: {{{{"tool": "STOP", "reason": "Все необходимые инструменты запущены."}}}}

Не запускай один и тот же инструмент дважды.
Всегда возвращай объект с полями "logic" и "next_step". Никогда не возвращай "tool" и "reason" напрямую без обертки в "next_step".
"""


def create_analyst_agent(tools: List) -> callable:
    """
    Создаёт Analyst Agent с LLM, промптом и JSON-парсером.

    Args:
        tools: Список доступных инструментов.

    Returns:
        Цепочка вызовов (prompt | llm | parser).
    """
    logger.info("Analysis Agent инициализирован")

    parser = JsonOutputParser(pydantic_object=AnalystResponse)

    prompt = ChatPromptTemplate.from_messages([
        ("system", ANALYST_SYSTEM_PROMPT.format(
            tools="\n".join([f"- {t.name}: {t.description}" for t in tools])
        )),
        ("placeholder", "{messages}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]).partial(format_instructions=parser.get_format_instructions())

    llm = ChatOpenAI(
        model="qwen2.5-32b-instruct",
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        temperature=0.3,
        max_tokens=4096
    )

    return prompt | llm | parser
