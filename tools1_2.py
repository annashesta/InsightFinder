import numpy as np
import pandas as pd
from typing import Any, Dict
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
from scipy.stats import pointbiserialr

# =========================
#  Tool 1: Primary Feature Finder
# =========================

def primary_feature_finder(df: pd.DataFrame, target_column: str) -> Dict[str, Any]:
    """
    Decision stump (DecisionTreeClassifier max_depth=1).
    Возвращает: best feature, split threshold, уменьшение gini impurity,
    средние значения признака в двух группах, количество дочерних элементов по сторонам.
    """
    tool_name = "PrimaryFeatureFinder" # Или PrimaryFeatureFinder)
    try:
        # Если не найдена целевая перменная
        if target_column not in df.columns:
            return {
                "tool_name": tool_name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": f"target_column '{target_column}' not found in dataframe"
            }

        data = df.copy()

        X = data.drop(columns=[target_column])
        y = data[target_column]

        # Если нет фичей
        if X.shape[1] == 0:
            return {
                "tool_name": tool_name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": "No features found (df has only target column)."
            }

        # Кодируем целевую
        if y.dtype.kind not in "biufc":  # Если категориальная - кодируем
            le = LabelEncoder()
            y_enc = le.fit_transform(y.astype(str))
        else: # если числовой тип данных
            y_enc = y.astype(int).values

        # Label-encoding всех категориальных признаков
        X_proc = X.copy()
        for col in X_proc.columns:
            if X_proc[col].dtype.kind not in "biufc":
                le = LabelEncoder()
                X_proc[col] = le.fit_transform(X_proc[col].astype(str))

        # Проверка на пустоту
        if X_proc.shape[1] == 0:
            return {
                "tool_name": tool_name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": "No usable features after preprocessing."
            }

        # Обучаем дерево глубины 1
        clf = DecisionTreeClassifier(max_depth=1, random_state=42)
        clf.fit(X_proc.values, y_enc)

        root_feature_index = int(clf.tree_.feature[0])
        # Если не было сплита возвращаем ошибку
        if root_feature_index == -2:
            return {
                "tool_name": tool_name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": "Decision tree root is a leaf; no split found."
            }

        feature_name = X_proc.columns[root_feature_index]
        threshold = float(clf.tree_.threshold[0])

        # Левое/правое разбиение
        feature_values = X_proc.iloc[:, root_feature_index].values
        left_mask = feature_values <= threshold
        right_mask = feature_values > threshold

        # Средние фичи по которой разбиваем
        group_0_mean = float(np.nanmean(feature_values[left_mask])) if left_mask.sum() > 0 else None
        group_1_mean = float(np.nanmean(feature_values[right_mask])) if right_mask.sum() > 0 else None


        # Вычисляем взвешенную среднюю Gini impurity дочерних узлов - единственное Gini-значение, которое возвращаем
        # Оно позволяет сделать вывод о характере разделения в последующем анализе
        left_node_idx = clf.tree_.children_left[0]
        right_node_idx = clf.tree_.children_right[0]

        # parent_impurity = float(clf.tree_.impurity[0])
        left_impurity = float(clf.tree_.impurity[left_node_idx])
        right_impurity = float(clf.tree_.impurity[right_node_idx])

        n_node_samples = clf.tree_.n_node_samples
        n_total = int(n_node_samples[0])
        n_left = int(n_node_samples[left_node_idx])
        n_right = int(n_node_samples[right_node_idx])

        if n_total == 0:
            weighted_child_impurity = None
        else:
            weighted_child_impurity = float((left_impurity * n_left + right_impurity * n_right) / n_total)


        summary = (f"Признак '{feature_name}' является наиболее важным для разделения по целевой перменной. "
                   f"Порог: {threshold:.6g}. Взвешенное среднее gini purity дочерних элементов : {weighted_child_impurity:.6g}.")

        details = {
            "best_feature": str(feature_name),
            "split_threshold": threshold,
            "weighted_child_gini_impurity": weighted_child_impurity,
            "group_0_mean": group_0_mean,
            "group_1_mean": group_1_mean,
            "n_left": int(left_mask.sum()),
            "n_right": int(right_mask.sum())
        }

        return {
            "tool_name": tool_name,
            "status": "success",
            "summary": summary,
            "details": details,
            "error_message": None
        }

    except Exception as e:
        return {
            "tool_name": tool_name,
            "status": "error",
            "summary": "",
            "details": {},
            "error_message": str(e)
        }



# =========================
#  Tool 2: Correlation Analysis
# =========================
def correlation_analysis(df: pd.DataFrame, target_column: str) -> Dict[str, Any]:
    """
    Корреляционный анализ (point-biserial) для бинарной целевой переменной.
    Возвращает: наиболее сильно коррелирующий признак, значение корреляции,
    топ-5 положительных и топ-5 отрицательных корреляций.
    """
    tool_name = "CorrelationAnalysis"
    try:
        # Если не найдена целевая переменная
        if target_column not in df.columns:
            return {
                "tool_name": tool_name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": f"target_column '{target_column}' not found in dataframe"
            }

        data = df.copy()

        # Разделяем на X и y
        X = data.drop(columns=[target_column])
        y = data[target_column]

        # Если нет фичей
        if X.shape[1] == 0:
            return {
                "tool_name": tool_name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": "No features found (df has only target column)."
            }

        # Кодируем целевую
        if y.dtype.kind not in "biufc":
            le = LabelEncoder()
            y_enc = le.fit_transform(y.astype(str))
        else:
            y_enc = y.astype(int).values

        # Проверка бинарности
        if len(np.unique(y_enc)) != 2:
            return {
                "tool_name": tool_name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": f"Target column '{target_column}' is not binary after encoding."
            }

        # Оставляем только числовые признаки
        X_proc = X.select_dtypes(include=['number']).copy()

        if X_proc.shape[1] == 0:
            return {
                "tool_name": tool_name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": "No numeric features available for correlation analysis."
            }

        correlations = {}
        for col in X_proc.columns:
            series = X_proc[col].dropna()
            if series.nunique() <= 1:
                continue  # Пропускаем признаки без вариации (дисперсии)
            try:
                corr, _ = pointbiserialr(y_enc[:len(series)], series)
                if not np.isnan(corr):
                    correlations[col] = corr
            except Exception:
                continue  # Пропускаем, если корреляция не считается

        if len(correlations) == 0:
            return {
                "tool_name": tool_name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": "No valid correlations could be computed."
            }

        # Сортировка
        sorted_corr = dict(sorted(correlations.items(), key=lambda x: x[1], reverse=True))
        top_pos = dict(list(sorted_corr.items())[:5])
        top_neg = dict(list(sorted_corr.items())[-5:])

        # Наиболее важный признак
        best_feature = next(iter(top_pos)) if top_pos else None
        best_corr_value = top_pos[best_feature] if best_feature else None

        summary = (
            f"Признак '{best_feature}' является наиболее сильно коррелирующим с целевой переменной '{target_column}'. "
            f"Коэффициент корреляции: {best_corr_value:.6g}."
        )

        details = {
            "top_positive": top_pos,
            "top_negative": top_neg,
            "correlation_method": "point-biserial",
            "n_features": len(correlations)
        }

        return {
            "tool_name": tool_name,
            "status": "success",
            "summary": summary,
            "details": details,
            "error_message": None
        }

    except Exception as e:
        return {
            "tool_name": tool_name,
            "status": "error",
            "summary": "",
            "details": {},
            "error_message": str(e)
        }