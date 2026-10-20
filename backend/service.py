"""
AWS FraudShield - Core Fraud Analysis Service
Coordinates input validation, historical profiling, feature extraction,
probabilistic model scoring, and actionable decision routing.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backend.config import settings
from backend.inference import InferenceEngine, get_inference_engine
from backend.storage import StorageAdapter, get_storage_adapter
from src.feature_engineering import extract_single_transaction_features


class FraudDetectionService:
    """Core domain service for fraud assessment and transaction management."""
    
    def __init__(
        self,
        storage: Optional[StorageAdapter] = None,
        inference: Optional[InferenceEngine] = None
    ):
        self.storage = storage or get_storage_adapter()
        self.inference = inference or get_inference_engine()

    def validate_transaction_payload(self, tx: dict) -> None:
        """Validates required transaction fields and value constraints."""
        if not isinstance(tx, dict):
            raise ValueError("Payload must be a valid JSON object.")
            
        required_fields = ["transaction_id", "user_id", "amount"]
        for field in required_fields:
            if field not in tx or tx[field] is None:
                raise ValueError(f"Missing required transaction field: '{field}'")
                
        try:
            amt = float(tx["amount"])
            if amt <= 0:
                raise ValueError("Transaction amount must be strictly greater than 0.")
        except (ValueError, TypeError):
            raise ValueError("Field 'amount' must be a positive numeric value.")

    def analyze_transaction(self, tx: dict) -> Dict[str, Any]:
        """
        Executes end-to-end fraud risk analysis pipeline:
        1. Validate request
        2. Idempotency check
        3. Fetch user history
        4. Extract features
        5. Invoke model inference
        6. Compute calibrated decision bands
        7. Persist transaction
        8. Return standard response
        """
        self.validate_transaction_payload(tx)
        tx_id = str(tx["transaction_id"]).strip()
        user_id = str(tx["user_id"]).strip()
        
        # Idempotency check: prevent duplicate billing or scoring
        existing = self.storage.get_transaction(tx_id)
        if existing:
            return existing

        # Retrieve user historical profile
        user_profile = self.storage.get_user_profile(user_id)
        
        # Extract features and rule-based explanations
        features_df, risk_factors = extract_single_transaction_features(tx, user_profile)
        
        # Run inference engine
        risk_score, engine_info = self.inference.predict_risk(features_df)
        
        # Calibrated decision bands (configurable)
        low_thresh = settings.RISK_THRESHOLD_LOW
        high_thresh = settings.RISK_THRESHOLD_HIGH
        
        if risk_score < low_thresh:
            risk_level = "LOW"
            prediction = "LEGITIMATE"
            recommended_action = "APPROVE"
        elif risk_score < high_thresh:
            risk_level = "MEDIUM"
            prediction = "SUSPICIOUS"
            recommended_action = "VERIFY_MFA"
        else:
            risk_level = "HIGH"
            prediction = "SUSPICIOUS"
            recommended_action = "FLAG_FOR_REVIEW"
            
        now_iso = tx.get("timestamp") or datetime.now(timezone.utc).isoformat()
        
        result_record = {
            "transaction_id": tx_id,
            "user_id": user_id,
            "amount": float(tx["amount"]),
            "merchant": tx.get("merchant", "General Merchant"),
            "merchant_category": tx.get("merchant_category", "general"),
            "location": tx.get("location", "Unknown Location"),
            "device_id": tx.get("device_id", "UNKNOWN_DEV"),
            "ip_address": tx.get("ip_address", "127.0.0.1"),
            "timestamp": now_iso,
            "risk_score": float(risk_score),
            "risk_level": risk_level,
            "prediction": prediction,
            "recommended_action": recommended_action,
            "risk_factors": risk_factors,
            "engine_info": engine_info,
            "review_status": "FLAGGED_FOR_REVIEW" if risk_level == "HIGH" else "AUTOMATICALLY_CLEARED"
        }
        
        # Save record
        self.storage.save_transaction(result_record)
        return result_record

    def get_transaction(self, tx_id: str) -> Optional[dict]:
        return self.storage.get_transaction(tx_id)

    def list_transactions(self, limit: int = 20, offset: int = 0, risk_level: Optional[str] = None):
        return self.storage.list_transactions(limit=limit, offset=offset, risk_level=risk_level)

    def list_alerts(self, limit: int = 50):
        return self.storage.list_alerts(limit=limit)

    def update_alert(self, tx_id: str, review_status: str, notes: str = ""):
        return self.storage.update_alert_status(tx_id, review_status, notes)

    def get_dashboard_stats(self):
        return self.storage.get_dashboard_stats()
