"""
AWS FraudShield - Prediction and Decision Logic Unit Tests
Tests risk scoring, calibrated decision bands, ATO attack handling,
legitimate high-value transactions, and model failure resilience.
"""

import os
import sys
import pytest

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.inference import LocalInferenceEngine
from backend.service import FraudDetectionService
from backend.storage import MemoryStorageAdapter


@pytest.fixture
def test_service():
    """Provides an isolated in-memory service instance with seeded test profile."""
    storage = MemoryStorageAdapter()
    storage.user_profiles["USR-1001"] = {
        "user_id": "USR-1001",
        "avg_amount": 750.0,
        "std_amount": 150.0,
        "known_devices": ["DEV-ANDR-TRUSTED"],
        "frequent_locations": ["Bengaluru"],
        "frequent_merchants": ["Swiggy Instamart", "Amazon India"]
    }
    inference = LocalInferenceEngine()
    return FraudDetectionService(storage=storage, inference=inference)


def test_normal_transaction_prediction(test_service):
    """Test standard everyday purchase: should have valid score and APPROVE recommendation."""
    tx = {
        "transaction_id": "TX-NORM-001",
        "user_id": "USR-1001",
        "amount": 720.0,
        "device_id": "DEV-ANDR-TRUSTED",
        "location": "Bengaluru",
        "merchant": "Swiggy Instamart"
    }
    result = test_service.analyze_transaction(tx)
    
    assert "risk_score" in result
    assert 0.0 <= result["risk_score"] <= 1.0
    assert result["risk_level"] in ("LOW", "MEDIUM", "HIGH")
    assert result["recommended_action"] in ("APPROVE", "VERIFY_MFA", "FLAG_FOR_REVIEW")
    assert result["transaction_id"] == "TX-NORM-001"
    assert result["risk_level"] == "LOW"
    assert result["recommended_action"] == "APPROVE"


def test_account_takeover_attack_detection(test_service):
    """Test suspicious transaction: 15x amount spike, foreign location, unknown device."""
    tx = {
        "transaction_id": "TX-ATO-001",
        "user_id": "USR-1001",
        "amount": 12500.0,  # ~16x higher than average
        "device_id": "DEV-ATTACKER-UNKNOWN",
        "location": "Lagos, Nigeria",
        "merchant": "Crypto Voucher Hub"
    }
    result = test_service.analyze_transaction(tx)
    
    assert result["risk_score"] >= 0.70
    assert result["risk_level"] == "HIGH"
    assert result["recommended_action"] == "FLAG_FOR_REVIEW"
    assert len(result["risk_factors"]) >= 2
    # Verify risk factors contain explainable signals
    factors_str = " ".join(result["risk_factors"])
    assert "unseen device" in factors_str.lower()
    assert "location" in factors_str.lower()


def test_legitimate_high_value_transaction(test_service):
    """
    Test legitimate high-value transaction (laptop purchase):
    High value alone must NOT be treated as guaranteed fraud when
    initiated on user's known device and home location.
    """
    tx = {
        "transaction_id": "TX-LAPTOP-001",
        "user_id": "USR-1001",
        "amount": 25000.0,  # Expensive purchase
        "device_id": "DEV-ANDR-TRUSTED",  # Familiar device!
        "location": "Bengaluru",          # Familiar location!
        "merchant": "Apple Store India"
    }
    result = test_service.analyze_transaction(tx)
    
    assert 0.0 <= result["risk_score"] <= 1.0
    assert "risk_factors" in result
    # It might have elevated amount ratio, but device is recognized
    factors_str = " ".join(result["risk_factors"])
    assert "unseen device" not in factors_str.lower()


def test_idempotency_prevents_duplicate_processing(test_service):
    """Test that submitting the same transaction ID twice returns the existing record."""
    tx = {
        "transaction_id": "TX-IDEMP-001",
        "user_id": "USR-1001",
        "amount": 500.0,
        "device_id": "DEV-ANDR-TRUSTED",
        "location": "Bengaluru"
    }
    first_res = test_service.analyze_transaction(tx)
    second_res = test_service.analyze_transaction(tx)
    
    assert first_res["transaction_id"] == second_res["transaction_id"]
    assert first_res["risk_score"] == second_res["risk_score"]


def test_validation_rejects_missing_and_negative_amounts(test_service):
    """Test API input validation fails on missing fields and invalid amounts."""
    with pytest.raises(ValueError, match="positive numeric value|greater than 0"):
        test_service.analyze_transaction({
            "transaction_id": "TX-NEG-001",
            "user_id": "USR-1001",
            "amount": -50.0
        })

    with pytest.raises(ValueError, match="Missing required transaction field: 'user_id'"):
        test_service.analyze_transaction({
            "transaction_id": "TX-NOUSER-001",
            "amount": 500.0
        })


def test_inference_engine_fallback_resilience():
    """Test that LocalInferenceEngine falls back to heuristic rules if model file missing."""
    engine = LocalInferenceEngine(model_path="non_existent_model_dir/missing.joblib")
    storage = MemoryStorageAdapter()
    service = FraudDetectionService(storage=storage, inference=engine)
    
    tx = {
        "transaction_id": "TX-FALLBACK-001",
        "user_id": "USR-NEW",
        "amount": 900.0
    }
    result = service.analyze_transaction(tx)
    
    assert "risk_score" in result
    assert 0.0 <= result["risk_score"] <= 1.0
    assert result["engine_info"] == "fallback_heuristic_engine"
