# AWS FraudShield — Models Directory

This directory stores trained machine learning pipelines, baseline user profiles, and evaluation metric artifacts.

---

## 1. Directory Structure

```
models/
├── README.md
├── fraud_detector_pipeline.joblib   # Saved best model pipeline (RandomForest / GradientBoosting / XGBoost)
├── user_profiles.json               # Historical baseline user profiles used for behavioral feature extraction
└── metrics.json                     # Real evaluation metrics produced by train.py
```

---

## 2. Model Training & Selection

The pipeline (`src/train.py`) evaluates multiple candidate classifiers under identical stratified 80/20 train/test splits with a fixed random seed (`RANDOM_STATE = 42`):

1. **Logistic Regression** (with StandardScaler & class-weight balanced) — High interpretability linear baseline.
2. **Random Forest Classifier** — Non-linear tree ensemble robust against outliers and feature scale differences.
3. **Gradient Boosting / XGBoost** — Boosted decision trees optimizing loss on rare-event fraud detection.

The winning model is selected based on **PR-AUC and F1-Score on the fraud class**, rather than raw accuracy. Because fraud represents a rare fraction of total volume (typically 1-5%), high accuracy can be achieved trivially by predicting all negatives.

---

## 3. Risk Scoring & Decision Bands

Model probabilities represent the estimated risk $P(\text{Fraud} = 1 \mid X)$. This is categorized into actionable decision bands:

| Score Band | Risk Level | Recommended Action | Analyst Guidance |
|---|---|---|---|
| **0.00 – 0.29** | `LOW` | `APPROVE` | Transaction processed without user disruption. |
| **0.30 – 0.69** | `MEDIUM` | `VERIFY_MFA` | Trigger 2-Factor Authentication (SMS OTP, Push Notification, or biometric confirmation). |
| **0.70 – 1.00** | `HIGH` | `FLAG_FOR_REVIEW` | Hold transaction temporarily; alert anti-fraud operations team for manual verification. |

> **Important**: Model probability outputs are risk scores, not mathematical proof of malicious intent. Edge cases such as business travel or legitimate gifting can elevate risk scores without fraudulent intent.

---

## 4. How to Train or Re-evaluate

To re-train all models and save the best pipeline:

```bash
python src/train.py
```

To evaluate the saved pipeline on test data and print the confusion matrix:

```bash
python src/evaluate.py
```
