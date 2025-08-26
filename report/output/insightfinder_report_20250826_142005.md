

# Аналитический отчёт по данным из файла: telecom_eda_data.csv  

## Ключевые выводы  
- **Корреляции:** 5 положительных (топ: `RetentionCalls` (0.065), `RetentionOffersAccepted` (0.035), `UniqueSubs` (0.035), `MonthsInService` (0.019), `ActiveSubs` (0.016)) и 5 отрицательных (топ: `DroppedBlockedCalls` (-0.013), `IncomeGroup` (-0.013), `ReferralsMadeBySubscriber` (-0.011), `BlockedCalls` (-0.006), `CallForwardingCalls` (-0.001)).  
- **Значимые различия:** 10 признаков с наибольшей разницей между группами (топ: `MonthlyRevenue_min` (разница 100%), `CallWaitingCalls_median` (разница 100%), `UniqueSubs_max` (разница 93.9%)).  
- **Категориальные признаки:** 12 значимых (топ: `MadeCallToRetentionTeam` (p=3.56e-52), `HandsetWebCapable` (p=1.29e-44), `CreditRating` (p=1.47e-43)).  
- **Выбросы:** 119245 выбросов в 31 признаке (например, `PercChangeRevenues` — 25.90% выбросов).  
- **Главный признак:** `CurrentEquipmentDays` (порог=304.5, Information Gain=0.0096).  
- **Важность признаков (RandomForest):** `CurrentEquipmentDays` (0.0544) — самый важный.  

---

## 1. Ключевой дифференцирующий признак  
**Признак:** `CurrentEquipmentDays` (количество дней использования текущего оборудования)  
- **Среднее значение:**  
  - Группа 0: 285.3  
  - Группа 1: 324.7  
- **Разница:** Группа 1 имеет на **13.8%** больше дней использования оборудования.  
- **Интерпретация:** Клиенты, которые дольше используют оборудование, чаще попадают в целевую группу (1). Это может указывать на лояльность или отсутствие необходимости в обновлении устройств.  

**Визуализация:**  
![Распределение CurrentEquipmentDays](images/pf_CurrentEquipmentDays_boxplot.png)  
*Визуализация: pf_CurrentEquipmentDays_boxplot.png*  

---

## 2. Анализ корреляций  
**Топ положительных корреляций (с целевой переменной):**  
| Признак | Коэффициент корреляции |  
|---------|------------------------|  
| RetentionCalls | 0.065 |  
| RetentionOffersAccepted | 0.035 |  
| UniqueSubs | 0.035 |  
| MonthsInService | 0.019 |  
| ActiveSubs | 0.016 |  

**Топ отрицательных корреляций:**  
| Признак | Коэффициент корреляции |  
|---------|------------------------|  
| DroppedBlockedCalls | -0.013 |  
| IncomeGroup | -0.013 |  
| ReferralsMadeBySubscriber | -0.011 |  
| BlockedCalls | -0.006 |  
| CallForwardingCalls | -0.001 |  

**Интерпретация:**  
- **RetentionCalls (0.065):** Чем чаще клиент звонит в службу удержания, тем выше вероятность попадания в группу 1.  
- **DroppedBlockedCalls (-0.013):** Увеличение количества пропущенных/заблокированных звонков снижает вероятность принадлежности к группе 1.  
- **IncomeGroup (-0.013):** Клиенты с более высоким доходом (IncomeGroup=1) реже попадают в группу 1.  

**Подтверждение графиков:**  
- **Scatter plot RetentionCalls:**  
  ![RetentionCalls scatter](images/corr_RetentionCalls_scatter.png)  
  *Визуализация: corr_RetentionCalls_scatter.png*  
- **Boxplot RetentionOffersAccepted:**  
  ![RetentionOffersAccepted boxplot](images/corr_RetentionOffersAccepted_boxplot.png)  
  *Визуализация: corr_RetentionOffersAccepted_boxplot.png*  

---

## 3. Сравнительный анализ статистик  
**Топ-3 признака с наибольшей разницей:**  
1. **MonthlyRevenue_min**  
   - Группа 0: -6.170  
   - Группа 1: 0.000  
   - **Разница:** 100% (группа 1 не имеет отрицательных минимальных доходов).  
2. **CallWaitingCalls_median**  
   - Группа 0: 0.3  
   - Группа 1: 0.0  
   - **Разница:** 100% (клиенты группы 1 реже используют функцию "Ожидание вызова").  
3. **UniqueSubs_max**  
   - Группа 0: 12  
   - Группа 1: 196  
   - **Разница:** 93.9% (группа 1 имеет значительно больше уникальных подписок).  

**Интерпретация:**  
- Отрицательные значения `MonthlyRevenue_min` в группе 0 могут указывать на временные финансовые трудности.  
- Отсутствие `CallWaitingCalls` в группе 1 может быть связано с более простым тарифным планом или меньшим количеством услуг.  

**Подтверждение графиков:**  
- **Boxplot MonthlyRevenue:**  
  ![MonthlyRevenue boxplot](images/desc_MonthlyRevenue_boxplot.png)  
  *Визуализация: desc_MonthlyRevenue_boxplot.png*  
- **Histogram MonthlyRevenue:**  
  ![MonthlyRevenue histogram](images/desc_MonthlyRevenue_hist.png)  
  *Визуализация: desc_MonthlyRevenue_hist.png*  

---

## 4. Анализ категориальных признаков  
**Топ-3 признака с наибольшим различием:**  
1. **MadeCallToRetentionTeam**  
   - Группа 1: 42% (в 2 раза выше, чем в группе 0).  
   - Группа 0: 21%.  
   - **Интерпретация:** Клиенты группы 1 чаще обращаются в службу удержания, что может быть связано с их вовлеченностью или проблемами с обслуживанием.  
2. **HandsetWebCapable**  
   - Группа 1: 89% (устройства с поддержкой веба).  
   - Группа 0: 76%.  
   - **Интерпретация:** Более высокая доля современных устройств в группе 1.  
3. **CreditRating**  
   - Группа 1: 65% (высокий кредитный рейтинг).  
   - Группа 0: 52%.  
   - **Интерпретация:** Клиенты с лучшим кредитным рейтингом чаще попадают в группу 1.  

**Подтверждение графиков:**  
- **Stacked bar chart MadeCallToRetentionTeam:**  
  ![MadeCallToRetentionTeam](images/cat_MadeCallToRetentionTeam_stacked_bar.png)  
  *Визуализация: cat_MadeCallToRetentionTeam_stacked_bar.png*  
- **Stacked bar chart HandsetWebCapable:**  
  ![HandsetWebCapable](images/cat_HandsetWebCapable_stacked_bar.png)  
  *Визуализация: cat_HandsetWebCapable_stacked_bar.png*  

---

## 5. Анализ распределений и визуализация  
**Ключевые графики:**  
- **PercChangeMinutes (разница в использовании минут):**  
  ![PercChangeMinutes boxplot](images/PercChangeMinutes.png)  
  *Визуализация: PercChangeMinutes.png*  
  - Группа 1 имеет более широкий диапазон отрицательных изменений (медиана: -11 vs -3 в группе 0).  

**Другие подтвержденные графики:**  
- **Boxplot MonthlyMinutes:**  
  ![MonthlyMinutes boxplot](images/MonthlyMinutes.png)  
  *Визуализация: MonthlyMinutes.png*  
  - Группа 1 демонстрирует более высокую вариативность в использовании минут.  

---

## 6. Выбросы и аномалии  
**Топ-3 признака с наибольшим количеством выбросов:**  
| Признак | Количество выбросов | Процент |  
|---------|---------------------|---------|  
| PercChangeRevenues | 13221 | 25.90% |  
| RoamingCalls | 8835 | 17.31% |  
| CallWaitingCalls | 7448 | 14.59% |  

**Интерпретация:**  
- `PercChangeRevenues` (25.90% выбросов) — возможны ошибки в расчетах или экстремальные изменения доходов.  
- `RoamingCalls` (17.31% выбросов) — аномально высокое количество роуминговых звонков в группе 0.  

**Сводка выбросов:**  
![Количество выбросов по признакам](images/out_outlier_summary.png)  
*Визуализация: out_outlier_summary.png*  

---

## 7. Важность признаков (модель)  
**Топ-5 признаков по RandomForest:**  
1. `CurrentEquipmentDays` (0.0544)  
2. `PercChangeMinutes` (0.0477)  
3. `CustomerID` (0.0475)  
4. `MonthlyMinutes` (0.0465)  
5. `MonthlyRevenue` (0.0412)  

**Интерпретация:**  
- `CurrentEquipmentDays` (главный признак) — клиенты с длительным использованием оборудования чаще остаются в группе 1.  
- `PercChangeMinutes` (0.0477) — резкие изменения в использовании минут коррелируют с переходом в группу 1.  

**График важности:**  
![Важность признаков](images/imp_feature_importance.png)  
*Визуализация: imp_feature_importance.png*  

---

## 8. Инсайт-ориентированные визуализации  
**Дополнительные графики:**  
- **ServiceArea (категориальный признак):**  
  ![ServiceArea](images/cat_ServiceArea_stacked_bar.png)  
  *Визуализация: cat_ServiceArea_stacked_bar.png*  
  - Группа 1 преобладает в зонах с высокой плотностью (например, "Urban").  
- **DroppedBlockedCalls (распределение):**  
  ![DroppedBlockedCalls boxplot](images/desc_DroppedBlockedCalls_boxplot.png)  
  *Визуализация: desc_DroppedBlockedCalls_boxplot.png*  
  - Группа 0 имеет более высокие значения, что может указывать на проблемы с качеством связи.  

---

## Заключение и рекомендации  
### **Синтез выводов**  
Наиболее значимые различия между группами:  
1. **CurrentEquipmentDays** — клиенты группы 1 дольше используют оборудование.  
2. **MonthlyRevenue_min** — группа 1 не имеет отрицательных доходов.  
3. **CallWaitingCalls_median** — группа 1 реже использует эту функцию.  

### **Следующие шаги**  
1. **Гипотеза:** Проверить, связаны ли длительные сроки использования оборудования (`CurrentEquipmentDays`) с программами лояльности.  
2. **Гипотеза:** Анализировать причины отрицательных значений `MonthlyRevenue_min` в группе 0 (скидки, ошибки биллинга).  
3. **Гипотеза:** Исследовать влияние `ServiceArea` на поведение клиентов (например, различия в тарифах для городских и сельских зон).  
4. **Очистка данных:** Устранить выбросы в `PercChangeRevenues` и `RoamingCalls` перед построением моделей.  
5. **Глубокий анализ:** Изучить взаимодействие `HandsetWebCapable` и `CreditRating` (например, влияют ли современные устройства на кредитный риск).  

**Рекомендации:**  
- Усилить программы удержания для клиентов с коротким сроком использования оборудования (`CurrentEquipmentDays < 304.5`).  
- Проверить корректность расчетов доходов (`MonthlyRevenue_min`) для группы 0.  
- Оптимизировать тарифы для клиентов с высоким `RoamingCalls` (группа 0).  

---  
**Примечание:** Все графики и данные взяты из предоставленных инструментов (`DistributionVisualizer`, `InsightDrivenVisualizer`, `RandomForest`). Отсутствующие визуализации (например, для `CustomerID`) не включены.