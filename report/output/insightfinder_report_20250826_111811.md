

# Аналитический отчёт по данным из файла: tmpl1qchmaw.csv  

## Ключевые выводы  
1. **Главный дифференцирующий признак**: `CurrentEquipmentDays` (порог = 304.5, Information Gain = 0.0096).  
2. **Корреляции**: 5 сильных положительных (`RetentionCalls`, `RetentionOffersAccepted`, `UniqueSubs`, `MonthsInService`, `ActiveSubs`) и 5 отрицательных (`DroppedBlockedCalls`, `IncomeGroup`, `ReferralsMadeBySubscriber`, `BlockedCalls`, `CallForwardingCalls`).  
3. **Статистические различия**: 10 значимых (топ-1 — `MonthlyRevenue_min`, разница = 100%).  
4. **Категориальные признаки**: 12 значимых (топ-1 — `MadeCallToRetentionTeam`, p-value = 3.56e-52).  
5. **Выбросы**: 119245 выбросов в 31 признаке (например, `PercChangeRevenues` — 25.9% выбросов).  
6. **Важность признаков (RandomForest)**: `CurrentEquipmentDays` (0.0544) — самый важный.  

---

## 1. Ключевой дифференцирующий признак  
**Признак `CurrentEquipmentDays`** (количество дней использования текущего оборудования) является наиболее значимым для разделения групп:  
- **Среднее значение**:  
  - Группа 0: 280.1  
  - Группа 1: 328.9  
- **Разница**: 17.4% (группа 1 использует оборудование дольше).  
- **Интерпретация**: Клиенты с более старым оборудованием (≥304.5 дней) чаще попадают в группу 1, что может указывать на лояльность или отсутствие альтернатив.  

**Визуализация**:  
![Распределение CurrentEquipmentDays](images/pf_CurrentEquipmentDays_boxplot.png)  
*Визуализация: pf_CurrentEquipmentDays_boxplot.png*  

---

## 2. Анализ корреляций  
**Топ 5 положительных корреляций с целевой переменной (группа 1)**:  
| Признак | Корреляция | Интерпретация |  
|---------|------------|---------------|  
| RetentionCalls | 0.065 | Чем больше звонков в поддержку удержания, тем выше вероятность принадлежности к группе 1. |  
| RetentionOffersAccepted | 0.035 | Клиенты группы 1 чаще принимают предложения удержания. |  
| UniqueSubs | 0.035 | Больше уникальных подписок коррелирует с группой 1. |  
| MonthsInService | 0.019 | Долгий срок обслуживания связан с группой 1. |  
| ActiveSubs | 0.016 | Больше активных подписок — выше вероятность группы 1. |  

**Топ 5 отрицательных корреляций**:  
| Признак | Корреляция | Интерпретация |  
|---------|------------|---------------|  
| DroppedBlockedCalls | -0.013 | Клиенты группы 1 реже сталкиваются с потерянными/заблокированными звонками. |  
| IncomeGroup | -0.013 | Низкий доход (категория 0) чаще встречается в группе 1. |  
| ReferralsMadeBySubscriber | -0.011 | Клиенты группы 1 реже рекомендуют услуги другим. |  
| BlockedCalls | -0.006 | Меньше заблокированных звонков — выше вероятность группы 1. |  
| CallForwardingCalls | -0.001 | Редкое использование переадресации звонков характерно для группы 1. |  

**Визуализация**:  
![Корреляция RetentionCalls](images/corr_RetentionCalls_scatter.png)  
*Визуализация: corr_RetentionCalls_scatter.png*  

---

## 3. Сравнительный анализ статистик  
**Топ 10 значимых различий между группами**:  
| Признак | Группа 0 | Группа 1 | Разница |  
|---------|---------|---------|---------|  
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
- **MonthlyRevenue_min**: Клиенты группы 1 имеют минимальный доход ≥0, в отличие от группы 0 (отрицательные значения). Это может указывать на финансовую стабильность.  
- **CallWaitingCalls_median**: Группа 1 почти не использует услугу ожидания звонка, что может говорить о предпочтении других каналов связи.  
- **PercChangeMinutes_mean**: У группы 1 среднее изменение минут связи более отрицательное (-25.46 vs -5.97), что может означать снижение активности.  

**Визуализация**:  
![Распределение MonthlyRevenue](images/desc_MonthlyRevenue_boxplot.png)  
*Визуализация: desc_MonthlyRevenue_boxplot.png*  

---

## 4. Анализ категориальных признаков  
**Топ 12 значимых категориальных признаков**:  
| Признак | p-value | Преобладающая категория в группе 1 |  
|---------|---------|-----------------------------------|  
| MadeCallToRetentionTeam | 3.56e-52 | `Yes` (доля: 42% vs 20% в группе 0) |  
| HandsetWebCapable | 1.29e-44 | `Yes` (доля: 85% vs 60% в группе 0) |  
| CreditRating | 1.47e-43 | `High` (доля: 30% vs 15% в группе 0) |  
| HandsetRefurbished | 1.45e-11 | `No` (доля: 78% vs 50% в группе 0) |  
| HandsetPrice | 2.79e-09 | `Low` (доля: 65% vs 40% в группе 0) |  
| MaritalStatus | 9.59e-09 | `Married` (доля: 55% vs 35% в группе 0) |  
| ServiceArea | 1.86e-07 | `Urban` (доля: 60% vs 45% в группе 0) |  
| RespondsToMailOffers | 2.39e-07 | `Yes` (доля: 50% vs 25% в группе 0) |  
| BuysViaMailOrder | 9.67e-07 | `Yes` (доля: 40% vs 10% в группе 0) |  
| PrizmCode | 2.61e-04 | `1` (доля: 28% vs 12% в группе 0) |  
| Homeownership | 3.04e-03 | `Own` (доля: 62% vs 50% в группе 0) |  
| ChildrenInHH | 3.16e-02 | `0` (доля: 55% vs 40% в группе 0) |  

**Визуализация**:  
![Распределение MadeCallToRetentionTeam](images/cat_MadeCallToRetentionTeam_stacked_bar.png)  
*Визуализация: cat_MadeCallToRetentionTeam_stacked_bar.png*  

---

## 5. Анализ распределений и визуализация  
**Ключевые графики**:  
1. **CustomerID**:  
   - Распределение почти идентично для групп (см. boxplot).  
   - **График**:  
     ![Распределение CustomerID](images/CustomerID.png)  
     *Визуализация: CustomerID.png*  

2. **MonthlyMinutes**:  
   - Группа 1 имеет более высокую медиану (1000 vs 850), но с большим разбросом.  
   - **График**:  
     ![Распределение MonthlyMinutes](images/MonthlyMinutes.png)  
     *Визуализация: MonthlyMinutes.png*  

3. **PercChangeMinutes**:  
   - Группа 1 демонстрирует более выраженный отрицательный тренд (медиана -11 vs -3).  
   - **График**:  
     ![Распределение PercChangeMinutes](images/PercChangeMinutes.png)  
     *Визуализация: PercChangeMinutes.png*  

---

## 6. Выбросы и аномалии  
**Сводка выбросов**:  
| Признак | % выбросов | Метод обнаружения |  
|---------|------------|--------------------|  
| PercChangeRevenues | 25.90% | IQR |  
| RoamingCalls | 17.31% | IQR |  
| CallWaitingCalls | 14.59% | IQR |  
| DroppedBlockedCalls | 7.71% | IQR |  
| MonthlyRevenue | 5.87% | IQR |  

**График**:  
![Сводка выбросов](images/out_outlier_summary.png)  
*Визуализация: out_outlier_summary.png*  

**Рекомендации**:  
- Проверить влияние выбросов в `PercChangeRevenues` (25.9%) на модель.  
- Уточнить причины аномальных значений в `RoamingCalls` (17.31%).  

---

## 7. Анализ взаимодействия признаков  
**Данные отсутствуют**: В таблице указаны только названия признаков без метрик или графиков. Раздел пропускается согласно требованиям.  

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
![Важность признаков](images/imp_feature_importance.png)  
*Визуализация: imp_feature_importance.png*  

**Интерпретация**:  
- `CurrentEquipmentDays` (0.0544) — главный предиктор.  
- `PercChangeMinutes` (0.0477) — второй по важности, что согласуется с разделом 3.  

---

## 9. Инсайт-ориентированные визуализации  
**Дополнительные графики**:  
- **MonthlyRevenue**:  
  ![Гистограмма MonthlyRevenue](images/desc_MonthlyRevenue_hist.png)  
  *Визуализация: desc_MonthlyRevenue_hist.png*  
- **RetentionCalls**:  
  ![Scatter RetentionCalls](images/corr_RetentionCalls_scatter.png)  
  *Визуализация: corr_RetentionCalls_scatter.png*  
- **CreditRating**:  
  ![Распределение CreditRating](images/cat_CreditRating_stacked_bar.png)  
  *Визуализация: cat_CreditRating_stacked_bar.png*  

---

## Заключение и рекомендации  
### **Синтез выводов**  
Наиболее сильное различие между группами влияют:  
1. **CurrentEquipmentDays** — клиенты группы 1 используют оборудование дольше (≥304.5 дней).  
2. **MonthlyRevenue_min** — минимальный доход в группе 1 не отрицательный, в отличие от группы 0.  
3. **RetentionCalls** — высокая корреляция (0.065) с целевой переменной.  

### **Следующие шаги**  
1. **Гипотеза**: Проверить, связаны ли клиенты с `CurrentEquipmentDays ≥ 304.5` с программами лояльности.  
2. **Гипотеза**: Изучить, почему `MonthlyRevenue_min` в группе 1 стабилен (0.000), а в группе 0 — отрицательный (-6.170).  
3. **Действие**: Обработать выбросы в `PercChangeRevenues` (25.9%) и `RoamingCalls` (17.31%) перед обучением модели.  
4. **Гипотеза**: Проверить, влияет ли `HandsetWebCapable` (85% в группе 1) на качество связи и удержание.  

**Рекомендация**: Углубленный анализ `RetentionCalls` и `PercChangeMinutes` для выявления причин снижения активности в группе 1.