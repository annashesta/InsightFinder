# tools/categorical_feature_analysis.py

import pandas as pd
from typing import Any, Dict
from scipy.stats import chi2_contingency

def categorical_feature_analysis(df: pd.DataFrame, target_column: str, p_value_threshold: float = 0.05) -> Dict[str, Any]:
    """
    Для каждого категориального признака строит таблицу сопряжённости и тест Хи-квадрат.
    Возвращает признаки с p-value < 0.05.
    """
    tool_name = "CategoricalFeatureAnalysis"
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

        # Кодируем целевую переменную
        if y.dtype.kind not in "biufc":
            from sklearn.preprocessing import LabelEncoder
            y = LabelEncoder().fit_transform(y.astype(str))
        else:
            y = y.astype(int).values

        # Только категориальные признаки
        X_cat = X.select_dtypes(include=['object', 'category']).copy()
        if X_cat.shape[1] == 0:
            return {
                "tool_name": tool_name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": "No categorical features"
            }

        significant_features = {}
        for col in X_cat.columns:
            cross_tab = pd.crosstab(X_cat[col], y)
            if cross_tab.shape[0] < 2 or cross_tab.shape[1] < 2:
                continue
            try:
                chi2, p, dof, expected = chi2_contingency(cross_tab)
                if p < p_value_threshold:
                    significant_features[col] = {
                        "p_value": float(p),
                        "chi2_statistic": float(chi2),
                        "dof": int(dof)
                    }
            except:
                continue

        if not significant_features:
            summary = "Не найдено категориальных признаков со статистически значимой связью с целевой переменной (p < 0.05)."
        else:
            summary = f"Найдено {len(significant_features)} категориальных признаков со значимой связью с целевой переменной."

        return {
            "tool_name": tool_name,
            "status": "success",
            "summary": summary,
            "details": {
                "p_value_threshold": p_value_threshold,
                "significant_features": significant_features,
                "n_significant": len(significant_features)
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