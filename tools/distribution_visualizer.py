# tools/distribution_visualizer.py
# Анализ распределений ключевых признаков между группами.

import pandas as pd
import numpy as np
from typing import Dict, Any
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pathlib import Path


def distribution_visualizer(
    df: pd.DataFrame, target_column: str, top_k: int = 3, output_dir: str = "report/output/images", **kwargs
) -> Dict[str, Any]:
    """
    Создаёт визуализации распределений для топ признаков и сохраняет их как файлы.

    Args:
        df: Входной DataFrame.
        target_column: Имя бинарной целевой переменной.
        top_k: Количество топ признаков для визуализации.
        output_dir: Директория для сохранения изображений.
        **kwargs: Дополнительные параметры.

    Returns:
        Словарь с результатами анализа.
    """
    tool_name = "DistributionVisualizer"
    try:
        if target_column not in df.columns:
            return {
                "tool_name": tool_name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": f"target_column '{target_column}' not found",
            }

        # Создаем директорию для изображений, если её нет
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Получаем числовые признаки
        X_num = df.select_dtypes(include=["number"]).drop(columns=[target_column], errors='ignore')
        
        if X_num.empty:
            return {
                "tool_name": tool_name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": "No numeric features for visualization",
            }

        # Находим признаки с наибольшей вариацией
        variance_scores = X_num.var().sort_values(ascending=False)
        top_features = variance_scores.head(top_k).index.tolist()

        saved_images = {}
        for feature in top_features:
            plt.figure(figsize=(10, 6))
            
            # Создаём boxplot для сравнения распределений
            try:
                sns.boxplot(data=df, x=target_column, y=feature)
                plt.title(f'Распределение {feature} по группам')
                plt.xlabel('Группа (0 - Отток, 1 - Удержание)')
                plt.ylabel(feature)
                
                # Формируем имя файла
                safe_feature_name = "".join(c for c in feature if c.isalnum() or c in (' ', '_')).rstrip()
                filename = f"{safe_feature_name}.png"
                filepath = os.path.join(output_dir, filename)
                
                # Сохраняем изображение
                plt.savefig(filepath, format='png', bbox_inches='tight', dpi=150)
                plt.close()
                
                saved_images[feature] = {
                    "file_path": filepath,
                    "relative_path": f"images/{filename}", # Путь относительно report/output
                    "description": f"Boxplot распределения {feature} для групп 0 и 1"
                }
            except Exception as e:
                plt.close() # Убедиться, что фигура закрыта в случае ошибки
                # Просто пропускаем признак, если не удалось построить график
                continue

        if not saved_images:
            summary = "Не удалось создать визуализации"
        else:
            count = len(saved_images)
            summary = f"Созданы визуализации для {count} ключевых признаков"

        return {
            "tool_name": tool_name,
            "status": "success",
            "summary": summary,
            "details": {
                "saved_images": saved_images,
                "features_analyzed": list(saved_images.keys())
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
