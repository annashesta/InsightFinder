# tools/outlier_detector.py
# Обнаружение выбросов, которые могут влиять на результаты.
import pandas as pd
import numpy as np
from typing import Dict, Any
from scipy import stats

def outlier_detector(
    df: pd.DataFrame, target_column: str, method: str = "iqr", threshold: float = 1.5, **kwargs
) -> Dict[str, Any]:
    """
    Обнаруживает выбросы в числовых признаках.
    """
    tool_name = "OutlierDetector"
    try:
        if target_column not in df.columns:
            return {
                "tool_name": tool_name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": f"target_column '{target_column}' not found",
            }

        X_num = df.select_dtypes(include=["number"]).drop(columns=[target_column], errors='ignore')
        
        if X_num.empty:
            return {
                "tool_name": tool_name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": "No numeric features",
            }

        outliers_info = {}
        total_outliers = 0
        
        for col in X_num.columns:
            if method == "iqr":
                Q1 = X_num[col].quantile(0.25)
                Q3 = X_num[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                outliers = X_num[(X_num[col] < lower_bound) | (X_num[col] > upper_bound)]
            elif method == "zscore":
                z_scores = np.abs(stats.zscore(X_num[col].dropna()))
                outliers = X_num[z_scores > threshold]
            
            outlier_count = len(outliers)
            if outlier_count > 0:
                outliers_info[col] = {
                    "count": outlier_count,
                    "percentage": (outlier_count / len(X_num)) * 100,
                    "method": method
                }
                total_outliers += outlier_count

        if not outliers_info:
            summary = "Выбросы не обнаружены"
        else:
            summary = f"Обнаружено {total_outliers} выбросов в {len(outliers_info)} признаках"
        
        return {
            "tool_name": tool_name,
            "status": "success",
            "summary": summary,
            "details": {
                "outliers": outliers_info,
                "total_outliers": total_outliers,
                "method_used": method
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