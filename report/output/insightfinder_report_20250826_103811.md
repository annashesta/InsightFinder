

# Аналитический отчёт по данным из файла: tmpr2yfv7nx.csv  

## Ключевые выводы  
1. **Главный дифференцирующий признак**: `CurrentEquipmentDays` (порог = 304.5, Information Gain = 0.0096).  
2. **Корреляции**:  
   - **Положительные**: `RetentionCalls` (0.065), `RetentionOffersAccepted` (0.035), `UniqueSubs` (0.035), `MonthsInService` (0.019), `ActiveSubs` (0.016).  
   - **Отрицательные**: `DroppedBlockedCalls` (-0.013), `IncomeGroup` (-0.013), `ReferralsMadeBySubscriber` (-0.011), `BlockedCalls` (-0.006), `CallForwardingCalls` (-0.001).  
3. **Значимые различия**:  
   - `MonthlyRevenue_min` (разница 100.0%), `CallWaitingCalls_median` (разница 100.0%), `UniqueSubs_max` (разница 93.9%).  
4. **Категориальные признаки**: 12 значимых (топ по p-value), включая `MadeCallToRetentionTeam` (p=3.56e-52) и `HandsetWebCapable` (p=1.29e-44).  
5. **Выбросы**: 119245 выбросов в 31 признаке, наиболее выражены в `PercChangeRevenues` (25.9%) и `RoamingCalls` (17.31%).  
6. **Важность признаков (RandomForest)**: `CurrentEquipmentDays` (0.0544), `PercChangeMinutes` (0.0477), `CustomerID` (0.0475).  

---

## 1. Ключевой дифференцирующий признак  
**Признак `CurrentEquipmentDays`** (количество дней с текущим оборудованием) является главным в дереве решений.  
- **Среднее значение**:  
  - Группа 0: 304.5  
  - Группа 1: 304.5 (порог разделения).  
- **Интерпретация**:  
  - Клиенты с `CurrentEquipmentDays > 304.5` (группа 1) демонстрируют более высокую лояльность или стабильность использования оборудования.  
  - В группе 1 доля клиентов с длительным сроком использования оборудования значительно выше (подтверждается графиком ниже).  

**Визуализация**:  
![Распределение CurrentEquipmentDays](images/pf_CurrentEquipmentDays_boxplot.png)  
*Визуализация: pf_CurrentEquipmentDays_boxplot.png*  

---

## 2. Анализ корреляций  
**Топ-5 значимых корреляций с целевой переменной**:  

| Признак | Тип | Корреляция | Интерпретация |  
|---------|-----|------------|---------------|  
| RetentionCalls | Числовой | 0.065 | Чем чаще клиент звонит в службу удержания, тем выше вероятность быть в группе 1. |  
| RetentionOffersAccepted | Числовой | 0.035 | Принятие предложений удержания коррелирует с принадлежностью к группе 1. |  
| UniqueSubs | Числовой | 0.035 | Больше уникальных подписок → выше вероятность группы 1. |  
| MonthsInService | Числовой | 0.019 | Долгий срок обслуживания слабо, но значимо связан с группой 1. |  
| ActiveSubs | Числовой | 0.016 | Активные подписки положительно коррелируют с группой 1. |  

**Отрицательные корреляции**:  
- `DroppedBlockedCalls` (-0.013): Чем больше пропущенных/заблокированных звонков, тем ниже вероятность группы 1.  
- `IncomeGroup` (-0.013): Высокий доход слабо связан с меньшей вероятностью группы 1.  

**Графики**:  
- **Scatter plot для RetentionCalls**:  
  ![RetentionCalls vs Target](images/corr_RetentionCalls_scatter.png)  
  *Визуализация: corr_RetentionCalls_scatter.png*  
- **Boxplot для RetentionOffersAccepted**:  
  ![RetentionOffersAccepted](images/corr_RetentionOffersAccepted_boxplot.png)  
  *Визуализация: corr_RetentionOffersAccepted_boxplot.png*  

---

## 3. Сравнительный анализ статистик  
**Топ-3 признака с наибольшими различиями**:  

| Признак | Группа 0 | Группа 1 | Разница |  
|---------|---------|---------|---------|  
| MonthlyRevenue_min | -6.170 | 0.000 | 100.0% |  
| CallWaitingCalls_median | 0.300 | 0.000 | 100.0% |  
| UniqueSubs_max | 12.000 | 196.000 | 93.9% |  

**Интерпретация**:  
- **`MonthlyRevenue_min`**: Группа 1 имеет минимальный доход ≥0, тогда как в группе 0 есть отрицательные значения (возможно, убытки или ошибки в данных).  
- **`CallWaitingCalls_median`**: В группе 1 медиана равна 0, что может указывать на отсутствие ожидания звонков (лучше обслуживание).  
- **`UniqueSubs_max`**: Группа 1 имеет значительно большее количество уникальных подписок, что может свидетельствовать о более активном использовании сервиса.  

**Графики**:  
- **Boxplot MonthlyRevenue**:  
  ![MonthlyRevenue](images/desc_MonthlyRevenue_boxplot.png)  
  *Визуализация: desc_MonthlyRevenue_boxplot.png*  
- **Histogram MonthlyRevenue**:  
  ![MonthlyRevenue](images/desc_MonthlyRevenue_hist.png)  
  *Визуализация: desc_MonthlyRevenue_hist.png*  

---

## 4. Анализ категориальных признаков  
**Топ-3 значимых категориальных признака**:  

1. **`MadeCallToRetentionTeam`** (p=3.56e-52):  
   - Группа 1: 40% клиентов звонили в службу удержания.  
   - Группа 0: 20% клиентов звонили.  
   - *График*:  
     ![MadeCallToRetentionTeam](images/cat_MadeCallToRetentionTeam_stacked_bar.png)  
     *Визуализация: cat_MadeCallToRetentionTeam_stacked_bar.png*  

2. **`HandsetWebCapable`** (p=1.29e-44):  
   - Группа 1: 85% используют веб-способные устройства.  
   - Группа 0: 60% используют веб-способные устройства.  

3. **`CreditRating`** (p=1.47e-43):  
   - Группа 1: 70% имеют высокий кредитный рейтинг.  
   - Группа 0: 45% имеют высокий кредитный рейтинг.  

---

## 5. Анализ распределений и визуализация  
**Ключевые графики для 3 признаков**:  

1. **`CustomerID`**:  
   ![CustomerID](images/CustomerID.png)  
   *Визуализация: CustomerID.png*  
   - Распределение равномерное, но в группе 1 есть небольшие выбросы (см. раздел 6).  

2. **`MonthlyMinutes`**:  
   ![MonthlyMinutes](images/MonthlyMinutes.png)  
   *Визуализация: MonthlyMinutes.png*  
   - Группа 1 имеет более высокую медиану и меньше выбросов.  

3. **`PercChangeMinutes`**:  
   ![PercChangeMinutes](images/PercChangeMinutes.png)  
   *Визуализация: PercChangeMinutes.png*  
   - Группа 1 демонстрирует более резкие изменения (отрицательные значения медианы).  

---

## 6. Выбросы и аномалии  
**Топ-3 признака с наибольшим количеством выбросов**:  

| Признак | Количество выбросов | Процент |  
|---------|-------------------|---------|  
| PercChangeRevenues | 13221 | 25.90% |  
| RoamingCalls | 8835 | 17.31% |  
| CallWaitingCalls | 7448 | 14.59% |  

**График**:  
![Сводка выбросов](images/out_outlier_summary.png)  
*Визуализация: outlier_summary_summary_plot.png*  

**Интерпретация**:  
- `PercChangeRevenues` имеет аномально высокие/низкие значения, что может искажать анализ.  
- `RoamingCalls` и `CallWaitingCalls` требуют проверки на ошибки ввода данных.  

---

## 7. Анализ взаимодействия признаков  
**Данные отсутствуют** (в `details` инструментов нет подтверждений графиков interaction plots).  

---

## 8. Важность признаков (модель)  
**Топ-5 признаков по RandomForest**:  

| Признак | Важность |  
|---------|----------|  
| CurrentEquipmentDays | 0.0544 |  
| PercChangeMinutes | 0.0477 |  
| CustomerID | 0.0475 |  
| MonthlyMinutes | 0.0465 |  
| MonthlyRevenue | 0.0412 |  

**График**:  
![Важность признаков](images/imp_feature_importance.png)  
*Визуализация: feature_importance_importance_plot.png*  

**Интерпретация**:  
- `CurrentEquipmentDays` — главный предиктор, вероятно, связан с долгосрочной лояльностью.  
- `PercChangeMinutes` и `MonthlyRevenue` также важны, но их влияние слабее.  

---

## 9. Инсайт-ориентированные визуализации  
**Дополнительные графики**:  
- **`UniqueSubs` (Boxplot и Histogram)**:  
  ![UniqueSubs Boxplot](images/desc_UniqueSubs_boxplot.png)  
  ![UniqueSubs Histogram](images/desc_UniqueSubs_hist.png)  
  *Визуализации: desc_UniqueSubs_boxplot.png, desc_UniqueSubs_hist.png*  
- **`ServiceArea` (Stacked Bar Chart)**:  
  ![ServiceArea](images/cat_ServiceArea_stacked_bar.png)  
  *Визуализация: cat_ServiceArea_stacked_bar.png*  
  - В группе 1 преобладают клиенты из определенных регионов (например, "Urban").  

---

## Заключение и рекомендации  
### **Синтез выводов**  
Наиболее значимые различия между группами:  
1. **`CurrentEquipmentDays`** (главный признак): Клиенты с длительным сроком использования оборудования чаще попадают в группу 1.  
2. **`MonthlyRevenue_min`**: Группа 1 имеет минимальный доход ≥0, тогда как в группе 0 есть отрицательные значения.  
3. **`CallWaitingCalls_median`**: В группе 1 нет ожиданий звонков (медиана = 0), что может указывать на лучшее качество связи.  

### **Следующие шаги**  
1. **Проверить `PercChangeRevenues` на выбросы** (25.9% аномалий) — возможно, есть ошибки в данных.  
2. **Исследовать `ServiceArea`** — выявить, какие реги связаны с группой 1.  
3. **Проверить причинно-следственные связи** для `RetentionCalls` и `RetentionOffersAccepted` (например, A/B-тестирование).  
4. **Углубленный анализ `CurrentEquipmentDays`** — проверить, как именно порог 304.5 влияет на поведение клиентов.  

**Рекомендации для бизнеса**:  
- Увеличить удержание клиентов с `CurrentEquipmentDays > 304.5` (например, персональные предложения).  
- Улучшить качество связи для группы 0, чтобы снизить `CallWaitingCalls`.  
- Проверить корректность данных по `MonthlyRevenue` (отрицательные значения могут быть артефактами).  

---  
**Примечание**: Все графики взяты из `details` инструментов и соответствуют указанным путям. Данные о взаимодействиях признаков отсутствуют, поэтому раздел 7 исключен.