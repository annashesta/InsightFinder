# core/orchestrator.py
from agents.analyst_agent import create_analyst_agent
from agents.executor_agent import ExecutorAgent
from agents.tools_wrapper import set_current_data, ALL_TOOLS
from langchain_core.messages import HumanMessage
import pandas as pd
import json
from core.logger import get_logger
from agents.summarizer_agent import generate_summary
from core.utils import make_serializable

logger = get_logger(__name__, "orchestrator.log")


def run_simple_orchestration(
    df: pd.DataFrame, target_column: str, filename: str = "data.csv"
) -> tuple[list[dict], str]:
    """
    Основной оркестратор: работает с JsonOutputParser.
    """
    logger.info("Установка данных для инструментов")
    set_current_data(df, target_column)

    analyst = create_analyst_agent(ALL_TOOLS)
    executor = ExecutorAgent(ALL_TOOLS)
    logger.info("Агенты инициализированы")

    history = []
    insights = []

    step_num = 1
    while True:
        logger.info(f"Шаг {step_num}: запрос к Analyst Agent")

        if not history:
            question = "Начни анализ с PrimaryFeatureFinder."
        else:
            serializable_history = make_serializable(history)
            history_json = json.dumps(serializable_history, ensure_ascii=False, indent=2)
            question = (
                "Учитывай предыдущие результаты.\n\n"
                f"--- Результаты предыдущих шагов ---\n{history_json}"
            )

        try:
            # ❌ response = analyst.invoke(...).content
            # ✅ response — это dict, не AIMessage
            response = analyst.invoke({
                "messages": [HumanMessage(content=question)],
                "agent_scratchpad": []
            })
            logger.info(f"✅ Analyst вернул: {response}")
        except Exception as e:
            logger.error(f"❌ Ошибка вызова Analyst: {e}")
            break

        # === Парсим ответ ===
        try:
            # response — это dict, а не строка
            next_step = response["next_step"]
            tool_name = next_step["tool"]
            logger.info(f"🔍 Analyst выбрал: {tool_name}")
        except Exception as e:
            logger.error(f"❌ Ошибка извлечения next_step: {e}")
            break

        # === STOP ===
        if tool_name.upper() == "STOP":
            logger.info(f"✅ Анализ завершён: {next_step.get('reason', 'Окончание')}")
            break

        # === Запуск инструмента ===
        try:
            result = executor.run_one_step(tool_name, df=df, target_column=target_column)
            logger.info(f"🚀 Executor выполнил {tool_name}: статус={result['status']}")
            if result["status"] == "error":
                logger.error(f"❌ Ошибка: {result['error_message']}")
        except Exception as e:
            logger.error(f"❌ Исключение при выполнении {tool_name}: {e}")
            result = {
                "tool_name": tool_name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": str(e),
            }

        # === Сохранение результата ===
        history.append({
            "tool_name": result["tool_name"],
            "status": result["status"],
            "summary": result["summary"],
            "details": make_serializable(result["details"]),
        })

        if result["status"] == "success":
            insights.append(result["summary"])

        step_num += 1

    # === Генерация отчёта ===
    logger.info("📝 Генерация итогового отчёта")
    final_report = generate_summary(insights=insights, tool_results=history, filename=filename)

    return history, final_report