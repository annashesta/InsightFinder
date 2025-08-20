# core/utils.py
import pandas as pd
import numpy as np


def make_serializable(obj):
    if isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_serializable(i) for i in obj]
    elif isinstance(obj, (np.integer, int)):
        return int(obj)
    elif isinstance(obj, (np.floating, float)):
        return float(obj)
    elif pd.isna(obj):
        return None
    elif isinstance(obj, (str, bool)) or obj is None:
        return obj
    else:
        return str(obj)


def find_binary_target(df: pd.DataFrame) -> str:
    for col in df.columns:
        if df[col].nunique() == 2:
            return col
    raise ValueError("Бинарная целевая переменная не найдена")


def make_target_binary(df: pd.DataFrame, target_column: str) -> pd.DataFrame:
    if target_column not in df.columns:
        raise ValueError(f"Столбец '{target_column}' не найден.")

    y = df[target_column].astype(str).str.strip().str.lower()
    mapping = {'yes': 1, 'no': 0, 'true': 1, 'false': 0, '1': 1, '0': 0, '1.0': 1, '0.0': 0}
    y_mapped = y.map(mapping)

    if y_mapped.isnull().all():
        raise ValueError(f"Не удалось распознать значения в '{target_column}'.")

    valid_mask = y_mapped.notna()
    df = df[valid_mask].copy()
    df[target_column] = y_mapped[valid_mask].astype(int)

    return df