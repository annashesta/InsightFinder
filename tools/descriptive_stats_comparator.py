# tools/descriptive_stats_comparator.py
import pandas as pd
from typing import Dict, Any
from sklearn.preprocessing import LabelEncoder


def descriptive_stats_comparator(
    df: pd.DataFrame, target_column: str, threshold_ratio: float = 0.2, **kwargs
) -> Dict[str, Any]:
    """
    Сравнивает mean, median, std, min, max по группам (0 и 1).

    Args:
        df: Входной DataFrame.
        target_column: Имя бинарной целевой переменной.
        threshold_ratio: Порог относительного различия (по умолчанию 0.2).
        **kwargs: Дополнительные параметры.

    Returns:
        Словарь с результатами анализа.
    """
    tool_name = "DescriptiveStatsComparator"
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

        if y.dtype.kind not in "biufc":
            y = LabelEncoder().fit_transform(y.astype(str))
        else:
            y = y.astype(int).values

        X_num = X.select_dtypes(include=["number"]).copy()
        if X_num.empty:
            return {
                "tool_name": tool_name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": "No numeric features",
            }

        X_num[target_column] = y
        grouped = X_num.groupby(target_column).agg(["mean", "median", "std", "min", "max"])
        grouped.columns = ["_".join(col) for col in grouped.columns]

        try:
            stats_0 = grouped.loc[0]
            stats_1 = grouped.loc[1]
        except KeyError:
            return {
                "tool_name": tool_name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": "Target not binary",
            }

        diffs = {}
        for col in X_num.columns[:-1]:
            for stat in ["mean", "median", "std", "min", "max"]:
                val_0 = stats_0[f"{col}_{stat}"]
                val_1 = stats_1[f"{col}_{stat}"]
                if val_0 == 0 and val_1 == 0:
                    continue
                rel_diff = abs(val_1 - val_0) / (max(abs(val_0), abs(val_1)) + 1e-8)
                if rel_diff > threshold_ratio:
                    diffs[f"{col}_{stat}"] = {
                        "group_0": float(val_0),
                        "group_1": float(val_1),
                        "relative_difference": float(rel_diff),
                    }

        if not diffs:
            summary = f"Нет значимых различий > {threshold_ratio*100:.0f}%"
        else:
            top = next(iter(diffs))
            feature, stat = top.split("_", 1)
            summary = f"Наибольшие различия у признака '{feature}' по {stat}."

        return {
            "tool_name": tool_name,
            "status": "success",
            "summary": summary,
            "details": {
                "threshold_ratio": threshold_ratio,
                "significant_differences": diffs,
                "n_features_with_diff": len(diffs),
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