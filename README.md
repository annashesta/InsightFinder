# InsightFinder
Аналитическая мультиагентная система «InsightFinder»
 
 🎯 Цель проекта
Разработать прототип мультиагентной системы на Python, которая автоматически проводит исследовательский анализ данных (EDA) для табличного датасета с бинарной целевой переменной и генерирует человекочитаемый аналитический отчёт в формате Markdown.

## Структура проекта

```
insightfinder/
│
├── data/                       # Папка с тестовыми и примерами CSV-файлов
│   └── test_data.csv
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
│   └── summarizer_agent.py
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
├── tests/                      # Юнит-тесты
│   ├── test_tools.py
│   └── test_agents.py
│
├── config/                     # Конфигурация
│   └── agent_prompts.py
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