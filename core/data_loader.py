# core/data_loader.py
import pandas as pd


def load_data(filepath: str) -> pd.DataFrame:
    """
    Загружает CSV-файл в DataFrame.

    Args:
        filepath: Путь к CSV-файлу.

    Returns:
        DataFrame с данными.

    Raises:
        FileNotFoundError: Если файл не найден.
        pd.errors.EmptyDataError: Если файл пуст.
        pd.errors.ParserError: Если ошибка парсинга.
    """
    try:
        df = pd.read_csv(filepath)
        print(f"✅ Загружено {len(df)} строк и {len(df.columns)} столбцов")
        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"Файл не найден: {filepath}")
    except pd.errors.EmptyDataError:
        raise ValueError(f"Файл пуст: {filepath}")
    except pd.errors.ParserError as e:
        raise ValueError(f"Ошибка парсинга CSV: {e}")