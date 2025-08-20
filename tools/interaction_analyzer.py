# tools/interaction_analyzer.py
# Анализ взаимодействий между признаками.

import pandas as pd
import numpy as np
from typing import Dict, Any
from sklearn.preprocessing import LabelEncoder
from scipy.stats import pointbiserialr

def interaction_analyzer(
    df: pd.DataFrame, target_column: str, top_k: int = 5, **kwargs
) -> Dict[str, Any]:
    """
    Анализирует взаимодействия между признаками и целевой переменной.
    """
    tool_name = "InteractionAnalyzer"
    try:
        if target_column not in df.columns:
            return {
                "tool_name": tool_name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": f"target_column '{target_column}' not found",
            }

        y = df[target_column]
        X = df.drop(columns=[target_column])

        # Кодируем целевую переменную если нужно
        if y.dtype.kind not in "biufc":
            y = LabelEncoder().fit_transform(y.astype(str))
        else:
            y = y.astype(int).values

        # Разделяем числовые и категориальные признаки
        X_num = X.select_dtypes(include=["number"])
        X_cat = X.select_dtypes(include=["object", "category"])

        interactions = []

        # Анализ взаимодействий числовых признаков
        if not X_num.empty:
            for col in X_num.columns[:min(10, len(X_num.columns))]:  # Ограничиваем для скорости
                if X_num[col].nunique() <= 1:
                    continue
                try:
                    corr, _ = pointbiserialr(y[:len(X_num[col])], X_num[col])
                    if not np.isnan(corr):
                        interactions.append({
                            "feature": col,
                            "type": "numeric",
                            "correlation": float(corr),
                            "description": f"Числовой признак {col}"
                        })
                except Exception:
                    continue

        # Анализ категориальных признаков
        if not X_cat.empty:
            from scipy.stats import chi2_contingency
            for col in X_cat.columns[:min(10, len(X_cat.columns))]:
                try:
                    cross_tab = pd.crosstab(X_cat[col], y)
                    if cross_tab.shape[0] >= 2 and cross_tab.shape[1] >= 2:
                        chi2, p, dof, _ = chi2_contingency(cross_tab)
                        interactions.append({
                            "feature": col,
                            "type": "categorical",
                            "p_value": float(p),
                            "chi2": float(chi2),
                            "description": f"Категориальный признак {col}"
                        })
                except Exception:
                    continue

        # Сортируем по значимости
        interactions.sort(key=lambda x: (
            x.get('correlation', 0) if x['type'] == 'numeric' else -x.get('p_value', 1)
        ), reverse=True)

        top_interactions = interactions[:top_k]

        if not top_interactions:
            summary = "Взаимодействия не найдены"
        else:
            summary = f"Найдено {len(top_interactions)} значимых взаимодействий"

        return {
            "tool_name": tool_name,
            "status": "success",
            "summary": summary,
            "details": {
                "interactions": top_interactions,
                "total_analyzed": len(interactions)
            },
            "error_message": None,
        }

    except Exception as e:
        return {
            "tool_name": tool_name,
            "status": "error",
            "summary": "",
            "details": {},
            "error_message": str(e),
        }