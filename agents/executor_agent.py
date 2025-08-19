# agents/executor_agent.py

#Executor_Agent (Исполнитель)
# - Роль: Выполняет вызовы Python-функций (инструментов).
# - Особенности:
#   - Должен иметь доступ к функциям из `tools/`.
#   - Использует `UserProxyAgent` из AutoGen с `function_map`.
#   - Настройка: `allow_code_execution=True`, `code_execution_config`.


# agents/executor_agent.py
from langchain.agents import AgentExecutor
from langchain_openai import ChatOpenAI
from langchain import hub
from langchain.agents import create_tool_calling_agent


def create_executor_agent(tools, analyst_prompt, analyst_llm):
    """
    Используем create_tool_calling_agent — более современный и надёжный способ
    """
    # Создаём агент с явной поддержкой вызова тулзов
    agent = create_tool_calling_agent(
        llm=analyst_llm,
        tools=tools,
        prompt=analyst_prompt
    )

    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=15
    )
    
    