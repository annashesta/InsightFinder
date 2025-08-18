# tools/correlation_analysis.py

import numpy as np
import pandas as pd
from typing import Dict, Any
from scipy.stats import pointbiserialr
from sklearn.preprocessing import LabelEncoder

def correlation_analysis(df: pd.DataFrame, target_column: str) -> Dict[str, Any]:
    """
    Выполняет корреляционный анализ с помощью коэффициента point-biserial
    между числовыми признаками и бинарной целевой переменной.

    Возвращает:
        - Топ-5 положительных и отрицательных корреляций
        - Наиболее коррелирующий признак
        - Метод и количество признаков

    Args:
        df (pd.DataFrame): Входной датасет.
        target_column (str): Имя столбца с бинарной целевой переменной.

    Returns:
        Dict[str, Any]: Словарь с результатами анализа.
    """
    tool_name = "CorrelationAnalysis"

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

        if len(np.unique(y_enc)) != 2:
            return {
                "tool_name": tool_name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": f"Целевая переменная '{target_column}' не является бинарной после кодирования."
            }

        # Только числовые признаки
        X_num = X.select_dtypes(include=["number"]).copy()

        if X_num.shape[1] == 0:
            return {
                "tool_name": tool_name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": "Нет числовых признаков для анализа корреляции."
            }

        correlations = {}
        for col in X_num.columns:
            series = X_num[col].dropna()
            if series.nunique() <= 1:
                continue  # Нет вариации
            try:
                corr, _ = pointbiserialr(y_enc[:len(series)], series)
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
                "error_message": "Не удалось вычислить ни одну корреляцию."
            }

        # Сортируем
        sorted_corr = dict(sorted(correlations.items(), key=lambda x: x[1], reverse=True))
        top_pos = dict(list(sorted_corr.items())[:5])
        top_neg = dict(list(sorted_corr.items())[-5:])

        best_feature = next(iter(top_pos))
        best_corr = top_pos[best_feature]

        summary = (
            f"Наиболее сильно положительно коррелирует признак '{best_feature}' "
            f"с коэффициентом корреляции {best_corr:.6g}."
        )

        details = {
            "top_positive": top_pos,
            "top_negative": top_neg,
            "correlation_method": "point-biserial",
            "n_features_analyzed": len(correlations)
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