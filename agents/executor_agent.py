# agents/executor_agent.py
from core.logger import get_logger
from core.utils import make_serializable

logger = get_logger(__name__, "executor.log")


class ExecutorAgent:
    def __init__(self, tools):
        self.tools = {t.name: t for t in tools}
        logger.info(f"Executor Agent инициализирован с {len(tools)} инструментами")

    def run_one_step(self, tool_name: str, **kwargs):
        if tool_name not in self.tools:
            raise ValueError(f"Инструмент {tool_name} не найден")

        tool = self.tools[tool_name]
        logger.info(f"🚀 Запуск инструмента: {tool_name}")
        
        # Передаем все доступные kwargs, включая df, target_column и history
        try:
            result = tool.run(tool_input="", **kwargs)
            logger.info(f"✅ Инструмент {tool_name} успешно выполнен")
        except Exception as e:
            logger.error(f"❌ Ошибка при выполнении инструмента {tool_name}: {e}")
            result = {
                "tool_name": tool_name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": str(e)
            }
        return make_serializable(result)
