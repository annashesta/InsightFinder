# tools/insight_driven_visualizer.py
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, Any, List
from sklearn.preprocessing import LabelEncoder
from core.logger import get_logger

logger = get_logger(__name__, "orchestrator.log")

def _safe_feature_name(name: str) -> str:
    """Создает безопасное имя файла из названия признака."""
    return "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).rstrip()


def _plot_boxplot(df: pd.DataFrame, feature: str, target_column: str, output_dir: str, prefix: str = ""):
    """Строит и сохраняет boxplot."""
    try:
        plt.figure(figsize=(8, 5))
        sns.boxplot(data=df, x=target_column, y=feature)
        plt.title(f'{prefix}Распределение {feature} по группам')
        plt.xlabel('Группа')
        plt.ylabel(feature)
        filename = f"{prefix}{_safe_feature_name(feature)}_boxplot.png"
        filepath = os.path.join(output_dir, filename)
        plt.savefig(filepath, bbox_inches='tight', dpi=150)
        plt.close()
        return filepath
    except Exception as e:
        plt.close()
        return None


def _plot_histograms(df: pd.DataFrame, feature: str, target_column: str, output_dir: str, prefix: str = ""):
    """Строит и сохраняет гистограммы для групп."""
    try:
        plt.figure(figsize=(10, 5))
        for val in sorted(df[target_column].dropna().unique()):
            subset = df[df[target_column] == val][feature].dropna()
            if not subset.empty:
                sns.histplot(subset, kde=True, label=f'Группа {val}', alpha=0.6)
        plt.title(f'{prefix}Гистограмма {feature} по группам')
        plt.xlabel(feature)
        plt.ylabel('Плотность')
        plt.legend()
        filename = f"{prefix}{_safe_feature_name(feature)}_hist.png"
        filepath = os.path.join(output_dir, filename)
        plt.savefig(filepath, bbox_inches='tight', dpi=150)
        plt.close()
        return filepath
    except Exception as e:
        plt.close()
        return None


def _plot_scatter(df: pd.DataFrame, feature: str, target_column: str, output_dir: str, prefix: str = ""):
    """Строит и сохраняет scatter plot."""
    try:
        plt.figure(figsize=(8, 5))
        # Для бинарной переменной jitter может помочь
        x = df[feature]
        y = df[target_column] + np.random.normal(0, 0.05, size=len(df)) # небольшой jitter
        plt.scatter(x, y, alpha=0.5, s=10)
        plt.xlabel(feature)
        plt.ylabel(target_column)
        plt.title(f'{prefix}Диаграмма рассеяния {feature} vs {target_column}')
        filename = f"{prefix}{_safe_feature_name(feature)}_scatter.png"
        filepath = os.path.join(output_dir, filename)
        plt.savefig(filepath, bbox_inches='tight', dpi=150)
        plt.close()
        return filepath
    except Exception as e:
        plt.close()
        return None


def _plot_stacked_bar(df: pd.DataFrame, feature: str, target_column: str, output_dir: str, prefix: str = ""):
    """Строит и сохраняет stacked bar chart."""
    try:
        crosstab = pd.crosstab(df[feature], df[target_column], normalize='index')
        ax = crosstab.plot(kind='bar', stacked=True, figsize=(10, 6))
        plt.title(f'{prefix}Доля групп по {feature}')
        plt.xlabel(feature)
        plt.ylabel('Доля')
        plt.xticks(rotation=45, ha='right')
        plt.legend(title=target_column)
        filename = f"{prefix}{_safe_feature_name(feature)}_stacked_bar.png"
        filepath = os.path.join(output_dir, filename)
        plt.savefig(filepath, bbox_inches='tight', dpi=150)
        plt.close()
        return filepath
    except Exception as e:
        plt.close()
        return None


def _plot_feature_importance(importances: Dict[str, float], output_dir: str, prefix: str = ""):
    """Строит и сохраняет bar chart важности признаков."""
    try:
        if not importances:
            return None
        sorted_features = sorted(importances.items(), key=lambda item: item[1], reverse=True)
        features, scores = zip(*sorted_features)
        
        plt.figure(figsize=(10, max(6, len(features) * 0.3)))
        bars = plt.barh(features, scores, color='skyblue')
        plt.xlabel('Важность')
        plt.title(f'{prefix}Важность признаков (Random Forest)')
        plt.gca().invert_yaxis() # Наиболее важные сверху

        # Добавление значений на бары
        for bar, value in zip(bars, scores):
            plt.text(bar.get_width() + max(scores)*0.01, bar.get_y() + bar.get_height()/2,
                     f'{value:.4f}', va='center', ha='left')

        filename = f"{prefix}feature_importance.png"
        filepath = os.path.join(output_dir, filename)
        plt.savefig(filepath, bbox_inches='tight', dpi=150)
        plt.close()
        return filepath
    except Exception as e:
        plt.close()
        return None


def _plot_outlier_summary(outliers_info: Dict[str, Any], output_dir: str, prefix: str = ""):
    """Строит и сохраняет bar chart количества выбросов."""
    try:
        if not outliers_info:
            return None
            
        features = list(outliers_info.keys())
        counts = [info.get('count', 0) for info in outliers_info.values()]
        
        plt.figure(figsize=(10, max(6, len(features) * 0.3)))
        bars = plt.barh(features, counts, color='salmon')
        plt.xlabel('Количество выбросов')
        plt.title(f'{prefix}Количество выбросов по признакам')
        plt.gca().invert_yaxis()

        # Добавление значений на бары
        for bar, value in zip(bars, counts):
            plt.text(bar.get_width() + max(counts)*0.01, bar.get_y() + bar.get_height()/2,
                     f'{value}', va='center', ha='left')

        filename = f"{prefix}outlier_summary.png"
        filepath = os.path.join(output_dir, filename)
        plt.savefig(filepath, bbox_inches='tight', dpi=150)
        plt.close()
        return filepath
    except Exception as e:
        plt.close()
        return None


def insight_driven_visualizer(
    df: pd.DataFrame,
    target_column: str,
    analysis_results: List[Dict[str, Any]], # Это будет history из orchestrator
    output_dir: str = "report/output/images",
    top_k: int = 3,
    **kwargs
) -> Dict[str, Any]:
    """
    Создаёт визуализации, основанные на результатах предыдущих анализов.

    Args:
        df: Входной DataFrame.
        target_column: Имя бинарной целевой переменной.
        analysis_results: Список результатов от предыдущих инструментов (history).
        output_dir: Директория для сохранения изображений.
        top_k: Количество топ признаков для визуализации из каждого анализа.
        **kwargs: Дополнительные параметры.

    Returns:
        Словарь с результатами анализа.
    """
    tool_name = "InsightDrivenVisualizer"
    try:
        # Создаем директорию для изображений, если её нет
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        saved_plots = {}
        plot_count = 0

        # 1. Визуализация результатов DescriptiveStatsComparator
        desc_results = [r for r in analysis_results if r["tool_name"] == "DescriptiveStatsComparator" and r["status"] == "success"]
        if desc_results:
            desc_result = desc_results[0]
            diffs = desc_result.get("details", {}).get("significant_differences", [])
            # diffs это список словарей, берем feature_stat и выделяем имя признака
            top_diff_items = diffs[:top_k]
            for item in top_diff_items:
                feature_stat = item.get("feature_stat", "")
                if '_' in feature_stat:
                    feature = feature_stat.split('_')[0]
                else:
                    feature = feature_stat
                    
                if feature in df.columns and feature != target_column:
                    bp_path = _plot_boxplot(df, feature, target_column, output_dir, prefix=f"desc_")
                    hist_path = _plot_histograms(df, feature, target_column, output_dir, prefix=f"desc_")
                    if bp_path or hist_path:
                        saved_plots[f"desc_{feature}"] = {
                            "boxplot": bp_path,
                            "histogram": hist_path,
                            "description": f"Визуализация для {feature} из DescriptiveStatsComparator"
                        }
                        plot_count += 1

        # 2. Визуализация результатов CorrelationAnalysis
        corr_results = [r for r in analysis_results if r["tool_name"] == "CorrelationAnalysis" and r["status"] == "success"]
        if corr_results:
            corr_result = corr_results[0]
            top_pos = corr_result.get("details", {}).get("top_positive", {})
            top_neg = corr_result.get("details", {}).get("top_negative", {})
            # Комбинируем и берем топ
            all_corr = {**top_pos, **top_neg}
            sorted_corr = sorted(all_corr.items(), key=lambda item: abs(item[1]), reverse=True)
            top_corr_features = [feat for feat, _ in sorted_corr[:top_k]]
            
            for feature in top_corr_features:
                if feature in df.columns and feature != target_column:
                    scat_path = _plot_scatter(df, feature, target_column, output_dir, prefix=f"corr_")
                    bp_path = _plot_boxplot(df, feature, target_column, output_dir, prefix=f"corr_")
                    if scat_path or bp_path:
                        saved_plots[f"corr_{feature}"] = {
                            "scatter": scat_path,
                            "boxplot": bp_path,
                            "description": f"Визуализация для {feature} из CorrelationAnalysis"
                        }
                        plot_count += 1

        # 3. Визуализация результатов CategoricalFeatureAnalysis
        cat_results = [r for r in analysis_results if r["tool_name"] == "CategoricalFeatureAnalysis" and r["status"] == "success"]
        if cat_results:
            cat_result = cat_results[0]
            significant_features = cat_result.get("details", {}).get("significant_features", {})
            # Сортируем по p-value и берем топ
            sorted_cat = sorted(significant_features.items(), key=lambda item: item[1].get('p_value', 1.0))
            top_cat_features = [feat for feat, _ in sorted_cat[:top_k]]
            
            for feature in top_cat_features:
                if feature in df.columns and feature != target_column:
                    sb_path = _plot_stacked_bar(df, feature, target_column, output_dir, prefix=f"cat_")
                    if sb_path:
                        saved_plots[f"cat_{feature}"] = {
                            "stacked_bar": sb_path,
                            "description": f"Визуализация для {feature} из CategoricalFeatureAnalysis"
                        }
                        plot_count += 1

        # 4. Визуализация результатов OutlierDetector
        out_results = [r for r in analysis_results if r["tool_name"] == "OutlierDetector" and r["status"] == "success"]
        if out_results:
            out_result = out_results[0]
            outliers_info = out_result.get("details", {}).get("outliers", {})
            if outliers_info:
                out_plot_path = _plot_outlier_summary(outliers_info, output_dir, prefix=f"out_")
                if out_plot_path:
                    saved_plots["outlier_summary"] = {
                        "summary_plot": out_plot_path,
                        "description": "Сводный график количества выбросов по признакам"
                    }
                    plot_count += 1

        # 5. Визуализация результатов FullModelFeatureImportance
        imp_results = [r for r in analysis_results if r["tool_name"] == "FullModelFeatureImportance" and r["status"] == "success"]
        if imp_results:
            imp_result = imp_results[0]
            importances = imp_result.get("details", {}).get("feature_importances", {})
            if importances:
                imp_plot_path = _plot_feature_importance(importances, output_dir, prefix=f"imp_")
                if imp_plot_path:
                    saved_plots["feature_importance"] = {
                        "importance_plot": imp_plot_path,
                        "description": "График важности признаков из RandomForest"
                    }
                    plot_count += 1

        # 6. Визуализация главного признака из PrimaryFeatureFinder
        pf_results = [r for r in analysis_results if r["tool_name"] == "PrimaryFeatureFinder" and r["status"] == "success"]
        if pf_results:
            pf_result = pf_results[0]
            best_feature = pf_result.get("details", {}).get("best_feature")
            if best_feature and best_feature in df.columns and best_feature != target_column:
                bp_path = _plot_boxplot(df, best_feature, target_column, output_dir, prefix=f"pf_")
                hist_path = _plot_histograms(df, best_feature, target_column, output_dir, prefix=f"pf_")
                if bp_path or hist_path:
                    saved_plots[f"pf_{best_feature}"] = {
                        "boxplot": bp_path,
                        "histogram": hist_path,
                        "description": f"Визуализация главного признака: {best_feature}"
                    }
                    plot_count += 1

        if plot_count == 0:
            summary = "Не удалось создать визуализации на основе результатов анализа"
        else:
            summary = f"Создано {plot_count} информативных графиков на основе результатов предыдущих анализов"

        return {
            "tool_name": tool_name,
            "status": "success",
            "summary": summary,
            "details": {
                "saved_plots": saved_plots,
                "total_plots": plot_count
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
