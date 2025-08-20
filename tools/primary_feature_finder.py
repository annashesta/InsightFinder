# tools/primary_feature_finder.py

import numpy as np
import pandas as pd
from typing import Dict, Any
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder

def primary_feature_finder(df: pd.DataFrame, target_column: str, **kwargs) -> Dict[str, Any]:
    """
    Обучает решающее дерево глубины 1 для поиска самого важного признака.
    """
    tool_name = "PrimaryFeatureFinder"
    try:
        if target_column not in df.columns:
            return {
                "tool_name": tool_name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": f"target_column '{target_column}' not found"
            }

        X = df.drop(columns=[target_column])
        y = df[target_column]

        if X.shape[1] == 0:
            return {
                "tool_name": tool_name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": "Dataset has only target column"
            }

        # Кодируем целевую переменную
        if y.dtype.kind not in "biufc":
            y = LabelEncoder().fit_transform(y.astype(str))
        else:
            y = y.astype(int).values

        # ✅ КРИТИЧЕСКАЯ ПРОВЕРКА: целевая переменная должна быть бинарной
        unique_classes = np.unique(y)
        if len(unique_classes) != 2:
            return {
                "tool_name": tool_name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": f"Target column must be binary. Found {len(unique_classes)} classes: {unique_classes.tolist()}"
            }

        # Кодируем признаки
        X_proc = X.copy()
        for col in X_proc.columns:
            if X_proc[col].dtype.kind not in "biufc":
                X_proc[col] = LabelEncoder().fit_transform(X_proc[col].astype(str))
            else:
                X_proc[col] = X_proc[col].fillna(X_proc[col].median())

        # Обучаем дерево
        clf = DecisionTreeClassifier(max_depth=1, random_state=42)
        clf.fit(X_proc.values, y)

        feature_idx = int(clf.tree_.feature[0])
        if feature_idx == -2:
            return {
                "tool_name": tool_name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": "Decision tree did not split"
            }

        feature_name = X_proc.columns[feature_idx]
        threshold = float(clf.tree_.threshold[0])

        n_total = clf.tree_.n_node_samples[0]
        n_left = clf.tree_.n_node_samples[clf.tree_.children_left[0]]
        n_right = clf.tree_.n_node_samples[clf.tree_.children_right[0]]
        parent_impurity = float(clf.tree_.impurity[0])
        left_impurity = float(clf.tree_.impurity[clf.tree_.children_left[0]])
        right_impurity = float(clf.tree_.impurity[clf.tree_.children_right[0]])
        weighted_child_impurity = (left_impurity * n_left + right_impurity * n_right) / n_total
        information_gain = parent_impurity - weighted_child_impurity

        summary = (
            f"Признак '{feature_name}' выбран деревом как главный. "
            f"Порог={threshold:.4f}, Information Gain={information_gain:.4f}"
        )

        return {
            "tool_name": str(tool_name),
            "status": "success",
            "summary": summary,
            "details": {
                "best_feature": feature_name,
                "split_threshold": float(threshold),
                "information_gain": float(information_gain),
                "n_left": int(n_left),
                "n_right": int(n_right)
            },
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