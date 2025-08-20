# core/orchestrator.py
import json
from typing import Tuple, List, Dict, Any

import pandas as pd
from langchain_core.messages import HumanMessage

from agents.analyst_agent import create_analyst_agent
from agents.executor_agent import ExecutorAgent
from agents.summarizer_agent import generate_summary
from agents.tools_wrapper import set_current_data, ALL_TOOLS
from core.logger import get_logger
from core.utils import make_serializable

logger = get_logger(__name__, "orchestrator.log")


def run_simple_orchestration(
    df: pd.DataFrame, 
    target_column: str, 
    filename: str = "data.csv"
) -> Tuple[List[Dict[str, Any]], str]:
    """
    Основной оркестратор: работает с JsonOutputParser.
    
    Args:
        df: DataFrame с данными для анализа
        target_column: Название целевой переменной
        filename: Имя файла данных для отчета
        
    Returns:
        Кортеж из истории выполнения инструментов и финального отчета
    """
    logger.info("Установка данных для инструментов")
    set_current_data(df, target_column)

    analyst = create_analyst_agent(ALL_TOOLS)
    executor = ExecutorAgent(ALL_TOOLS)
    logger.info("Агенты инициализированы")

    history: List[Dict[str, Any]] = []
    insights: List[str] = []

    step_num = 1
    max_steps = 20
    while step_num <= max_steps:
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
            response = analyst.invoke({
                "messages": [HumanMessage(content=question)],
                "agent_scratchpad": []
            })
            logger.info(f"✅ Analyst вернул: {response}")
        except Exception as e:
            logger.error(f"❌ Ошибка вызова Analyst: {e}")
            step_num += 1
            continue

        # Парсим ответ с проверкой структуры
        next_step_data = None
        try:
            if isinstance(response, dict):
                if "next_step" in response and isinstance(response["next_step"], dict):
                    next_step_data = response["next_step"]
                elif "tool" in response and "reason" in response:
                    logger.warning("Analyst вернул next_step напрямую, а не в поле 'next_step'. Используем как есть.")
                    next_step_data = response
                else:
                    logger.error(f"❌ Неверная структура ответа Analyst: {response}")
            else:
                logger.error(f"❌ Ответ Analyst не является словарем: {response}")

        except Exception as e:
            logger.error(f"❌ Неожиданная ошибка при парсинге ответа Analyst: {e}")

        if not next_step_data:
            logger.warning("Не удалось извлечь next_step. Пропускаем шаг.")
            step_num += 1
            continue
            
        try:
            tool_name = next_step_data["tool"]
            logger.info(f"🔍 Analyst выбрал: {tool_name}")
        except KeyError:
            logger.error(f"❌ В next_step отсутствует ключ 'tool': {next_step_data}")
            step_num += 1
            continue

        # STOP
        if tool_name.upper() == "STOP":
            logger.info(f"✅ Анализ завершён: {next_step_data.get('reason', 'Окончание')}")
            break

        # Запуск инструмента
        # Подготавливаем аргументы: основные + история для специфических инструментов
        tool_kwargs = {
            "df": df,
            "target_column": target_column
        }
            
        try:
            result = executor.run_one_step(tool_name, **tool_kwargs)
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

        # Сохранение результата
        history.append({
            "tool_name": result["tool_name"],
            "status": result["status"],
            "summary": result["summary"],
            "details": make_serializable(result["details"]),
        })

        if result["status"] == "success":
            insights.append(result["summary"])

        step_num += 1
    else:
        logger.warning(f"Достигнут лимит шагов ({max_steps}). Принудительная остановка.")

    # Автоматический запуск InsightDrivenVisualizer
    logger.info("🔍 Автоматический запуск InsightDrivenVisualizer")
    try:
        # Импортируем функцию прямо здесь, чтобы избежать циклических импортов
        from tools.insight_driven_visualizer import insight_driven_visualizer

        # Вызываем инструмент напрямую, передавая ему историю
        insight_result = insight_driven_visualizer(
            df=df,
            target_column=target_column,
            analysis_results=history, # Передаем всю историю
            output_dir="report/output/images"
        )
        # Добавляем результат в историю, как будто его выполнил агент
        history.append({
            "tool_name": insight_result["tool_name"],
            "status": insight_result["status"],
            "summary": insight_result["summary"],
            "details": make_serializable(insight_result["details"]),
        })
        if insight_result["status"] == "success":
            insights.append(insight_result["summary"])
        logger.info(f"✅ InsightDrivenVisualizer выполнен: статус={insight_result['status']}")
    except Exception as e:
        logger.error(f"❌ Ошибка при автоматическом запуске InsightDrivenVisualizer: {e}")
        # Можно добавить фейковый результат об ошибке, если нужно
        # history.append({...})

    # Генерация отчёта
    logger.info("📝 Генерация итогового отчёта")
    final_report = generate_summary(insights=insights, tool_results=history, filename=filename)

    return history, final_report
