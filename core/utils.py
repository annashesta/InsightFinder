# core/utils.py
import pandas as pd
import numpy as np


def make_serializable(obj):
    """
    Рекурсивно преобразует объект Python в сериализуемый формат (JSON-совместимый).

    Args:
        obj: Любой Python-объект.

    Returns:
        Объект, совместимый с JSON (dict, list, tuple, str, int, float, bool, None).
    """
    if isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_serializable(i) for i in obj]
    elif isinstance(obj, tuple):
        return tuple(make_serializable(i) for i in obj)
    elif isinstance(obj, set):
        return [make_serializable(i) for i in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return make_serializable(obj.tolist())
    elif pd.isna(obj):
        return None
    elif isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    else:
        return str(obj)


def find_binary_target(df: pd.DataFrame) -> str:
    """
    Находит первый столбец в DataFrame, который имеет ровно два уникальных значения.

    Args:
        df: Входной DataFrame.

    Returns:
        Название первого бинарного столбца.

    Raises:
        ValueError: Если бинарный столбец не найден.
    """
    for col in df.columns:
        if df[col].nunique() == 2:
            return col
    raise ValueError("Бинарная целевая переменная не найдена")


def make_target_binary(df: pd.DataFrame, target_column: str) -> pd.DataFrame:
    """
    Преобразует указанный столбец в бинарный формат (0/1).

    Сопоставляет строковые значения 'yes'/'no', 'true'/'false', '1'/'0' и т.д.
    Удаляет строки с нераспознанными значениями.

    Args:
        df: Входной DataFrame.
        target_column: Название столбца для преобразования.

    Returns:
        DataFrame с преобразованным target_column и отфильтрованными строками.

    Raises:
        ValueError: Если столбец не найден или все значения нераспознаны.
    """
    if target_column not in df.columns:
        raise ValueError(f"Столбец '{target_column}' не найден.")

    y = df[target_column].astype(str).str.strip().str.lower()
    mapping = {
        'yes': 1, 'no': 0,
        'true': 1, 'false': 0,
        '1': 1, '0': 0,
        '1.0': 1, '0.0': 0
    }
    y_mapped = y.map(mapping)

    if y_mapped.isnull().all():
        raise ValueError(f"Не удалось распознать значения в '{target_column}'.")

    valid_mask = y_mapped.notna()
    # Создаем копию, чтобы избежать SettingWithCopyWarning, если применимо
    df_filtered = df[valid_mask].copy()
    df_filtered[target_column] = y_mapped[valid_mask].astype(int)

    return df_filtered
