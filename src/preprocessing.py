"""
AWS FraudShield - Preprocessing Pipeline
Handles data cleaning, duplicate detection, missing-value imputation,
label validation, and stratified train/test partitioning.
"""

from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight

from src.feature_engineering import FEATURE_COLUMNS, build_batch_features, load_user_profiles


def clean_raw_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """
    Cleans raw transaction data:
    - Removes duplicate transactions based on transaction_id
    - Validates label column is binary (0 or 1)
    - Validates positive transaction amounts
    - Imputes missing categorical and numerical fields
    """
    stats = {
        "initial_rows": len(df),
        "duplicates_removed": 0,
        "missing_values_imputed": 0,
        "invalid_rows_dropped": 0
    }
    
    # 1. Duplicate detection
    duplicates = df.duplicated(subset=["transaction_id"], keep="first")
    stats["duplicates_removed"] = int(duplicates.sum())
    cleaned_df = df[~duplicates].copy()
    
    # 2. Label validation
    if "is_fraud" in cleaned_df.columns:
        valid_labels = cleaned_df["is_fraud"].isin([0, 1])
        stats["invalid_rows_dropped"] += int((~valid_labels).sum())
        cleaned_df = cleaned_df[valid_labels]
        cleaned_df["is_fraud"] = cleaned_df["is_fraud"].astype(int)
        
    # 3. Numeric validation
    if "amount" in cleaned_df.columns:
        valid_amount = cleaned_df["amount"] > 0
        stats["invalid_rows_dropped"] += int((~valid_amount).sum())
        cleaned_df = cleaned_df[valid_amount]
        
    # 4. Missing value imputation
    if "device_id" in cleaned_df.columns:
        null_devices = cleaned_df["device_id"].isnull()
        stats["missing_values_imputed"] += int(null_devices.sum())
        cleaned_df["device_id"] = cleaned_df["device_id"].fillna("UNKNOWN_DEVICE")
        
    if "location" in cleaned_df.columns:
        null_loc = cleaned_df["location"].isnull()
        stats["missing_values_imputed"] += int(null_loc.sum())
        cleaned_df["location"] = cleaned_df["location"].fillna("UNKNOWN_LOCATION")
        
    stats["final_clean_rows"] = len(cleaned_df)
    return cleaned_df, stats


def prepare_datasets(
    data_path: str = "data/fraud_transactions.csv",
    profiles_path: str = "models/user_profiles.json",
    test_size: float = 0.20,
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, dict]:
    """
    Loads raw CSV data, applies behavioral feature extraction,
    and performs a stratified train/test split.
    """
    raw_df = pd.read_csv(data_path)
    clean_df, clean_stats = clean_raw_data(raw_df)
    
    profiles = load_user_profiles(profiles_path)
    features_df = build_batch_features(clean_df, profiles)
    y = clean_df["is_fraud"].copy()
    
    # Stratified train/test split to preserve rare fraud class ratio
    X_train, X_test, y_train, y_test = train_test_split(
        features_df,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y
    )
    
    # Compute class weights to address severe class imbalance
    classes = np.unique(y_train)
    weights = compute_class_weight(class_weight="balanced", classes=classes, y=y_train)
    class_weight_dict = {int(c): float(w) for c, w in zip(classes, weights)}
    
    split_summary = {
        "cleaning_stats": clean_stats,
        "total_samples": len(features_df),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "train_fraud_rate": float(y_train.mean()),
        "test_fraud_rate": float(y_test.mean()),
        "class_weights": class_weight_dict,
        "feature_columns": FEATURE_COLUMNS
    }
    
    return X_train, X_test, y_train, y_test, split_summary
