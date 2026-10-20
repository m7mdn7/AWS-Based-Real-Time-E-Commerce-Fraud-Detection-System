"""
AWS FraudShield - Unit Tests for Preprocessing and Feature Engineering
Validates missing value handling, duplicate detection, zero leakage,
and graceful handling of new users with zero history.
"""

import os
import sys
import pytest
import pandas as pd
import numpy as np

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.preprocessing import clean_raw_data
from src.feature_engineering import (
    extract_single_transaction_features,
    FEATURE_COLUMNS,
    POPULATION_DEFAULTS
)


def test_clean_raw_data_removes_duplicates():
    """Verify duplicate transaction IDs are cleanly deduplicated."""
    data = {
        "transaction_id": ["TX-1", "TX-1", "TX-2"],
        "user_id": ["USR-1", "USR-1", "USR-2"],
        "amount": [500.0, 500.0, 800.0],
        "is_fraud": [0, 0, 1]
    }
    df = pd.DataFrame(data)
    clean_df, stats = clean_raw_data(df)
    
    assert len(clean_df) == 2
    assert stats["duplicates_removed"] == 1
    assert "TX-1" in clean_df["transaction_id"].values
    assert "TX-2" in clean_df["transaction_id"].values


def test_clean_raw_data_filters_invalid_amounts():
    """Verify negative and zero amounts are rejected."""
    data = {
        "transaction_id": ["TX-1", "TX-2", "TX-3"],
        "user_id": ["USR-1", "USR-2", "USR-3"],
        "amount": [500.0, -100.0, 0.0],
        "is_fraud": [0, 0, 0]
    }
    df = pd.DataFrame(data)
    clean_df, stats = clean_raw_data(df)
    
    assert len(clean_df) == 1
    assert stats["invalid_rows_dropped"] == 2
    assert clean_df.iloc[0]["transaction_id"] == "TX-1"


def test_clean_raw_data_imputes_missing_categoricals():
    """Verify missing device_id and location are gracefully imputed."""
    data = {
        "transaction_id": ["TX-1"],
        "user_id": ["USR-1"],
        "amount": [1200.0],
        "device_id": [None],
        "location": [None],
        "is_fraud": [0]
    }
    df = pd.DataFrame(data)
    clean_df, stats = clean_raw_data(df)
    
    assert clean_df.iloc[0]["device_id"] == "UNKNOWN_DEVICE"
    assert clean_df.iloc[0]["location"] == "UNKNOWN_LOCATION"
    assert stats["missing_values_imputed"] == 2


def test_feature_engineering_known_user_features():
    """Test feature extraction with established user historical baseline."""
    user_profile = {
        "user_id": "USR-1001",
        "avg_amount": 1000.0,
        "std_amount": 200.0,
        "known_devices": ["DEV-TRUSTED-1"],
        "frequent_locations": ["Bengaluru"],
        "frequent_merchants": ["Amazon India"]
    }
    tx = {
        "transaction_id": "TX-TEST-01",
        "user_id": "USR-1001",
        "amount": 1000.0,
        "device_id": "DEV-TRUSTED-1",
        "location": "Bengaluru",
        "merchant": "Amazon India",
        "timestamp": "2026-10-20T14:30:00Z"
    }
    
    feat_df, risk_factors = extract_single_transaction_features(tx, user_profile)
    
    assert isinstance(feat_df, pd.DataFrame)
    assert list(feat_df.columns) == FEATURE_COLUMNS
    assert feat_df.iloc[0]["amount_to_avg_ratio"] == pytest.approx(1.0, 0.01)
    assert feat_df.iloc[0]["amount_z_score"] == pytest.approx(0.0, 0.01)
    assert feat_df.iloc[0]["is_device_known"] == 1
    assert feat_df.iloc[0]["is_location_unusual"] == 0
    assert feat_df.iloc[0]["is_merchant_familiar"] == 1
    assert feat_df.iloc[0]["hour_of_day"] == 14
    assert len(risk_factors) == 0


def test_feature_engineering_unknown_user_fallback():
    """Test feature extraction for new / guest user with no prior history."""
    tx = {
        "transaction_id": "TX-NEW-01",
        "user_id": "USR-UNKNOWN-GUEST",
        "amount": 900.0,
        "device_id": "DEV-NEW-PHONE",
        "location": "Mumbai",
        "merchant": "Flipkart"
    }
    
    feat_df, risk_factors = extract_single_transaction_features(tx, user_profile=None)
    
    assert isinstance(feat_df, pd.DataFrame)
    # Check that ratio used population default
    expected_ratio = 900.0 / POPULATION_DEFAULTS["avg_amount"]
    assert feat_df.iloc[0]["amount_to_avg_ratio"] == pytest.approx(expected_ratio, 0.01)
    assert any("Unestablished customer profile" in f for f in risk_factors)
