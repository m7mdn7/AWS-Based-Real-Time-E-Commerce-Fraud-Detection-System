"""
AWS FraudShield - Model Evaluation & Reporting Tool
Loads the serialized best model pipeline and prints deep performance metrics,
confusion matrix analysis, and explainability trade-offs.
"""

import json
import os
import sys
from typing import Any, Dict

import joblib
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.preprocessing import prepare_datasets


def evaluate_saved_model(
    model_path: str = "models/fraud_detector_pipeline.joblib",
    data_path: str = "data/fraud_transactions.csv",
    profiles_path: str = "models/user_profiles.json",
    random_state: int = 42
) -> Dict[str, Any]:
    """
    Evaluates the saved pipeline on test data and returns metrics.
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}. Run src/train.py first.")
        
    pipeline = joblib.load(model_path)
    _, X_test, _, y_test, _ = prepare_datasets(
        data_path=data_path,
        profiles_path=profiles_path,
        random_state=random_state
    )
    
    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1] if hasattr(pipeline, "predict_proba") else y_pred
    
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    roc_auc = roc_auc_score(y_test, y_prob)
    pr_auc = average_precision_score(y_test, y_prob)
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()
    
    report_text = classification_report(y_test, y_pred, target_names=["Legitimate", "Fraud"])
    
    print("=" * 70)
    print("AWS FraudShield — Model Evaluation Summary")
    print("=" * 70)
    print(f"Model Artifact: {model_path}")
    print(f"Test Set Size : {len(y_test)} transactions")
    print(f"Fraud Instances: {int(y_test.sum())} ({y_test.mean()*100:.2f}%)")
    print("-" * 70)
    print(f"Precision (Fraud): {prec:.4f}  (Low False Positive rate is critical for CX)")
    print(f"Recall (Fraud)   : {rec:.4f}  (Catches {rec*100:.1f}% of all simulated attacks)")
    print(f"F1-Score         : {f1:.4f}")
    print(f"ROC-AUC          : {roc_auc:.4f}")
    print(f"PR-AUC           : {pr_auc:.4f}")
    print("-" * 70)
    print("Confusion Matrix:")
    print(f"  True Negatives  (Legitimate approved)    : {tn}")
    print(f"  False Positives (Legitimate flagged)     : {fp} (Customer friction)")
    print(f"  False Negatives (Fraud missed)           : {fn} (Financial loss)")
    print(f"  True Positives  (Fraud caught)           : {tp}")
    print("-" * 70)
    print("Full Classification Report:")
    print(report_text)
    print("=" * 70)
    print("Note: In e-commerce fraud prevention, raw accuracy is deceiving because 95%+")
    print("of traffic is legitimate. Focus on Precision, Recall, and PR-AUC.")
    print("=" * 70)
    
    return {
        "precision": float(prec),
        "recall": float(rec),
        "f1": float(f1),
        "roc_auc": float(roc_auc),
        "pr_auc": float(pr_auc),
        "confusion_matrix": {
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "tp": int(tp)
        }
    }


if __name__ == "__main__":
    evaluate_saved_model()
