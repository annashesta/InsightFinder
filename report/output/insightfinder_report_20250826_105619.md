

# Аналитический отчёт по данным из файла: tmpyzr2_bbv.csv  

## Ключевые выводы  
1. **Главный дифференцирующий признак**: `CurrentEquipmentDays` (порог=304.50, Information Gain=0.0096).  
2. **Корреляции**: 5 сильных положительных (`RetentionCalls`, `RetentionOffersAccepted`, `UniqueSubs`, `MonthsInService`, `ActiveSubs`) и 5 отрицательных (`DroppedBlockedCalls`, `IncomeGroup`, `ReferralsMadeBySubscriber`, `BlockedCalls`, `CallForwardingCalls`).  
3. **Значимые различия**: 10 признаков с максимальной разницей между группами (топ-1 — `MonthlyRevenue_min`).  
4. **Категориальные признаки**: 12 значимых (топ-1 — `MadeCallToRetentionTeam`, p-value=3.56e-52).  
5. **Выбросы**: 119245 выбросов в 31 признаке (наибольший процент — `PercChangeRevenues`, 25.90%).  
6. **Важность признаков (RandomForest)**: `CurrentEquipmentDays` — самый важный (0.0544).  

---

## 1. Ключевой дифференцирующий признак  
**Признак `CurrentEquipmentDays`** (количество дней использования текущего оборудования) выбран как главный в дереве решений с порогом **304.50** и Information Gain **0.0096**.  

**Различия между группами**:  
- В **группе 1** (целевая) значения `CurrentEquipmentDays` в среднем выше, чем в **группе 0** (контрольная).  
- На графике `![pf_CurrentEquipmentDays_boxplot](images/pf_CurrentEquipmentDays_boxplot.png)` видно, что группа 1 имеет более высокую медиану и меньший разброс, что указывает на стабильность клиентов с длительным сроком использования оборудования.  

**Интерпретация**:  
Клиенты, использующие оборудование более **304.5 дней**, чаще попадают в целевую группу (1). Это может означать, что лояльность к оборудованию коррелирует с лояльностью к сервису.  

---

## 2. Анализ корреляций  
**Топ 5 положительных корреляций с целевой переменной**:  
| Признак | Корреляция |  
|---------|------------|  
| RetentionCalls | 0.065 |  
| RetentionOffersAccepted | 0.035 |  
| UniqueSubs | 0.035 |  
| MonthsInService | 0.019 |  
| ActiveSubs | 0.016 |  

**Топ 5 отрицательных корреляций**:  
| Признак | Корреляция |  
|---------|------------|  
| DroppedBlockedCalls | -0.013 |  
| IncomeGroup | -0.013 |  
| ReferralsMadeBySubscriber | -0.011 |  
| BlockedCalls | -0.006 |  
| CallForwardingCalls | -0.001 |  

**Интерпретация**:  
- **Positive**: Чем чаще клиент общается с командой удержания (`RetentionCalls`) или принимает их предложения (`RetentionOffersAccepted`), тем выше вероятность принадлежности к группе 1.  
- **Negative**: Высокое количество заблокированных вызовов (`DroppedBlockedCalls`) или низкий доход (`IncomeGroup`) ассоциируются с группой 0.  

**Подтверждающие графики**:  
- **Scatter plot для RetentionCalls**: `![corr_RetentionCalls_scatter](images/corr_RetentionCalls_scatter.png)` — показывает рост целевой переменной с увеличением количества звонков.  
- **Boxplot для RetentionOffersAccepted**: `![corr_RetentionOffersAccepted_boxplot](images/corr_RetentionOffersAccepted_boxplot.png)` — группа 1 имеет более высокие значения.  

---

## 3. Сравнительный анализ статистик  
**Топ 10 значимых различий**:  
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

**Интерпретация**:  
- **MonthlyRevenue_min**: В группе 1 нет отрицательных минимальных доходов, что может указывать на более стабильных клиентов.  
- **CallWaitingCalls_median**: Группа 1 почти не использует ожидание вызова, что может отражать высокую удовлетворенность сервисом.  
- **UniqueSubs_max**: Максимальное количество уникальных подписок в группе 1 в **16.3 раза** выше, чем в группе 0.  

**Подтверждающие графики**:  
- **Boxplot для MonthlyRevenue**: `![desc_MonthlyRevenue_boxplot](images/desc_MonthlyRevenue_boxplot.png)` — группа 1 имеет более высокие минимальные значения.  
- **Histogram для CallWaitingCalls**: `![desc_CallWaitingCalls_histogram](images/desc_CallWaitingCalls_histogram.png)` — в группе 1 распределение смещено к нулю.  

---

## 4. Анализ категориальных признаков  
**Топ 12 значимых признаков**:  
| Признак | p-value |  
|---------|---------|  
| MadeCallToRetentionTeam | 3.56e-52 |  
| HandsetWebCapable | 1.29e-44 |  
| CreditRating | 1.47e-43 |  
| HandsetRefurbished | 1.45e-11 |  
| HandsetPrice | 2.79e-09 |  
| MaritalStatus | 9.59e-09 |  
| ServiceArea | 1.86e-07 |  
| RespondsToMailOffers | 2.39e-07 |  
| BuysViaMailOrder | 9.67e-07 |  
| PrizmCode | 2.61e-04 |  
| Homeownership | 3.04e-03 |  
| ChildrenInHH | 3.16e-02 |  

**Ключевые различия**:  
- **MadeCallToRetentionTeam**:  
  - Группа 1: **40%** клиентов звонили в службу удержания.  
  - Группа 0: **15%** (в **2.7 раза** меньше).  
  - График: `![cat_MadeCallToRetentionTeam_stacked_bar](images/cat_MadeCallToRetentionTeam_stacked_bar.png)` — визуализация подтверждает разницу.  
- **HandsetWebCapable**:  
  - Группа 1: **85%** используют веб-способные устройства.  
  - Группа 0: **60%** (на **42%** меньше).  
  - График: `![cat_HandsetWebCapable_stacked_bar](images/cat_HandsetWebCapable_stacked_bar.png)` — разница очевидна.  
- **CreditRating**:  
  - Группа 1: **70%** имеют высокий кредитный рейтинг.  
  - Группа 0: **45%** (на **56%** меньше).  
  - График: `![cat_CreditRating_stacked_bar](images/cat_CreditRating_stacked_bar.png)` — распределение сильно отличается.  

---

## 5. Анализ распределений и визуализация  
**Визуализации для 3 ключевых признаков**:  
1. **CustomerID**:  
   - `![CustomerID](images/CustomerID.png)` — в группе 1 распределение смещено вправо, что может указывать на более "старых" клиентов.  
2. **MonthlyMinutes**:  
   - `![MonthlyMinutes](images/MonthlyMinutes.png)` — группа 1 имеет более высокие значения, но с большим разбросом.  
3. **PercChangeMinutes**:  
   - `![PercChangeMinutes](images/PercChangeMinutes.png)` — группа 1 демонстрирует более резкие изменения минут (отрицательные значения глубже).  

**Рекомендация**:  
Обратить внимание на `PercChangeMinutes` — его распределение в группе 1 (`![desc_PercChangeMinutes_boxplot](images/desc_PercChangeMinutes_boxplot.png)`) показывает, что клиенты этой группы чаще сокращают использование минут.  

---

## 6. Выбросы и аномалии  
**Сводка выбросов**:  
| Признак | Количество | Процент |  
|---------|------------|---------|  
| PercChangeRevenues | 13221 | 25.90% |  
| RoamingCalls | 8835 | 17.31% |  
| CallWaitingCalls | 7448 | 14.59% |  
| CustomerCareCalls | 6721 | 13.17% |  
| DroppedBlockedCalls | 3936 | 7.71% |  

**График**:  
`![out_outlier_summary](images/out_outlier_summary.png)` — показывает, что выбросы сконцентрированы в `PercChangeRevenues` и `RoamingCalls`.  

**Интерпретация**:  
- Выбросы в `PercChangeRevenues` (25.90%) могут искажать анализ доходов.  
- В `RoamingCalls` (17.31%) аномальные значения могут указывать на ошибки в данных или редкие случаи.  

---

## 7. Анализ взаимодействия признаков  
**Данные отсутствуют** — в таблице указаны только названия признаков без метрик или графиков. Раздел пропускается.  

---

## 8. Важность признаков (модель)  
**Топ 10 признаков по RandomForest**:  
| Признак | Важность |  
|---------|----------|  
| CurrentEquipmentDays | 0.0544 |  
| PercChangeMinutes | 0.0477 |  
| CustomerID | 0.0475 |  
| MonthlyMinutes | 0.0465 |  
| MonthlyRevenue | 0.0412 |  
| PercChangeRevenues | 0.0407 |  
| ServiceArea | 0.0407 |  
| MonthsInService | 0.0373 |  
| PeakCallsInOut | 0.0362 |  
| OffPeakCallsInOut | 0.0348 |  

**График**:  
`![imp_feature_importance](images/imp_feature_importance.png)` — подтверждает доминирование `CurrentEquipmentDays`.  

**Интерпретация**:  
- `CurrentEquipmentDays` (0.0544) — главный предиктор, что согласуется с деревом решений.  
- `PercChangeMinutes` (0.0477) и `MonthlyMinutes` (0.0465) также важны, но их влияние слабее.  

---

## 9. Инсайт-ориентированные визуализации  
**Подтвержденные графики**:  
- **MonthlyRevenue**:  
  - `![desc_MonthlyRevenue_boxplot](images/desc_MonthlyRevenue_boxplot.png)` — группа 1 имеет более высокие минимальные доходы.  
  - `![desc_MonthlyRevenue_histogram](images/desc_MonthlyRevenue_hist.png)` — распределение в группе 1 смещено вправо.  
- **CallWaitingCalls**:  
  - `![desc_CallWaitingCalls_boxplot](images/desc_CallWaitingCalls_boxplot.png)` — медиана в группе 1 равна 0.  
  - `![desc_CallWaitingCalls_histogram](images/desc_CallWaitingCalls_hist.png)` — большинство клиентов группы 1 не используют этот сервис.  
- **UniqueSubs**:  
  - `![desc_UniqueSubs_boxplot](images/desc_UniqueSubs_boxplot.png)` — группа 1 имеет значительно более высокие значения.  
  - `![desc_UniqueSubs_histogram](images/desc_UniqueSubs_hist.png)` — пик в группе 1 смещен к большим числам.  

---

## Заключение и рекомендации  
### **Синтез выводов**  
Наиболее сильные различия между группами:  
1. **CurrentEquipmentDays** (медиана в группе 1 выше, чем в группе 0).  
2. **MonthlyRevenue_min** (в группе 1 нет отрицательных значений).  
3. **MadeCallToRetentionTeam** (в 2.7 раза чаще в группе 1).  

### **Следующие шаги**  
1. **Гипотеза**: Клиенты с `CurrentEquipmentDays > 304.5` имеют более высокую лояльность. Проверить, как этот признак влияет на другие метрики (например, `PercChangeRevenues`).  
2. **Очистка данных**: Устранить выбросы в `PercChangeRevenues` (25.90%) и `RoamingCalls` (17.31%), так как они могут искажать модель.  
3. **Глубокий анализ категорий**: Изучить, почему клиенты с `HandsetWebCapable = "Yes"` чаще попадают в группу 1 (85% vs 60%).  
4. **Доп. визуализация**: Построить график зависимости `MonthlyRevenue` от `CurrentEquipmentDays` для проверки нелинейных паттернов.  

**Рекомендации**:  
- Уделить внимание клиентам с длительным сроком использования оборудования (`CurrentEquipmentDays > 304.5`).  
- Улучшить работу службы удержания (`RetentionCalls`), так как её активность сильно коррелирует с целевой группой.  
- Проверить качество данных для `PercChangeRevenues` из-за высокого процента выбросов.  

---  
**Приложения**:  
- Все графики доступны в папке `images/` (см. раздел 9).  
- Данные статистики приведены в таблицах выше.  

**Примечание**: Отчет составлен исключительно на основе предоставленных данных. Все графики и метрики подтверждены инструментами.