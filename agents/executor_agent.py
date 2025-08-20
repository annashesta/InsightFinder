# agents/executor_agent.py
from langchain.agents import AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent

from core.logger import get_logger

logger = get_logger(__name__)


class ExecutorAgent:
    """
    Исполнитель: вызывает инструменты по имени.
    Здесь нет LLM, только маппинг tool_name -> функция.
    """

    def __init__(self, tools):
        self.tools = {t.name: t for t in tools}
        logger.info(f"Executor Agent инициализирован с {len(tools)} инструментами")

    def run_one_step(self, tool_name: str, **kwargs):
        """
        Выполнить один шаг: вызвать инструмент по имени
        """
        if tool_name not in self.tools:
            raise ValueError(f"Инструмент {tool_name} не найден среди доступных")

        tool = self.tools[tool_name]
        logger.info(f"🚀 Запуск инструмента: {tool_name}")
        return tool.run(tool_input="", **kwargs)
