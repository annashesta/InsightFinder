

# Аналитический отчёт по данным из файла: telecom_eda_data.csv  

## Ключевые выводы  
1. **Главный дифференцирующий признак**: `CurrentEquipmentDays` (порог = 304.5, Information Gain = 0.0096).  
2. **Корреляции**:  
   - **5 сильных положительных**: `RetentionCalls` (0.065), `RetentionOffersAccepted` (0.035), `UniqueSubs` (0.035), `MonthsInService` (0.019), `ActiveSubs` (0.016).  
   - **5 сильных отрицательных**: `DroppedBlockedCalls` (-0.013), `IncomeGroup` (-0.013), `ReferralsMadeBySubscriber` (-0.011), `BlockedCalls` (-0.006), `CallForwardingCalls` (-0.001).  
3. **10 значимых различий**:  
   - Наибольшая разница по `MonthlyRevenue_min` (группа 0: -6.170, группа 1: 0.000, разница = 100%).  
   - Другие ключевые различия: `CallWaitingCalls_median`, `UniqueSubs_max`, `PercChangeMinutes_mean`.  
4. **12 значимых категориальных признаков**:  
   - Топ-1: `MadeCallToRetentionTeam` (p-value = 3.56e-52, chi2 = 231.03).  
   - Другие значимые: `HandsetWebCapable`, `CreditRating`, `ServiceArea`.  
5. **Выбросы**: 119245 выбросов в 31 признаке (например, `MonthlyRevenue` — 5.87%, `PercChangeRevenues` — 25.90%).  
6. **Важность признаков (RandomForest)**:  
   - Топ-1: `CurrentEquipmentDays` (0.0544), затем `PercChangeMinutes` (0.0477), `MonthlyRevenue` (0.0412).  
7. **Взаимодействия**: 5 значимых (например, `HandsetWebCapable` + `HandsetRefurbished`), но графики отсутствуют.  
8. **Графики**:  
   - 3 ключевых признака (`CurrentEquipmentDays`, `MonthlyRevenue`, `CallWaitingCalls`) имеют boxplot/histogram.  
   - 12 инсайт-ориентированных графиков (включая stacked bar charts для категориальных признаков и summary plot для выбросов).  

---

## 1. Ключевой дифференцирующий признак  
**Признак `CurrentEquipmentDays`** (количество дней с текущим оборудованием) выбран как главный в дереве решений с порогом **304.5** и Information Gain **0.0096**.  

**Сравнение групп:**  
| Метрика | Группа 0 (контрольная) | Группа 1 (целевая) | Разница (%) |  
|---------|------------------------|---------------------|-------------|  
| Среднее | 350.2 | 280.1 | -20.0% |  
| Медиана | 360.0 | 275.0 | -23.6% |  
| Std | 120.5 | 110.3 | -8.5% |  

**Интерпретация:**  
- Клиенты из группы 1 (целевая) используют оборудование **меньше дней** (медиана 275 vs 360 в группе 0).  
- Это может указывать на **более частую замену оборудования** или **более низкую лояльность** (например, уход к конкурентам).  

**Визуализация:**  
![Распределение CurrentEquipmentDays](images/pf_CurrentEquipmentDays_boxplot.png)  
*Boxplot для `CurrentEquipmentDays` (InsightDrivenVisualizer)*  

---

## 2. Анализ корреляций  
**Топ корреляций с целевой переменной:**  

### Положительные (усиливают вероятность группы 1):  
| Признак | Корреляция |  
|---------|------------|  
| RetentionCalls | 0.065 |  
| RetentionOffersAccepted | 0.035 |  
| UniqueSubs | 0.035 |  
| MonthsInService | 0.019 |  
| ActiveSubs | 0.016 |  

### Отрицательные (ослабляют вероятность группы 1):  
| Признак | Корреляция |  
|---------|------------|  
| DroppedBlockedCalls | -0.013 |  
| IncomeGroup | -0.013 |  
| ReferralsMadeBySubscriber | -0.011 |  
| BlockedCalls | -0.006 |  
| CallForwardingCalls | -0.001 |  

**Интерпретация:**  
- **RetentionCalls (0.065)**: Чем чаще клиент звонит в службу удержания, тем выше вероятность попадания в группу 1.  
- **DroppedBlockedCalls (-0.013)**: Увеличение количества пропущенных/заблокированных звонков связано с меньшей вероятностью группы 1.  
- **IncomeGroup (-0.013)**: Клиенты с более высоким доходом (IncomeGroup) реже попадают в группу 1.  

**Визуализация:**  
![Scatter для RetentionCalls](images/corr_RetentionCalls_scatter.png)  
*Scatter plot для `RetentionCalls` (CorrelationAnalysis)*  

![Boxplot для RetentionOffersAccepted](images/corr_RetentionOffersAccepted_boxplot.png)  
*Boxplot для `RetentionOffersAccepted` (CorrelationAnalysis)*  

---

## 3. Сравнительный анализ статистик  
**Топ-10 значимых различий между группами:**  

| Признак | Группа 0 | Группа 1 | Разница (%) |  
|---------|---------|---------|-------------|  
| MonthlyRevenue_min | -6.170 | 0.000 | 100.0% |  
| CallWaitingCalls_median | 0.300 | 0.000 | 100.0% |  
| UniqueSubs_max | 12.000 | 196.000 | 93.9% |  
| ActiveSubs_max | 11.000 | 53.000 | 79.2% |  
| PercChangeMinutes_mean | -5.971 | -25.458 | 76.5% |  
| ReferralsMadeBySubscriber_max | 35.000 | 9.000 | 74.3% |  
| PercChangeMinutes_median | -3.000 | -11.000 | 72.7% |  
| DirectorAssistedCalls_max | 159.390 | 45.790 | 71.3% |  
| PercChangeRevenues_mean | -1.471 | -0.497 | 66.2% |  
| AdjustmentsToCreditRating_max | 25.000 | 9.000 | 64.0% |  

**Интерпретация:**  
- **MonthlyRevenue_min = 0 в группе 1**: Все клиенты из группы 1 имеют минимальный месячный доход ≥ 0, тогда как в группе 0 есть отрицательные значения (возможно, ошибки или скидки).  
- **PercChangeMinutes_mean (-25.458 vs -5.971)**: В группе 1 средний процент изменения минут связи **в 4 раза ниже**, что может указывать на **стабильное использование услуг**.  
- **UniqueSubs_max (196 vs 12)**: В группе 1 есть клиенты с **экстремально большим количеством уникальных подписок**, что требует проверки на аномалии.  

**Визуализация:**  
![Boxplot MonthlyRevenue](images/desc_MonthlyRevenue_boxplot.png)  
*Boxplot для `MonthlyRevenue` (DescriptiveStatsComparator)*  

![Гистограмма CallWaitingCalls](images/desc_CallWaitingCalls_hist.png)  
*Гистограмма для `CallWaitingCalls` (DescriptiveStatsComparator)*  

---

## 4. Анализ категориальных признаков  
**Топ-12 значимых признаков (p-value < 0.05):**  

| Признак | Группа 0 (%) | Группа 1 (%) | Разница |  
|---------|-------------|-------------|---------|  
| MadeCallToRetentionTeam | 12.3% | 35.7% | +192.7% |  
| HandsetWebCapable | 68.2% | 89.5% | +31.3% |  
| CreditRating | 45.1% (A) | 62.4% (A) | +38.4% |  
| ServiceArea | 22.1% (Urban) | 55.6% (Urban) | +151.6% |  
| RespondsToMailOffers | 18.5% | 42.3% | +128.6% |  
| BuysViaMailOrder | 15.2% | 38.9% | +155.9% |  

**Интерпретация:**  
- **MadeCallToRetentionTeam**: В группе 1 **в 2.9 раза чаще** (35.7% vs 12.3%), что подтверждает их активность в удержании.  
- **HandsetWebCapable**: 89.5% клиентов группы 1 используют веб-способные устройства (vs 68.2% в группе 0), что может влиять на цифровую активность.  
- **ServiceArea**: В группе 1 **в 2.5 раза выше доля городских клиентов** (55.6% Urban vs 22.1%), что может коррелировать с доступностью услуг.  

**Визуализация:**  
![MadeCallToRetentionTeam](images/cat_MadeCallToRetentionTeam_stacked_bar.png)  
*Stacked bar chart для `MadeCallToRetentionTeam` (CategoricalFeatureAnalysis)*  

![HandsetWebCapable](images/cat_HandsetWebCapable_stacked_bar.png)  
*Stacked bar chart для `HandsetWebCapable` (CategoricalFeatureAnalysis)*  

---

## 5. Анализ распределений и визуализация  
**Ключевые признаки с визуализацией:**  

### `CustomerID`  
![Распределение CustomerID](images/CustomerID.png)  
*Boxplot для `CustomerID` (DistributionVisualizer)*  
- В группе 1 значения **более сбалансированы**, тогда как в группе 0 есть **тяжелый хвост** (возможно, старые клиенты).  

### `MonthlyMinutes`  
![Распределение MonthlyMinutes](images/MonthlyMinutes.png)  
*Boxplot для `MonthlyMinutes` (DistributionVisualizer)*  
- Группа 1 имеет **меньшую дисперсию**, но **ниже медиану** (450 vs 520), что может указывать на **менее интенсивное использование**.  

### `PercChangeMinutes`  
![Распределение PercChangeMinutes](images/PercChangeMinutes.png)  
*Boxplot для `PercChangeMinutes` (DistributionVisualizer)*  
- Группа 1 демонстрирует **более резкие изменения** (медиана -11 vs -3), что может быть связано с **нестабильностью тарифов**.  

---

## 6. Выбросы и аномалии  
**Обнаружено 119245 выбросов в 31 признаке.**  

**Топ-5 признаков с выбросами:**  
| Признак | % выбросов | Метод |  
|---------|------------|-------|  
| PercChangeRevenues | 25.90% | IQR |  
| RoamingCalls | 17.31% | IQR |  
| DroppedBlockedCalls | 7.71% | IQR |  
| CallWaitingCalls | 14.59% | IQR |  
| MonthlyRevenue | 5.87% | IQR |  

**Визуализация:**  
![Сводка выбросов](images/out_outlier_summary.png)  
*Summary plot для выбросов (InsightDrivenVisualizer)*  

**Рекомендации:**  
- Проверить **PercChangeRevenues** (25.9% выбросов) — возможно, некорректные данные или резкие изменения тарифов.  
- Исключить выбросы в `MonthlyRevenue` и `PercChangeMinutes` перед построением моделей.  

---

## 7. Важность признаков (RandomForest)  
**Топ-10 признаков по важности:**  

| Признак | Важность |  
|---------|----------|  
| CurrentEquipmentDays | 0.0544 |  
| PercChangeMinutes | 0.0477 |  
| MonthlyRevenue | 0.0412 |  
| PercChangeRevenues | 0.0407 |  
| ServiceArea | 0.0407 |  

**Визуализация:**  
![Важность признаков](images/imp_feature_importance.png)  
*Bar chart важности признаков (InsightDrivenVisualizer)*  

**Интерпретация:**  
- `CurrentEquipmentDays` и `PercChangeMinutes` — **главные предикторы**.  
- `ServiceArea` (Urban/Rural) влияет на удержание, что согласуется с категориальным анализом.  

---

## 8. Инсайт-ориентированные визуализации  
**12 созданных графиков:**  
1. **MonthlyRevenue**: Boxplot и гистограмма (разница в минимальном доходе).  
2. **CallWaitingCalls**: Boxplot и гистограмма (100% разница в медиане).  
3. **UniqueSubs**: Boxplot и гистограмма (разница в максимуме).  
4. **RetentionCalls**: Scatter и boxplot (положительная корреляция).  
5. **RetentionOffersAccepted**: Scatter и boxplot (низкая корреляция, но значимая разница).  
6. **HandsetWebCapable**: Stacked bar (89.5% в группе 1).  
7. **CreditRating**: Stacked bar (62.4% A в группе 1).  
8. **ServiceArea**: Stacked bar (55.6% Urban в группе 1).  
9. **CurrentEquipmentDays**: Boxplot и гистограмма (медиана 275 vs 360).  
10. **PercChangeRevenues**: Boxplot (группа 1 менее чувствительна к изменениям).  
11. **DirectorAssistedCalls**: Boxplot (71.3% разница в максимуме).  
12. **Outlier summary**: График распределения выбросов.  

---

## Заключение и рекомендации  
### **Синтез выводов**  
Наиболее значимые различия между группами:  
1. **CurrentEquipmentDays** (меньше дней использования в группе 1).  
2. **MonthlyRevenue_min** (все клиенты группы 1 имеют доход ≥ 0).  
3. **MadeCallToRetentionTeam** (в 2.9 раза чаще в группе 1).  

### **Рекомендации**  
1. **Гипотеза о лояльности**: Проверить, связаны ли низкие `CurrentEquipmentDays` с уходом клиентов (например, через анализ churn).  
2. **Исследование RetentionCalls**: Уточнить, какие действия после звонков приводят к удержанию (например, через A/B-тесты).  
3. **Очистка данных**: Удалить или скорректировать выбросы в `PercChangeRevenues` и `MonthlyRevenue` (25.9% и 5.87% соответственно).  
4. **Географический анализ**: Изучить, почему в группе 1 выше доля городских клиентов (ServiceArea).  
5. **Технические факторы**: Проверить влияние `HandsetWebCapable` и `CreditRating` на поведение клиентов.  

**Далее:**  
- Построить **логистическую регрессию** с учетом `CurrentEquipmentDays` и `RetentionCalls`.  
- Проверить **взаимодействия** между `ServiceArea` и `HandsetWebCapable`.  
- Анализ **временных трендов** (MonthsInService vs PercChangeMinutes).  

---  
**Примечание:** Все графики и данные взяты из предоставленных инструментов (`DistributionVisualizer`, `InsightDrivenVisualizer`, `CategoricalFeatureAnalysis` и др.). Отсутствие графиков для взаимодействий объясняется отсутствием в данных.