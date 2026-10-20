"""
AWS FraudShield - Local Development REST API Server
Provides high-performance FastAPI endpoints mirroring AWS API Gateway & Lambda.
Fully runnable locally without AWS credentials.
"""

import os
import sys
from typing import Any, Dict, List, Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.config import settings
from backend.service import FraudDetectionService

app = FastAPI(
    title="AWS FraudShield API",
    description="Real-Time E-Commerce Fraud Risk Scoring Engine",
    version="1.0.0"
)

# Configure CORS
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

service = FraudDetectionService()


# Request / Response Models
class TransactionAnalyzeRequest(BaseModel):
    transaction_id: str = Field(..., json_schema_extra={"example": "TX-DEMO-001"})
    user_id: str = Field(..., json_schema_extra={"example": "USR-1001"})
    amount: float = Field(..., gt=0, json_schema_extra={"example": 1250.0})
    merchant: Optional[str] = Field(default="Amazon India", json_schema_extra={"example": "Amazon India"})
    merchant_category: Optional[str] = Field(default="electronics", json_schema_extra={"example": "electronics"})
    location: Optional[str] = Field(default="Bengaluru", json_schema_extra={"example": "Bengaluru"})
    device_id: Optional[str] = Field(default="DEV-ANDR-1001", json_schema_extra={"example": "DEV-ANDR-1001"})
    ip_address: Optional[str] = Field(default="103.21.244.1", json_schema_extra={"example": "103.21.244.1"})
    timestamp: Optional[str] = Field(default=None, json_schema_extra={"example": "2026-10-20T12:00:00Z"})


class ReviewAlertRequest(BaseModel):
    review_status: str = Field(..., json_schema_extra={"example": "CONFIRMED_FRAUD"})
    notes: Optional[str] = Field(default="", json_schema_extra={"example": "Confirmed with cardholder via phone."})


# Endpoints
@app.get("/health", tags=["System"])
def health_check():
    """Health check endpoint for container orchestrators and load balancers."""
    return {
        "status": "healthy",
        "service": "AWS FraudShield API",
        "environment": settings.ENVIRONMENT,
        "storage_backend": settings.STORAGE_BACKEND,
        "inference_engine": settings.INFERENCE_ENGINE
    }


@app.post("/transactions/analyze", tags=["Transactions"], status_code=status.HTTP_200_OK)
def analyze_transaction(req: TransactionAnalyzeRequest):
    """
    Analyzes an e-commerce transaction against historical user behavioral baselines
    and returns a machine-learning risk assessment.
    """
    try:
        result = service.analyze_transaction(req.model_dump())
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transaction analysis encountered an unexpected internal error."
        )


@app.get("/transactions", tags=["Transactions"])
def list_transactions(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    risk_level: Optional[str] = Query(None, description="Filter by LOW, MEDIUM, HIGH, or ALL")
):
    """Retrieves paginated transaction records."""
    records, total = service.list_transactions(limit=limit, offset=offset, risk_level=risk_level)
    return {
        "items": records,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@app.get("/transactions/{transaction_id}", tags=["Transactions"])
def get_transaction(transaction_id: str):
    """Retrieves a single analyzed transaction by its identifier."""
    tx = service.get_transaction(transaction_id)
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Transaction '{transaction_id}' not found.")
    return tx


@app.get("/alerts", tags=["Alerts"])
def list_alerts(limit: int = Query(50, ge=1, le=200)):
    """Retrieves high and medium-risk flagged transactions requiring operational review."""
    alerts = service.list_alerts(limit=limit)
    return {
        "alerts": alerts,
        "count": len(alerts)
    }


@app.post("/alerts/{transaction_id}/review", tags=["Alerts"])
def review_alert(transaction_id: str, req: ReviewAlertRequest):
    """Updates the security analyst review status of a flagged transaction."""
    updated = service.update_alert(transaction_id, req.review_status, req.notes or "")
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Transaction '{transaction_id}' not found.")
    return updated


@app.get("/stats", tags=["Dashboard"])
def get_dashboard_statistics():
    """Returns aggregated transaction metrics for dashboard display."""
    return service.get_dashboard_stats()


@app.get("/scenarios", tags=["Demonstration"])
def get_demo_scenarios():
    """Returns curated simulation scenarios to test various risk vectors."""
    return [
        {
            "id": "scenario_normal",
            "name": "1. Routine Grocery Purchase",
            "description": "₹750 purchase on user's known smartphone from their home city (Bengaluru).",
            "payload": {
                "transaction_id": "TX-SCENARIO-NORM",
                "user_id": "USR-1001",
                "amount": 750.0,
                "merchant": "Swiggy Instamart",
                "merchant_category": "groceries",
                "location": "Bengaluru",
                "device_id": "DEV-ANDR-1001",
                "ip_address": "103.21.244.1"
            }
        },
        {
            "id": "scenario_legit_high",
            "name": "2. Legitimate High-Value Electronics",
            "description": "₹45,000 laptop purchase on user's primary known device from their home location.",
            "payload": {
                "transaction_id": "TX-SCENARIO-LEGIT-HIGH",
                "user_id": "USR-1001",
                "amount": 45000.0,
                "merchant": "Apple Store India",
                "merchant_category": "electronics",
                "location": "Bengaluru",
                "device_id": "DEV-ANDR-1001",
                "ip_address": "103.21.244.1"
            }
        },
        {
            "id": "scenario_ato",
            "name": "3. Account Takeover (ATO Attack)",
            "description": "Attacker attempts ₹10,000 transaction on an unseen device from an unusual remote location.",
            "payload": {
                "transaction_id": "TX-SCENARIO-ATO",
                "user_id": "USR-1001",
                "amount": 10000.0,
                "merchant": "Crypto Voucher Hub",
                "merchant_category": "digital_goods",
                "location": "Lagos, Nigeria",
                "device_id": "DEV-ATTACK-9999",
                "ip_address": "185.220.101.5"
            }
        },
        {
            "id": "scenario_travel",
            "name": "4. Legitimate Travel Dining",
            "description": "₹1,800 dinner purchase in Goa using the user's familiar mobile device.",
            "payload": {
                "transaction_id": "TX-SCENARIO-TRAVEL",
                "user_id": "USR-1001",
                "amount": 1800.0,
                "merchant": "MakeMyTrip",
                "merchant_category": "travel",
                "location": "Goa",
                "device_id": "DEV-ANDR-1001",
                "ip_address": "103.28.12.8"
            }
        },
        {
            "id": "scenario_card_testing",
            "name": "5. Rapid Card-Testing Micro-Spend",
            "description": "₹49 digital token attempt on an unrecognized device fingerprint.",
            "payload": {
                "transaction_id": "TX-SCENARIO-MICRO",
                "user_id": "USR-1002",
                "amount": 49.0,
                "merchant": "Google Play Store",
                "merchant_category": "digital_goods",
                "location": "Bucharest, Romania",
                "device_id": "DEV-BOT-4444",
                "ip_address": "185.190.22.4"
            }
        }
    ]


if __name__ == "__main__":
    import uvicorn
    print(f"Starting AWS FraudShield API server on {settings.HOST}:{settings.PORT}...")
    uvicorn.run("backend.server:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
