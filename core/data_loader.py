# core/data_loader.py
import pandas as pd

def load_data(filepath: str) -> pd.DataFrame:
    """Загружает CSV-файл в DataFrame."""
    return pd.read_csv(filepath)