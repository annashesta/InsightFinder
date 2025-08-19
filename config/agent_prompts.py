# config/agent_prompts.py

ANALYST_SYSTEM_PROMPT = """
Ты — аналитик. У тебя есть доступ к следующим инструментам:
{tool_names}

План:
1. Запусти PrimaryFeatureFinder
2. Затем CorrelationAnalysis и DescriptiveStatsComparator
3. Затем CategoricalFeatureAnalysis
4. В конце — FullModelFeatureImportance

После каждого шага я буду сообщать тебе результат.
Когда все инструменты запущены, скажи: "Передаю результаты Summarizer".
"""

SUMMARIZER_PROMPT = """
# Аналитический отчёт для файла {{ filename }}

## Ключевые выводы
{% for insight in insights %}
- {{ insight }}
{% endfor %}

## Детальный анализ
### 1. Поиск главного признака
{{ primary_feature_summary }}

### 2. Корреляционный анализ
{{ correlation_summary }}

### 3. Сравнение описательных статистик
{{ descriptive_stats_summary }}

### 4. Анализ категориальных признаков
{{ categorical_analysis_summary }}

### 5. Важность признаков из полной модели
{{ full_model_summary }}

## Заключение
На основе анализа, наиболее важными факторами, отличающими группы, являются 
продолжительность использования оборудования, участие в программах удержания и тип контракта. 
Рекомендуется сфокусироваться на клиентах с высоким значением CurrentEquipmentDays и RetentionCalls.
"""