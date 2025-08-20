# # core/orchestrator.py
# from typing import List, Dict
# from agents.tools_wrapper import ALL_TOOLS

# def run_analysis_pipeline(df, target_column: str) -> List[Dict]:
#     """
#     Запускает все аналитические инструменты и возвращает список результатов.
#     """
#     from agents.tools_wrapper import set_current_data
#     set_current_data(df, target_column)

#     results = []
#     for tool in ALL_TOOLS:
#         print(f"🔧 Запуск: {tool.name}")
#         try:
#             result = tool._run()
#             results.append(result)
#         except Exception as e:
#             results.append({
#                 "tool_name": tool.name,
#                 "status": "error",
#                 "summary": "",
#                 "details": {},
#                 "error_message": str(e)
#             })
#     return results


# orchestrator.py
from agents.analyst_agent import create_analyst_agent
from agents.tools_wrapper import set_current_data, ALL_TOOLS
from agents.executor_agent import ExecutorAgent
from langchain_core.messages import HumanMessage
import pandas as pd
import json
from core.logger import get_logger
from agents.summarizer_agent import generate_summary

logger = get_logger(__name__)

def run_simple_orchestration(df: pd.DataFrame, target_column: str, filename: str = "data.csv"):
    """
    Лёгкая версия оркестратора:
    - Загружает данные
    - Инициализирует аналитика
    - Получает его ответ
    """
     # 1. Загружаем данные в тулзы
    set_current_data(df, target_column)

    # 2. Создаём аналитика
    analyst = create_analyst_agent(ALL_TOOLS)
    executor = ExecutorAgent(tools=ALL_TOOLS)

    history = []   # история инструментов
    insights = []  # сюда можно собирать краткие инсайты (если нужны)

    while True:
        # === 1. Формируем промпт для аналитика ===
        if not history:
            question = f"""
            Ответь строго в формате JSON.
            Не используй Markdown-обёртку.

            Ты — аналитик-планировщик.
            Твоя задача: найти ключевые различия между группами по бинарной целевой переменной.

            На первом шаге выбери только ОДИН инструмент, с которого ты начнёшь анализ.

            Формат ответа:
            {{
              "logic": "Почему именно этот шаг выбирается первым.",
              "next_step": {{"tool": "<название инструмента>", "reason": "зачем его запускать"}}
            }}
            """
        else:
            question = f"""
            Ответь строго в формате JSON.
            Не используй Markdown-обёртку.

            Ты — аналитик-планировщик.
            У тебя уже есть результаты предыдущих инструментов, приложены ниже.

            Формат ответа:
            {{
              "logic": "Почему именно этот шаг выбирается сейчас (опираясь на результаты).",
              "next_step": {{"tool": "<название инструмента>", "reason": "зачем его запускать"}}
            }}

            ВАЖНО:
            - Никогда не придумывай результаты инструмента.
            - Если все необходимые шаги уже сделаны, вместо "next_step" верни:
              {{"tool": "STOP", "reason": "Все необходимые инструменты запущены."}}

            --- Результаты предыдущих шагов ---
            {json.dumps(history, ensure_ascii=False, indent=2)}
            """

        # === 2. Ответ аналитика ===
        response = analyst.invoke({
            "messages": [HumanMessage(content=question)],
            "agent_scratchpad": []
        })

        print("=== Итоговый ответ аналитика ===")
        print(response)

        # === 3. Парсим JSON ===
        try:
            parsed = json.loads(response.content)
            step = parsed["next_step"]
        except Exception as e:
            print("❌ Ошибка парсинга ответа аналитика:", e)
            break

        # === 4. Проверка на STOP ===
        if step["tool"] == "STOP":
            print("✅ Анализ завершён.")
            break

        # === 5. Запуск исполнителя ===
        result = executor.run_one_step(step["tool"], df=df, target_column=target_column)

        print("=== Результат Исполнителя ===")
        print(result)

        # === 6. Сохраняем результат ===
        history.append({
            "tool_name": result["tool_name"],
            "status": result["status"],
            "summary": result["summary"],
            "details": result["details"]
        })

        # (опционально) можно извлекать инсайты из summary и класть в insights
        insights.append(result["summary"])

    # === 7. Генерация отчёта через SummarizerAgent ===
    final_report = generate_summary(
        insights=insights,
        tool_results=history,
        filename=filename
    )

    return history, final_report

def run_one_step(analyst, executor: ExecutorAgent, df, target_column):
    # 1. Получаем решение от Analyst
    response = analyst.invoke({
        "messages": [
            {"role": "user", "content": "Выбери следующий шаг анализа в JSON"}
        ],
        "agent_scratchpad": []
    })
    
    try:
        step = json.loads(response.content)["next_step"]
    except Exception as e:
        logger.error(f"Ошибка парсинга ответа аналитика: {response.content}")
        return None, {"status": "error", "error_message": str(e)}

    tool_name = step.get("tool")
    args = {"df": df, "target_column": target_column}

    # 2. Отправляем шаг в Executor
    result = executor.run_one_step(tool_name, **args)

    return step, result