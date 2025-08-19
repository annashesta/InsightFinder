# main.py

# "Поскольку сервер API не поддерживает tool_choice="auto", для оркестрации агентов был реализован кастомный цикл, 
# в котором Аналитик выбирает инструмент по имени, 
# а Исполнитель вызывает соответствующую функцию. 
# Это обеспечивает полный контроль над процессом и гарантирует работу системы."

import pandas as pd
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from agents.tools_wrapper import set_current_data, ALL_TOOLS
from agents.summarizer_agent import generate_summary
import os

load_dotenv()

# Загрузка данных
df = pd.read_csv("data/telecom_eda_data.csv")
set_current_data(df, "Churn")

# LLM
llm = ChatOpenAI(
    model="qwen2.5-32b-instruct",
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
    temperature=0.0
)

# Промпт для Аналитика
prompt = ChatPromptTemplate.from_messages([
    ("system", """
Ты — аналитик. У тебя есть доступ к следующим инструментам:
{tool_names}

План:
1. Запусти PrimaryFeatureFinder
2. Затем CorrelationAnalysis и DescriptiveStatsComparator
3. Затем CategoricalFeatureAnalysis
4. В конце — FullModelFeatureImportance

После каждого шага я буду сообщать тебе результат.
Когда все инструменты запущены, скажи: "Передаю результаты Summarizer".
"""),
    ("placeholder", "{messages}")
])

# Словарь: имя тулза → функция
tool_map = {tool.name: tool._run for tool in ALL_TOOLS}
tool_names = ", ".join(tool_map.keys())

# История диалога
messages = [{"role": "user", "content": f"Начни анализ. Доступные инструменты: {tool_names}"}]

# Цикл анализа
results = []
for _ in range(6):  # Максимум 6 шагов
    chain = prompt | llm
    response = chain.invoke({"tool_names": tool_names, "messages": messages})
    msg = response.content.strip()
    print(f"🧠 Аналитик: {msg}")

    # Если хочет передать отчёт
    if "summarizer" in msg.lower() or "все инструменты" in msg.lower():
        break

    # Поиск, какой тулз нужно запустить
    chosen_tool = None
    for name in tool_map:
        if name in msg:
            chosen_tool = name
            break

    if chosen_tool:
        print(f"🔧 Запуск: {chosen_tool}")
        result = tool_map[chosen_tool]()
        results.append(f"### {chosen_tool}\n{result}")
        messages.append({"role": "assistant", "content": msg})
        messages.append({"role": "user", "content": f"Результат выполнения {chosen_tool}:\n{result}"})
    else:
        messages.append({"role": "assistant", "content": msg})
        messages.append({"role": "user", "content": "Не удалось определить, какой инструмент запустить. Уточни."})

# Генерация отчёта
full_results = "\n\n".join(results)
summary = generate_summary(full_results, "telecom_eda_data.csv")

with open("report.md", "w", encoding="utf-8") as f:
    f.write(summary)

print("✅ Отчёт сгенерирован: report.md")