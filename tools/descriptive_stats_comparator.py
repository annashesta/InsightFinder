# tools/descriptive_stats_comparator.py

import pandas as pd
from typing import Any, Dict

def descriptive_stats_comparator(df: pd.DataFrame, target_column: str, threshold_ratio: float = 0.2) -> Dict[str, Any]:
    """
    Сравнивает mean, median, std по группам (0 и 1) целевой переменной.
    Возвращает признаки, где разница в mean или median > threshold_ratio (по умолчанию 20%).
    """
    tool_name = "DescriptiveStatsComparator"
    try:
        if target_column not in df.columns:
            return {
                "tool_name": tool_name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": f"target_column '{target_column}' not found"
            }

        data = df.copy()
        y = data[target_column]
        X = data.drop(columns=[target_column])

        # Кодируем целевую переменную, если нужно
        if y.dtype.kind not in "biufc":
            from sklearn.preprocessing import LabelEncoder
            y = LabelEncoder().fit_transform(y.astype(str))
        else:
            y = y.astype(int).values

        # Только числовые признаки
        X_num = X.select_dtypes(include=['number']).copy()
        if X_num.shape[1] == 0:
            return {
                "tool_name": tool_name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": "No numeric features"
            }

        # Добавляем целевую переменную
        X_num[target_column] = y
        grouped = X_num.groupby(target_column).agg(['mean', 'median', 'std'])

        # Переименовываем столбцы
        grouped.columns = ['_'.join(col).strip() for col in grouped.columns]

        # Извлекаем группы
        try:
            stats_0 = grouped.loc[0]
            stats_1 = grouped.loc[1]
        except KeyError:
            return {
                "tool_name": tool_name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": "Target column is not binary after encoding"
            }

        # Сравниваем mean и median
        significant_diffs = {}
        for col in X_num.columns[:-1]:  # Все, кроме целевой
            for stat in ['mean', 'median']:
                val_0 = stats_0[f"{col}_{stat}"]
                val_1 = stats_1[f"{col}_{stat}"]
                if val_0 == 0 and val_1 == 0:
                    continue
                # Относительная разница
                rel_diff = abs(val_1 - val_0) / (max(abs(val_0), abs(val_1)) + 1e-8)
                if rel_diff > threshold_ratio:
                    key = f"{col}_{stat}"
                    significant_diffs[key] = {
                        "group_0": float(val_0),
                        "group_1": float(val_1),
                        "relative_difference": float(rel_diff)
                    }

        if not significant_diffs:
            summary = "Не найдено признаков с разницей средних или медиан > 20% между группами."
        else:
            top_feature = next(iter(significant_diffs))
            summary = f"Наибольшие различия между группами — у признака '{top_feature.split('_')[0]}' (по {top_feature.split('_')[1]})."

        return {
            "tool_name": tool_name,
            "status": "success",
            "summary": summary,
            "details": {
                "threshold_ratio": threshold_ratio,
                "significant_differences": significant_diffs,
                "n_features_with_diff": len(significant_diffs)
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