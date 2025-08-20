# tools/categorical_feature_analysis.py
import pandas as pd
from typing import Any, Dict, List
from scipy.stats import chi2_contingency
from sklearn.preprocessing import LabelEncoder


def categorical_feature_analysis(
    df: pd.DataFrame, target_column: str, p_value_threshold: float = 0.05, top_k: int = 15, **kwargs
) -> Dict[str, Any]:
    """
    Проверяет связь категориальных признаков с целевой переменной через тест Хи-квадрат.

    Args:
        df: Входной DataFrame.
        target_column: Имя бинарной целевой переменной.
        p_value_threshold: Порог p-value для значимости (по умолчанию 0.05).
        top_k: Количество топ признаков для возврата.
        **kwargs: Дополнительные параметры.

    Returns:
        Словарь с результатами анализа.
    """
    tool_name = "CategoricalFeatureAnalysis"
    try:
        if target_column not in df.columns:
            return {
                "tool_name": tool_name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": f"target_column '{target_column}' not found",
            }

        y = df[target_column]
        X = df.drop(columns=[target_column])

        if y.dtype.kind not in "biufc":
            y = LabelEncoder().fit_transform(y.astype(str))
        else:
            y = y.astype(int).values

        X_cat = X.select_dtypes(include=["object", "category"]).copy()
        if X_cat.empty:
            return {
                "tool_name": tool_name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": "No categorical features",
            }

        significant = {}
        for col in X_cat.columns:
            cross_tab = pd.crosstab(X_cat[col], y)
            if cross_tab.shape[0] < 2 or cross_tab.shape[1] < 2:
                continue
            try:
                chi2, p, dof, _ = chi2_contingency(cross_tab)
                if p < p_value_threshold:
                    significant[col] = {
                        "p_value": float(p),
                        "chi2": float(chi2),
                        "dof": int(dof),
                    }
            except Exception:
                continue

        # Сортировка по p-value
        sorted_significant = dict(sorted(significant.items(), key=lambda item: item[1]['p_value']))
        top_significant = dict(list(sorted_significant.items())[:top_k])

        if not top_significant:
            summary = "Нет категориальных признаков со значимой связью."
        else:
            count = len(top_significant)
            summary = f"Найдено {count} значимых категориальных признаков. Топ-{min(top_k, count)} по p-value."

        return {
            "tool_name": tool_name,
            "status": "success",
            "summary": summary,
            "details": {
                "p_value_threshold": p_value_threshold,
                "significant_features": top_significant, # Возвращаем отсортированный список
                "n_significant": len(significant),
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
