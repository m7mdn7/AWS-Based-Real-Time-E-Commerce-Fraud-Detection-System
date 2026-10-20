"""
AWS FraudShield - REST API Integration Tests
Tests HTTP endpoints, query parameters, error codes, and responses.
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.server import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_check_endpoint(client):
    """GET /health should return 200 and healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data


def test_analyze_transaction_endpoint(client):
    """POST /transactions/analyze should validate and return scored transaction."""
    payload = {
        "transaction_id": "TX-API-TEST-001",
        "user_id": "USR-1001",
        "amount": 650.0,
        "merchant": "Amazon India",
        "merchant_category": "electronics",
        "location": "Bengaluru",
        "device_id": "DEV-ANDR-1001"
    }
    response = client.post("/transactions/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["transaction_id"] == "TX-API-TEST-001"
    assert "risk_score" in data
    assert "risk_level" in data
    assert "recommended_action" in data
    assert isinstance(data["risk_factors"], list)


def test_analyze_transaction_invalid_amount(client):
    """POST /transactions/analyze with non-positive amount should return 422 or 400."""
    payload = {
        "transaction_id": "TX-API-TEST-002",
        "user_id": "USR-1001",
        "amount": -100.0
    }
    response = client.post("/transactions/analyze", json=payload)
    assert response.status_code in (400, 422)


def test_list_transactions_endpoint(client):
    """GET /transactions should return list and count."""
    response = client.get("/transactions?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)


def test_get_transaction_by_id(client):
    """GET /transactions/{id} should return 200 for existing transaction."""
    # First create
    client.post("/transactions/analyze", json={
        "transaction_id": "TX-FETCH-001",
        "user_id": "USR-1001",
        "amount": 400.0
    })
    
    response = client.get("/transactions/TX-FETCH-001")
    assert response.status_code == 200
    assert response.json()["transaction_id"] == "TX-FETCH-001"


def test_get_transaction_not_found(client):
    """GET /transactions/{id} should return 404 for unknown transaction."""
    response = client.get("/transactions/TX-DOES-NOT-EXIST-999")
    assert response.status_code == 404


def test_get_alerts_endpoint(client):
    """GET /alerts should return alerts list."""
    response = client.get("/alerts")
    assert response.status_code == 200
    data = response.json()
    assert "alerts" in data


def test_get_stats_endpoint(client):
    """GET /stats should return dashboard counts."""
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_transactions" in data
    assert "high_risk_count" in data
