# tools/distribution_visualizer.py
# Анализ распределений ключевых признаков между группами.

import pandas as pd
import numpy as np
from typing import Dict, Any
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns

def distribution_visualizer(
    df: pd.DataFrame, target_column: str, top_k: int = 3, **kwargs) -> Dict[str, Any]:
    """
    Создаёт визуализации распределений для топ признаков.
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

        # Получаем топ признаки из других инструментов (можно передать как параметр)
        # Пока используем простой подход - числовые признаки с наибольшей вариацией
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

        visualizations = {}
        for feature in top_features:
            plt.figure(figsize=(10, 6))
            
            # Создаём boxplot для сравнения распределений
            sns.boxplot(data=df, x=target_column, y=feature)
            plt.title(f'Распределение {feature} по группам')
            plt.xlabel('Группа (0 - Отток, 1 - Удержание)')
            plt.ylabel(feature)
            
            # Сохраняем в base64 для включения в отчёт
            buffer = BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            plt.close()
            
            visualizations[feature] = {
                "image_base64": image_base64,
                "description": f"Boxplot распределения {feature} для групп 0 и 1"
            }

        summary = f"Созданы визуализации для {len(visualizations)} ключевых признаков"
        
        return {
            "tool_name": tool_name,
            "status": "success",
            "summary": summary,
            "details": {
                "visualizations": visualizations,
                "features_analyzed": top_features
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