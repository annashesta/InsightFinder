# agents/executor_agent.py

#Executor_Agent (Исполнитель)
# - Роль: Выполняет вызовы Python-функций (инструментов).
# - Особенности:
#   - Должен иметь доступ к функциям из `tools/`.
#   - Использует `UserProxyAgent` из AutoGen с `function_map`.
#   - Настройка: `allow_code_execution=True`, `code_execution_config`.



from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# Загружаем переменные из .env
load_dotenv()


def create_executor_agent(tools, analyst_prompt, analyst_llm):
    """
    Создаёт исполнительного агента, который вызывает тулзы.
    Использует create_openai_tools_agent, но работает с любым OpenAI-совместимым API.
    """
    # Создаём агент с вашей моделью и промптом
    agent = create_openai_tools_agent(
        llm=ChatOpenAI(
            model="qwen2.5-32b-instruct",
            api_key=os.getenv("OPENAI_API_KEY"),           # ← из .env
            base_url=os.getenv("OPENAI_BASE_URL"),         # ← из .env
            temperature=0.0  # Низкая температура для точности
        ),
        tools=tools,
        prompt=analyst_prompt
    )
    # Возвращаем исполнителя
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)