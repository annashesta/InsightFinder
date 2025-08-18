# tools/full_model_importance.py


import pandas as pd
from typing import Dict, Any
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

def full_model_importance(df: pd.DataFrame, target_column: str, top_k: int = 10, **kwargs) -> Dict[str, Any]:
    """
    Обучает RandomForestClassifier и возвращает топ-K важных признаков.
    """
    tool_name = "FullModelFeatureImportance"
    try:
        if target_column not in df.columns:
            return {"tool_name": tool_name, "status": "error", "summary": "", "details": {}, "error_message": f"target_column '{target_column}' not found"}

        X = df.drop(columns=[target_column])
        y = df[target_column]

        if y.dtype.kind not in "biufc":
            y = LabelEncoder().fit_transform(y.astype(str))
        else:
            y = y.astype(int).values

        X_proc = X.copy()
        for col in X_proc.columns:
            if X_proc[col].dtype.kind not in "biufc":
                X_proc[col] = LabelEncoder().fit_transform(X_proc[col].astype(str))
            else:
                X_proc[col] = X_proc[col].fillna(X_proc[col].median())

        if X_proc.empty:
            return {"tool_name": tool_name, "status": "error", "summary": "", "details": {}, "error_message": "No features after preprocessing"}

        clf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        clf.fit(X_proc, y)

        importances = clf.feature_importances_
        importance_df = pd.DataFrame({"feature": X_proc.columns, "importance": importances})
        top_features = importance_df.sort_values("importance", ascending=False).head(top_k)
        feat_dict = top_features.set_index("feature")["importance"].to_dict()

        summary = f"Топ-важный признак по RandomForest — '{next(iter(feat_dict))}'"

        return {"tool_name": tool_name, "status": "success", "summary": summary,
                "details": {"top_k": top_k, "feature_importances": feat_dict, "model": "RandomForestClassifier"},
                "error_message": None}

    except Exception as e:
        return {"tool_name": tool_name, "status": "error", "summary": "", "details": {}, "error_message": str(e)}
