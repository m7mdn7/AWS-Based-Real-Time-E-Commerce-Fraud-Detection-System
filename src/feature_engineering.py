"""
AWS FraudShield - Feature Engineering Module
Transforms raw transaction inputs and historical customer baselines into
predictive feature vectors without future target leakage.
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

# Default population statistics for new / guest users with no prior transaction history
POPULATION_DEFAULTS = {
    "avg_amount": 850.0,
    "std_amount": 350.0,
    "known_devices": [],
    "frequent_locations": ["Bengaluru", "Mumbai", "Delhi NCR"],
    "frequent_merchants": ["Amazon India", "Flipkart"]
}

# The explicit feature column list used in model training and inference
FEATURE_COLUMNS = [
    "amount",
    "amount_to_avg_ratio",
    "amount_z_score",
    "is_device_known",
    "is_location_unusual",
    "is_merchant_familiar",
    "hour_of_day",
    "day_of_week",
    "is_weekend",
    "is_night_transaction",
    "is_amount_spike"
]


def load_user_profiles(profiles_path: str = "models/user_profiles.json") -> Dict[str, dict]:
    """Loads baseline customer profiles from disk."""
    if os.path.exists(profiles_path):
        with open(profiles_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def extract_single_transaction_features(
    tx: dict,
    user_profile: Optional[dict] = None,
    recent_transactions: Optional[List[dict]] = None
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Extracts behavioral features for a single real-time transaction request.
    Handles unknown users safely without crashing.
    Returns:
        features_df: Single-row DataFrame matching FEATURE_COLUMNS
        risk_factors: List of explainable rule-based risk factor strings
    """
    if user_profile is None or not user_profile:
        profile = POPULATION_DEFAULTS
        is_new_user = True
    else:
        profile = user_profile
        is_new_user = False
        
    amount = float(tx.get("amount", 0.0))
    avg_amt = float(profile.get("avg_amount", POPULATION_DEFAULTS["avg_amount"]))
    std_amt = float(profile.get("std_amount", POPULATION_DEFAULTS["std_amount"]))
    std_amt = max(std_amt, 50.0)  # Avoid division by zero
    
    # Behavioral ratios
    ratio = amount / max(avg_amt, 1.0)
    z_score = (amount - avg_amt) / std_amt
    
    # Device familiarity
    known_devices = set(profile.get("known_devices", []))
    device_id = str(tx.get("device_id", ""))
    is_device_known = 1 if (device_id in known_devices and len(known_devices) > 0) else 0
    
    # Location familiarity
    frequent_locations = [loc.lower() for loc in profile.get("frequent_locations", [])]
    tx_location = str(tx.get("location", "")).lower()
    is_location_familiar = any(fl in tx_location or tx_location in fl for fl in frequent_locations) if frequent_locations else False
    is_location_unusual = 0 if is_location_familiar else 1
    
    # Merchant familiarity
    frequent_merchants = [m.lower() for m in profile.get("frequent_merchants", [])]
    tx_merchant = str(tx.get("merchant", "")).lower()
    is_merchant_familiar = 1 if any(fm in tx_merchant or tx_merchant in fm for fm in frequent_merchants) else 0
    
    # Timestamp parsing
    raw_timestamp = tx.get("timestamp")
    if raw_timestamp:
        try:
            dt = datetime.fromisoformat(str(raw_timestamp).replace("Z", "+00:00"))
        except Exception:
            dt = datetime.now(timezone.utc)
    else:
        dt = datetime.now(timezone.utc)
        
    hour = dt.hour
    day_of_week = dt.weekday()
    is_weekend = 1 if day_of_week in [5, 6] else 0
    is_night_transaction = 1 if hour in [0, 1, 2, 3, 4, 5] else 0
    is_amount_spike = 1 if ratio >= 4.0 else 0
    
    # Risk factor rule explanations
    risk_factors = []
    if ratio >= 4.0:
        risk_factors.append(f"Transaction amount ₹{amount:,.2f} is {ratio:.1f}x higher than user average (₹{avg_amt:,.2f})")
    elif ratio >= 2.5:
        risk_factors.append(f"Elevated spend: {ratio:.1f}x typical transaction value")
        
    if not is_device_known:
        risk_factors.append("Transaction initiated from a previously unseen device")
        
    if is_location_unusual:
        risk_factors.append(f"Unusual or foreign geographic location: '{tx.get('location', 'Unknown')}'")
        
    if is_night_transaction:
        risk_factors.append(f"High-risk execution window (executed at {hour:02d}:00 hours)")
        
    if is_new_user:
        risk_factors.append("Unestablished customer profile (evaluated using population baseline)")

    row = {
        "amount": amount,
        "amount_to_avg_ratio": float(ratio),
        "amount_z_score": float(z_score),
        "is_device_known": int(is_device_known),
        "is_location_unusual": int(is_location_unusual),
        "is_merchant_familiar": int(is_merchant_familiar),
        "hour_of_day": int(hour),
        "day_of_week": int(day_of_week),
        "is_weekend": int(is_weekend),
        "is_night_transaction": int(is_night_transaction),
        "is_amount_spike": int(is_amount_spike)
    }
    
    features_df = pd.DataFrame([row])[FEATURE_COLUMNS]
    return features_df, risk_factors


def build_batch_features(
    df: pd.DataFrame,
    profiles: Dict[str, dict]
) -> pd.DataFrame:
    """
    Computes behavioral features for a batch DataFrame of historical transactions.
    Ensures zero target leakage.
    """
    feature_rows = []
    for _, row in df.iterrows():
        tx_dict = row.to_dict()
        user_id = tx_dict.get("user_id")
        user_profile = profiles.get(user_id, POPULATION_DEFAULTS)
        feat_df, _ = extract_single_transaction_features(tx_dict, user_profile)
        feature_rows.append(feat_df.iloc[0].to_dict())
        
    features_df = pd.DataFrame(feature_rows)[FEATURE_COLUMNS]
    return features_df
