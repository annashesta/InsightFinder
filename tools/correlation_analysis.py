# tools/correlation_analysis.py

import numpy as np
import pandas as pd
from typing import Dict, Any
from scipy.stats import pointbiserialr
from sklearn.preprocessing import LabelEncoder

def correlation_analysis(df: pd.DataFrame, target_column: str, **kwargs) -> Dict[str, Any]:
    """
    Считает point-biserial корреляции между числовыми признаками и бинарной целью.
    """
    tool_name = "CorrelationAnalysis"
    try:
        if target_column not in df.columns:
            return {"tool_name": tool_name, "status": "error", "summary": "", "details": {}, "error_message": f"target_column '{target_column}' not found"}

        X = df.drop(columns=[target_column])
        y = df[target_column]

        if y.dtype.kind not in "biufc":
            y = LabelEncoder().fit_transform(y.astype(str))
        else:
            y = y.astype(int).values

        if len(np.unique(y)) != 2:
            return {"tool_name": tool_name, "status": "error", "summary": "", "details": {}, "error_message": "Target must be binary"}

        X_num = X.select_dtypes(include=["number"]).copy()
        if X_num.empty:
            return {"tool_name": tool_name, "status": "error", "summary": "", "details": {}, "error_message": "No numeric features"}

        correlations = {}
        for col in X_num.columns:
            if X_num[col].nunique() <= 1:
                continue
            try:
                corr, _ = pointbiserialr(y[:len(X_num[col])], X_num[col])
                if not np.isnan(corr):
                    correlations[col] = corr
            except Exception:
                continue

        if not correlations:
            return {"tool_name": tool_name, "status": "error", "summary": "", "details": {}, "error_message": "No correlations computed"}

        sorted_corr = dict(sorted(correlations.items(), key=lambda x: x[1], reverse=True))
        top_pos = dict(list(sorted_corr.items())[:5])
        top_neg = dict(list(sorted_corr.items())[-5:])
        best_feature = next(iter(top_pos))
        best_corr = top_pos[best_feature]

        summary = f"Лучший признак по корреляции: '{best_feature}' (r={best_corr:.3f})"

        return {"tool_name": tool_name, "status": "success", "summary": summary,
                "details": {"top_positive": top_pos, "top_negative": top_neg, "n_features_analyzed": len(correlations)},
                "error_message": None}

    except Exception as e:
        return {"tool_name": tool_name, "status": "error", "summary": "", "details": {}, "error_message": str(e)}
