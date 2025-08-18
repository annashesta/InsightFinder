# tools/primary_feature_finder.py

import numpy as np
import pandas as pd
from typing import Dict, Any
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder

def primary_feature_finder(df: pd.DataFrame, target_column: str) -> Dict[str, Any]:
    """
    Обучает решающее дерево глубины 1 (Decision Stump) для поиска самого важного признака,
    разделяющего данные по бинарной целевой переменной.

    Возвращает:
        - Лучший признак и порог разделения
        - Information Gain (уменьшение неоднородности)
        - Средние значения признака в двух группах
        - Размеры дочерних узлов

    Args:
        df (pd.DataFrame): Входной датасет.
        target_column (str): Имя столбца с бинарной целевой переменной.

    Returns:
        Dict[str, Any]: Словарь с результатами анализа.
    """
    tool_name = "PrimaryFeatureFinder"

    try:
        if target_column not in df.columns:
            return {
                "tool_name": tool_name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": f"Целевая переменная '{target_column}' не найдена в данных."
            }

        data = df.copy()
        X = data.drop(columns=[target_column])
        y = data[target_column]

        if X.shape[1] == 0:
            return {
                "tool_name": tool_name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": "Нет признаков: датасет содержит только целевую переменную."
            }

        # Кодируем целевую переменную
        if y.dtype.kind not in "biufc":
            le = LabelEncoder()
            y_enc = le.fit_transform(y.astype(str))
        else:
            y_enc = y.astype(int).values

        # Преобразуем категориальные признаки
        X_proc = X.copy()
        for col in X_proc.columns:
            if X_proc[col].dtype.kind not in "biufc":
                le = LabelEncoder()
                X_proc[col] = le.fit_transform(X_proc[col].astype(str))
            else:
                X_proc[col] = X_proc[col].fillna(X_proc[col].median())  # Заполняем NaN

        if X_proc.shape[1] == 0:
            return {
                "tool_name": tool_name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": "Нет признаков после предобработки."
            }

        # Обучаем дерево
        clf = DecisionTreeClassifier(max_depth=1, random_state=42)
        clf.fit(X_proc.values, y_enc)

        feature_idx = int(clf.tree_.feature[0])
        if feature_idx == -2:  # Нет сплита
            return {
                "tool_name": tool_name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": "Не удалось найти разделение (дерево не разделилось)."
            }

        feature_name = X_proc.columns[feature_idx]
        threshold = float(clf.tree_.threshold[0])

        # Группы
        values = X_proc.iloc[:, feature_idx].values
        left_mask = values <= threshold
        right_mask = values > threshold

        group_0_mean = float(np.nanmean(values[left_mask])) if left_mask.sum() > 0 else None
        group_1_mean = float(np.nanmean(values[right_mask])) if right_mask.sum() > 0 else None

        # Information Gain
        parent_impurity = float(clf.tree_.impurity[0])
        left_impurity = float(clf.tree_.impurity[clf.tree_.children_left[0]])
        right_impurity = float(clf.tree_.impurity[clf.tree_.children_right[0]])

        n_total = clf.tree_.n_node_samples[0]
        n_left = clf.tree_.n_node_samples[clf.tree_.children_left[0]]
        n_right = clf.tree_.n_node_samples[clf.tree_.children_right[0]]

        weighted_child_impurity = (left_impurity * n_left + right_impurity * n_right) / n_total
        information_gain = parent_impurity - weighted_child_impurity

        summary = (
            f"Признак '{feature_name}' является наиболее важным для разделения. "
            f"Порог: {threshold:.6g}. Прирост информации (Information Gain): {information_gain:.6g}."
        )

        details = {
            "best_feature": str(feature_name),
            "split_threshold": threshold,
            "information_gain": information_gain,
            "group_0_mean": group_0_mean,
            "group_1_mean": group_1_mean,
            "n_left": int(n_left),
            "n_right": int(n_right)
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