# tools/correlation_analysis.py
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from scipy.stats import pointbiserialr
from sklearn.preprocessing import LabelEncoder


def correlation_analysis(
    df: pd.DataFrame, target_column: str, top_k: int = 5, **kwargs
) -> Dict[str, Any]:
    """
    Считает point-biserial корреляции между числовыми признаками и бинарной целью.

    Args:
        df: Входной DataFrame.
        target_column: Имя бинарной целевой переменной.
        top_k: Количество топ признаков для возврата.
        **kwargs: Дополнительные параметры (не используются).

    Returns:
        Словарь с результатами анализа.
    """
    tool_name = "CorrelationAnalysis"
    try:
        if target_column not in df.columns:
            return {
                "tool_name": tool_name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": f"target_column '{target_column}' not found",
            }

        X = df.drop(columns=[target_column])
        y = df[target_column]

        # Кодируем целевую
        if y.dtype.kind not in "biufc":
            y = LabelEncoder().fit_transform(y.astype(str))
        else:
            y = y.astype(int).values

        if len(np.unique(y)) != 2:
            return {
                "tool_name": tool_name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": "Target must be binary",
            }

        X_num = X.select_dtypes(include=["number"]).copy()
        if X_num.empty:
            return {
                "tool_name": tool_name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": "No numeric features",
            }

        correlations = {}
        for col in X_num.columns:
            if X_num[col].nunique() <= 1:
                continue
            try:
                corr, _ = pointbiserialr(y[: len(X_num[col])], X_num[col])
                if not np.isnan(corr):
                    correlations[col] = corr
            except Exception:
                continue

        if not correlations:
            return {
                "tool_name": tool_name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": "No correlations computed",
            }

        # Сортировка по абсолютному значению корреляции
        sorted_items = sorted(correlations.items(), key=lambda x: abs(x[1]), reverse=True)
        
        top_pos_items = [item for item in sorted_items if item[1] >= 0][:top_k]
        top_neg_items = [item for item in sorted_items if item[1] < 0][-top_k:]
        
        top_pos = dict(top_pos_items)
        top_neg = dict(top_neg_items)

        if not top_pos and not top_neg:
             summary = "Не найдены значимые корреляции."
        else:
             pos_count = len(top_pos)
             neg_count = len(top_neg)
             summary = f"Найдены корреляции: {pos_count} положительных, {neg_count} отрицательных. Топ по модулю."

        return {
            "tool_name": tool_name,
            "status": "success",
            "summary": summary,
            "details": {
                "top_positive": top_pos, # Словарь
                "top_negative": top_neg, # Словарь
                "all_correlations_sorted": sorted_items, # Полный список для отчета
                "n_features_analyzed": len(correlations),
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
