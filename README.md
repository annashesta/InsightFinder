# InsightFinder
Аналитическая мультиагентная система «InsightFinder»
 
 🎯 Цель проекта
Разработать прототип мультиагентной системы на Python, которая автоматически проводит исследовательский анализ данных (EDA) для табличного датасета с бинарной целевой переменной и генерирует человекочитаемый аналитический отчёт в формате Markdown.

## Структура проекта

```
insightfinder/
│
├── data/                       # Папка с тестовыми и примерами CSV-файлов
│   └── telecom_eda_data.csv
│
├── tools/                      # Библиотека аналитических инструментов
│   ├── __init__.py
│   ├── primary_feature_finder.py
│   ├── correlation_analysis.py
│   ├── descriptive_stats_comparator.py
│   ├── categorical_feature_analysis.py
│   └── full_model_importance.py
│
├── agents/                     # Модули агентов
│   ├── __init__.py
│   ├── analyst_agent.py
│   ├── executor_agent.py
│   ├── summarizer_agent.py
│   └── tools_wrapper.py  # Обёртка для тулзов
│
├── core/                       # Ядро системы
│   ├── data_loader.py
│   └── orchestrator.py
│
├── report/                     # Генерация отчёта
│   ├── templates/
│   │   └── report_template.md.j2
│   └── generate_report.py
│
├── config/                     # Конфигурация
│   └── agent_prompts.py
│
├── tests/                      # Юнит-тесты
│   ├── test_tools.py
│   └── test_edge_cases.py
│
├── main.py                     # Точка входа
├── requirements.txt
└── README.md                   # Документация

```





### Общий интерфейс инструмента:

   - Все функции принимают `df: pd.DataFrame`, `target_column: str`, `**kwargs`.
    
	Где  pandas.DataFrame — полный набор данных. 
    target_column: str — имя столбца с целевой переменной. 
    *kwargs — опциональные параметры, специфичные для инструмента (например, feature_name: strдля анализа конкретного признака).

   - Возвращают словарь строго определённой структуры. Пример структуры выходного словаря:

```
      {
    "tool_name": "DecisionTreeSplitter", // Название инструмента
    "status": "success", // 'success' или 'error'
    "summary": "Признак 'Средний чек' является самым сильным предиктором с порогом 8500. Gain: 0.12.", // Краткий вывод для человека
    "details": { // Технические детали для других агентов или для отчета
        "best_feature": "Средний чек",
        "split_threshold": 8500.0,
        "information_gain": 0.12,
        "group_0_mean": 4300.0,
        "group_1_mean": 12100.0
    },
    "error_message": None // Сообщение в случае ошибки
}
```


2. **Реализованы 5 инструментов**:

| Инструмент | Описание | Библиотека |
|-----------|--------|----------|
| `PrimaryFeatureFinder` | Обучает `DecisionTreeClassifier(max_depth=1)` и возвращает лучший признак, порог, gain | `sklearn.tree` |
| `CorrelationAnalysis` | Считает корреляцию Пирсона между числовыми признаками и целевой переменной (после кодирования) | `pandas`, `numpy` |
| `DescriptiveStatsComparator` | Сравнивает mean, median, std по группам (0 и 1), возвращает признаки с разницей > 20% | `pandas` |
| `CategoricalFeatureAnalysis` | Для категориальных признаков — таблица сопряжённости + тест Хи-квадрат (`scipy.stats.chi2_contingency`) | `scipy` |
| `FullModelFeatureImportance` | Обучает `RandomForestClassifier` или `LGBM`, возвращает топ-10 важных признаков | `sklearn` / `lightgbm` |

3. **Обработка ошибок**:
   - Все инструменты возвращаают `status: "error"` и `error_message` при исключениях.


## Запуск тестов**

Выполните в терминале:

```bash
pytest tests/test_tools.py -v -s
```

+ дописать проручные тесты
+ дописать про негативные тесты

Создана мультиагентная система, где:

1. Аналитик планирует, какой инструмент запустить.
2. Исполнитель вызывает вашу функцию-тулз.
3. Система координирует их диалог.
4. Summarizer в конце генерирует отчёт.


# InsightFinder — Аналитическая мультиагентная система

## Описание
Система автоматически проводит EDA для табличных данных с бинарной целевой переменной и генерирует отчёт в формате Markdown.

## Технологии
- Python 3.9+
- LangChain
- qwen2.5-32b-instruct (через NeuralDeep)
- pandas, scikit-learn, scipy

## Запуск
1. Установите зависимости: `pip install -r requirements.txt`
2. Создайте `.env` с `OPENAI_API_KEY` и `OPENAI_BASE_URL`
3. Запустите: `python main.py`

## Структура
- `tools/` — аналитические инструменты
- `agents/` — агенты на LangChain
- `core/` — ядро системы
- `report/` — генерация отчёта
- `main.py` — точка входа
- `report.md` — итоговый отчёт

---

Надеюсь, не пригодится.

# Установка зависимостей:
Если по API используй
```
pip install langchain langchain-openai python-dotenv
```
Создай файл .env в корне проекта:
```
# .env
OPENAI_API_KEY=
OPENAI_BASE_URL=
```


Если Ollama
pip install langchain  langchain-ollama python-dotenv

Нужно будет изменить:
1.  agents/analyst.py и agents/summarizer.py
```
from langchain_ollama import ChatOllama  # ← вместо ChatOpenAI
```

2. agents/summarizer.py
from langchain_ollama import ChatOllama

```
def generate_summary(results: str, filename: str = "unknown.csv") -> str:
    prompt = ChatPromptTemplate.from_template(SUMMARIZER_PROMPT)
    llm = ChatOllama(model="llama3", temperature=0.3)
    chain = prompt | llm
    response = chain.invoke({"results": results, "filename": filename})
    return response.content
```


3. agents/executor.py тоже замени LLM
```
# agents/executor.py
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_ollama import ChatOllama  # ← здесь

def create_executor_agent(tools, analyst_prompt, analyst_llm):
    # Создаём агент с тулзами
    agent = create_openai_tools_agent(
        llm=ChatOllama(model="llama3", temperature=0),  # ← вместо ChatOpenAI
        tools=tools,
        prompt=analyst_prompt
    )
    return AgentExecutor(agent=agent, tools=tools, verbose=True)

```