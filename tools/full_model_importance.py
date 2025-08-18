# tools/full_model_importance.py

import pandas as pd
from typing import Any, Dict
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

def full_model_feature_importance(df: pd.DataFrame, target_column: str, top_k: int = 10) -> Dict[str, Any]:
    """
    Обучает RandomForestClassifier, возвращает топ-K важных признаков.
    """
    tool_name = "FullModelFeatureImportance"
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
        X = data.drop(columns=[target_column])
        y = data[target_column]

        # Кодируем целевую
        if y.dtype.kind not in "biufc":
            le = LabelEncoder()
            y = le.fit_transform(y.astype(str))
        else:
            y = y.astype(int).values

        # Кодируем категориальные признаки
        X_proc = X.copy()
        for col in X_proc.columns:
            if X_proc[col].dtype.kind not in "biufc":
                le = LabelEncoder()
                X_proc[col] = le.fit_transform(X_proc[col].astype(str))
            else:
                X_proc[col] = X_proc[col].fillna(X_proc[col].median())

        if X_proc.shape[1] == 0:
            return {
                "tool_name": tool_name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": "No features after preprocessing"
            }

        # Обучаем модель
        clf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        clf.fit(X_proc.values, y)

        # Важность признаков
        importances = clf.feature_importances_
        feature_names = X_proc.columns
        importance_df = pd.DataFrame({'feature': feature_names, 'importance': importances})
        importance_df = importance_df.sort_values('importance', ascending=False).head(top_k)

        top_features = importance_df.set_index('feature')['importance'].to_dict()

        summary = f"Топ-важный признак по модели Random Forest — '{next(iter(top_features))}'."

        return {
            "tool_name": tool_name,
            "status": "success",
            "summary": summary,
            "details": {
                "top_k": top_k,
                "feature_importances": top_features,
                "model": "RandomForestClassifier"
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