"""
AWS FraudShield - Model Training & Model Selection Pipeline
Trains and compares Logistic Regression, Random Forest, and XGBoost.
Evaluates on imbalanced test data and saves the best model pipeline with real metrics.
"""

import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.preprocessing import prepare_datasets


def evaluate_model_pipeline(
    pipeline: Any,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    model_name: str
) -> Dict[str, Any]:
    """
    Computes rigorous evaluation metrics on holdout test data.
    Does not rely on accuracy alone due to extreme class imbalance.
    """
    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1] if hasattr(pipeline, "predict_proba") else y_pred
    
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    roc_auc = roc_auc_score(y_test, y_prob)
    pr_auc = average_precision_score(y_test, y_prob)
    cm = confusion_matrix(y_test, y_pred).tolist()
    
    # Classification report dict
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    
    return {
        "model_name": model_name,
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "f1_score": round(float(f1), 4),
        "roc_auc": round(float(roc_auc), 4),
        "pr_auc": round(float(pr_auc), 4),
        "confusion_matrix": cm,
        "classification_report": report
    }


def train_and_select_model(
    data_path: str = "data/fraud_transactions.csv",
    profiles_path: str = "models/user_profiles.json",
    output_model_path: str = "models/fraud_detector_pipeline.joblib",
    output_metrics_path: str = "models/metrics.json",
    random_state: int = 42
) -> Dict[str, Any]:
    """
    Trains candidate models, records actual metrics, and serializes the best performer.
    """
    print("=" * 70)
    print("AWS FraudShield — Model Training & Selection Pipeline")
    print("=" * 70)
    
    X_train, X_test, y_train, y_test, split_meta = prepare_datasets(
        data_path=data_path,
        profiles_path=profiles_path,
        random_state=random_state
    )
    
    neg_count = int((y_train == 0).sum())
    pos_count = int((y_train == 1).sum())
    scale_pos_weight = float(neg_count / max(pos_count, 1))
    
    print(f"Dataset split: {len(X_train)} train samples, {len(X_test)} test samples.")
    print(f"Training Class distribution: {neg_count} legitimate, {pos_count} fraud (weight: {scale_pos_weight:.2f})")
    
    candidate_pipelines = {}
    
    # 1. Logistic Regression Baseline (Scaled & Balanced)
    candidate_pipelines["Logistic Regression"] = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=random_state))
    ])
    
    # 2. Random Forest (Class weight balanced)
    candidate_pipelines["Random Forest"] = Pipeline([
        ("classifier", RandomForestClassifier(
            n_estimators=120,
            max_depth=10,
            class_weight="balanced",
            min_samples_split=4,
            random_state=random_state,
            n_jobs=-1
        ))
    ])
    
    # 3. XGBoost (or Gradient Boosting fallback)
    try:
        from xgboost import XGBClassifier
        print("XGBoost library detected. Including XGBClassifier in comparison.")
        candidate_pipelines["XGBoost"] = Pipeline([
            ("classifier", XGBClassifier(
                n_estimators=120,
                max_depth=5,
                learning_rate=0.08,
                scale_pos_weight=scale_pos_weight,
                random_state=random_state,
                eval_metric="logloss"
            ))
        ])
    except ImportError:
        from sklearn.ensemble import HistGradientBoostingClassifier
        print("XGBoost not installed; utilizing HistGradientBoostingClassifier as boosting model.")
        candidate_pipelines["HistGradientBoosting"] = Pipeline([
            ("classifier", HistGradientBoostingClassifier(
                max_iter=120,
                class_weight="balanced",
                random_state=random_state
            ))
        ])
        
    model_metrics = {}
    best_model_name = None
    best_f1 = -1.0
    
    for name, pipe in candidate_pipelines.items():
        print(f"\nTraining {name}...")
        pipe.fit(X_train, y_train)
        metrics = evaluate_model_pipeline(pipe, X_test, y_test, name)
        model_metrics[name] = metrics
        
        print(f"  -> Precision: {metrics['precision']:.4f} | Recall: {metrics['recall']:.4f} | F1: {metrics['f1_score']:.4f} | ROC-AUC: {metrics['roc_auc']:.4f}")
        
        # Select best model based on F1-score on fraud class
        if metrics["f1_score"] > best_f1:
            best_f1 = metrics["f1_score"]
            best_model_name = name
            
    print("\n" + "=" * 70)
    print(f"Best Performing Model: {best_model_name} (F1-Score: {best_f1:.4f})")
    print("=" * 70)
    
    best_pipeline = candidate_pipelines[best_model_name]
    
    # Save best model pipeline
    os.makedirs(os.path.dirname(output_model_path), exist_ok=True)
    joblib.dump(best_pipeline, output_model_path)
    print(f"Serialized winning pipeline to: {output_model_path}")
    
    # Prepare comprehensive metrics artifact
    artifacts_meta = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "selected_model": best_model_name,
        "evaluation_summary": {
            "selected_f1": best_f1,
            "selected_precision": model_metrics[best_model_name]["precision"],
            "selected_recall": model_metrics[best_model_name]["recall"],
            "selected_roc_auc": model_metrics[best_model_name]["roc_auc"],
            "selected_pr_auc": model_metrics[best_model_name]["pr_auc"],
            "confusion_matrix": model_metrics[best_model_name]["confusion_matrix"]
        },
        "all_models": model_metrics,
        "dataset_split_metadata": split_meta
    }
    
    with open(output_metrics_path, "w", encoding="utf-8") as f:
        json.dump(artifacts_meta, f, indent=2)
        
    print(f"Saved real evaluation metrics to: {output_metrics_path}")
    return artifacts_meta


if __name__ == "__main__":
    train_and_select_model()
