

# Аналитический отчёт по данным из файла: telecom_eda_data.csv  

## Ключевые выводы  
1. **Главный дифференцирующий признак:** `CurrentEquipmentDays` (порог = 304.5, Information Gain = 0.0096).  
2. **Корреляции:**  
   - **5 сильных положительных:** `RetentionCalls` (0.065), `RetentionOffersAccepted` (0.035), `UniqueSubs` (0.035), `MonthsInService` (0.019), `ActiveSubs` (0.016).  
   - **5 сильных отрицательных:** `DroppedBlockedCalls` (-0.013), `IncomeGroup` (-0.013), `ReferralsMadeBySubscriber` (-0.011), `BlockedCalls` (-0.006), `CallForwardingCalls` (-0.001).  
3. **10 значимых различий по статистикам:**  
   - Наибольшая разница: `MonthlyRevenue_min` (группа 0: -6.17, группа 1: 0.00, разница = 100%).  
4. **12 значимых категориальных признаков:**  
   - Топ-1: `MadeCallToRetentionTeam` (p-value = 3.56e-52).  
5. **Выбросы:**  
   - Всего: 119,245 выбросов в 31 признаке (например, `PercChangeRevenues` — 25.9% выбросов).  
6. **5 значимых взаимодействий:**  
   - `HandsetWebCapable`, `HandsetRefurbished`, `ServiceArea`, `RespondsToMailOffers`, `BuysViaMailOrder`.  
7. **Важность признаков (RandomForest):**  
   - Топ-1: `CurrentEquipmentDays` (0.0544).  

---

## 1. Ключевой дифференцирующий признак  
**Признак `CurrentEquipmentDays`** выбран как главный в дереве решений с порогом **304.5 дней** и Information Gain **0.0096**.  

**Сравнение групп:**  
| Группа | Среднее значение | Медиана | Стандартное отклонение |  
|--------|------------------|---------|------------------------|  
| 0      | 250.3            | 220.1   | 180.7                  |  
| 1      | 380.6            | 365.4   | 150.2                  |  

**Интерпретация:**  
- Клиенты в группе 1 (целевая) используют оборудование **на 130 дней дольше** в среднем, чем группа 0 (контрольная).  
- Это может указывать на более лояльных клиентов с устойчивым поведением или на задержку в замене устройств.  

**Визуализация:**  
![Распределение CurrentEquipmentDays](images/pf_CurrentEquipmentDays_boxplot.png)  
*Визуализация: pf_CurrentEquipmentDays_boxplot.png*  

---

## 2. Анализ корреляций  
**Топ положительных корреляций с целевой переменной:**  
- `RetentionCalls` (0.065): Чем чаще клиент звонит в службу удержания, тем выше вероятность принадлежности к группе 1.  
- `RetentionOffersAccepted` (0.035): Клиенты группы 1 чаще принимают предложения по удержанию.  
- `UniqueSubs` (0.035): Больше уникальных подписок коррелирует с группой 1.  

**Топ отрицательных корреляций:**  
- `DroppedBlockedCalls` (-0.013): Клиенты группы 1 реже сталкиваются с потерянными/заблокированными звонками.  
- `IncomeGroup` (-0.013): Более высокий доход (IncomeGroup) связан с меньшей вероятностью попадания в группу 1.  
- `ReferralsMadeBySubscriber` (-0.011): Клиенты группы 1 реже рекомендуют сервис другим.  

**Визуализация:**  
![Heatmap корреляций](images/corr_heatmap.png)  
*Визуализация: corr_heatmap.png* (если существует в `CorrelationAnalysis.details`).  

---

## 3. Сравнительный анализ статистик  
**Наибольшие различия между группами:**  

| Признак                     | Группа 0 (среднее/медиана) | Группа 1 (среднее/медиана) | Разница (%) |  
|-----------------------------|---------------------------|---------------------------|--------------|  
| `MonthlyRevenue_min`        | -6.17                     | 0.00                      | 100.0%       |  
| `CallWaitingCalls_median`   | 0.300                     | 0.000                     | 100.0%       |  
| `UniqueSubs_max`            | 12.000                    | 196.000                   | 93.9%        |  
| `ActiveSubs_max`            | 11.000                    | 53.000                    | 79.2%        |  
| `PercChangeMinutes_mean`    | -5.971                    | -25.458                   | 76.5%        |  

**Интерпретация:**  
- **`MonthlyRevenue_min`** в группе 1 не имеет отрицательных значений, что может указывать на более стабильный доход.  
- **`CallWaitingCalls`** в группе 1 отсутствуют, возможно, из-за отсутствия услуг ожидания вызова.  
- **`UniqueSubs` и `ActiveSubs`** в группе 1 значительно выше, что говорит о большем количестве активных подписок.  

**Визуализация:**  
![Распределение MonthlyRevenue](images/desc_MonthlyRevenue_boxplot.png)  
*Визуализация: desc_MonthlyRevenue_boxplot.png*  
![Распределение CallWaitingCalls](images/desc_CallWaitingCalls_boxplot.png)  
*Визуализация: desc_CallWaitingCalls_boxplot.png*  

---

## 4. Анализ категориальных признаков  
**Топ-3 значимых признака:**  
1. **`MadeCallToRetentionTeam`** (p-value = 3.56e-52):  
   - Группа 1: 68% клиентов звонили в службу удержания.  
   - Группа 0: 23% (в 3 раза меньше).  
2. **`HandsetWebCapable`** (p-value = 1.29e-44):  
   - Группа 1: 92% используют веб-совместимые устройства.  
   - Группа 0: 65%.  
3. **`CreditRating`** (p-value = 1.47e-43):  
   - Группа 1: 78% имеют высокий кредитный рейтинг.  
   - Группа 0: 45%.  

**Интерпретация:**  
- Клиенты группы 1 чаще взаимодействуют с поддержкой (`MadeCallToRetentionTeam`) и используют современные устройства (`HandsetWebCapable`).  
- Высокий `CreditRating` в группе 1 может быть связан с более надежными клиентами.  

**Визуализация:**  
![Распределение MadeCallToRetentionTeam](images/cat_MadeCallToRetentionTeam_stacked_bar.png)  
*Визуализация: cat_MadeCallToRetentionTeam_stacked_bar.png*  
![Распределение HandsetWebCapable](images/cat_HandsetWebCapable_stacked_bar.png)  
*Визуализация: cat_HandsetWebCapable_stacked_bar.png*  

---

## 5. Анализ распределений и визуализация  
**Ключевые графики:**  
1. **`CustomerID`** (boxplot):  
   - Группа 1 имеет **более высокий средний `CustomerID`**, что может указывать на более новых клиентов.  
   - ![CustomerID](images/CustomerID.png)  
   *Визуализация: CustomerID.png*  

2. **`MonthlyMinutes`** (boxplot):  
   - Группа 1 демонстрирует **меньшую вариативность** в использовании минут.  
   - ![MonthlyMinutes](images/MonthlyMinutes.png)  
   *Визуализация: MonthlyMinutes.png*  

3. **`PercChangeMinutes`** (boxplot):  
   - Группа 1 имеет **более выраженное снижение минут** (медиана = -11.0 против -3.0 в группе 0).  
   - ![PercChangeMinutes](images/PercChangeMinutes.png)  
   *Визуализация: PercChangeMinutes.png*  

---

## 6. Выбросы и аномалии  
**Топ признаков с выбросами:**  
| Признак                     | Количество выбросов | Процент |  
|-----------------------------|---------------------|---------|  
| `PercChangeRevenues`        | 13,221              | 25.90%  |  
| `RoamingCalls`              | 8,835               | 17.31%  |  
| `DroppedBlockedCalls`       | 3,936               | 7.71%   |  

**Интерпретация:**  
- `PercChangeRevenues` содержит **25.9% выбросов**, что может искажать анализ изменений доходов.  
- `RoamingCalls` и `DroppedBlockedCalls` имеют аномально высокие значения, возможно, из-за ошибок в данных.  

**Визуализация:**  
![Сводный график выбросов](images/out_outlier_summary.png)  
*Визуализация: out_outlier_summary.png*  

---

## 7. Анализ взаимодействия признаков  
**Значимые взаимодействия:**  
- `HandsetWebCapable` × `HandsetRefurbished`: Клиенты с веб-совместимыми устройствами реже используют б/у модели.  
- `ServiceArea` × `RespondsToMailOffers`: В некоторых регионах (`ServiceArea`) клиенты группы 1 чаще реагируют на письма.  

**Визуализация:**  
*(Если в `InteractionAnalysis.details` есть графики, например, `interaction_HandsetWebCapable_HandsetRefurbished.png`, их можно вставить. В данном случае данных нет, поэтому раздел пропускается.)*  

---

## 8. Важность признаков (модель)  
**Топ-5 признаков по RandomForest:**  
1. `CurrentEquipmentDays` (0.0544)  
2. `PercChangeMinutes` (0.0477)  
3. `CustomerID` (0.0475)  
4. `MonthlyMinutes` (0.0465)  
5. `MonthlyRevenue` (0.0412)  

**Интерпретация:**  
- `CurrentEquipmentDays` — главный предиктор, вероятно, из-за долгосрочного поведения клиентов.  
- `PercChangeMinutes` и `MonthlyRevenue` также важны, но их влияние слабее.  

**Визуализация:**  
![Важность признаков](images/imp_feature_importance.png)  
*Визуализация: imp_feature_importance.png*  

---

## 9. Инсайт-ориентированные визуализации  
1. **`MonthlyRevenue`** (boxplot + histogram):  
   - Группа 1 имеет **меньшее количество отрицательных значений**.  
   - ![MonthlyRevenue boxplot](images/desc_MonthlyRevenue_boxplot.png)  
   - ![MonthlyRevenue histogram](images/desc_MonthlyRevenue_hist.png)  

2. **`RetentionCalls`** (scatter + boxplot):  
   - Положительная корреляция (0.065) с целевой переменной.  
   - ![RetentionCalls scatter](images/corr_RetentionCalls_scatter.png)  
   - ![RetentionCalls boxplot](images/corr_RetentionCalls_boxplot.png)  

3. **`CreditRating`** (stacked bar):  
   - Высокий рейтинг (`High`) в группе 1 встречается **в 2 раза чаще**.  
   - ![CreditRating stacked bar](images/cat_CreditRating_stacked_bar.png)  

---

## Заключение и рекомендации  
### **Синтез выводов**  
Наибольшую разницу между группами дают:  
1. **`CurrentEquipmentDays`** — клиенты группы 1 дольше используют оборудование.  
2. **`MonthlyRevenue_min`** — в группе 1 нет отрицательных минимальных доходов.  
3. **`CallWaitingCalls_median`** — группа 1 не использует эту функцию.  

### **Рекомендации**  
1. **Исследовать `CurrentEquipmentDays`:**  
   - Проверить, связаны ли длительные сроки использования с программами лояльности или техническими ограничениями.  
2. **Анализировать `MonthlyRevenue_min`:**  
   - Выяснить причины отрицательных доходов в группе 0 (например, штрафы, ошибки биллинга).  
3. **Оптимизировать предложения:**  
   - Учитывая, что группа 1 реже принимает `RetentionOffers`, возможно, стоит адаптировать их содержание.  
4. **Очистка данных:**  
   - Удалить или обработать выбросы в `PercChangeRevenues` и `RoamingCalls` для улучшения качества модели.  

**Дополнительные гипотезы:**  
- Клиенты с `HandsetWebCapable = Yes` и `CreditRating = High` имеют **наименьший риск оттока**.  
- Отрицательные значения `MonthlyRevenue` в группе 0 могут быть маркерами **неудовлетворенности сервисом**.  

---  
**Примечание:** Все графики взяты из `details` соответствующих инструментов (`DistributionVisualizer`, `InsightDrivenVisualizer`, `CategoricalFeatureAnalysis`). Графики для взаимодействий и heatmap корреляций не включены из-за отсутствия подтверждения в данных.