"""
AWS FraudShield - Serverless AWS Lambda Handler
Processes API Gateway HTTP proxy events for real-time transaction scoring,
historical querying, and fraud alert reviews.
"""

import json
import os
import sys
from typing import Any, Dict

# Ensure src and backend modules can be imported inside Lambda runtime
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from backend.service import FraudDetectionService

# Reusable service instance across warm Lambda invocations
service = FraudDetectionService()

CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT",
    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token"
}


def build_response(status_code: int, body_dict: Any) -> Dict[str, Any]:
    """Formats standard API Gateway HTTP proxy response."""
    return {
        "statusCode": status_code,
        "headers": CORS_HEADERS,
        "body": json.dumps(body_dict, default=str)
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main entry point for AWS Lambda invoked by Amazon API Gateway.
    """
    http_method = event.get("httpMethod") or event.get("requestContext", {}).get("http", {}).get("method", "GET")
    path = event.get("path") or event.get("rawPath", "/")
    
    # Handle CORS Preflight
    if http_method.upper() == "OPTIONS":
        return build_response(200, {"message": "CORS preflight successful"})
        
    try:
        # Route: GET /health
        if path.rstrip("/") == "/health" and http_method.upper() == "GET":
            return build_response(200, {
                "status": "healthy",
                "service": "AWS FraudShield Lambda",
                "region": os.getenv("AWS_REGION", "us-east-1")
            })

        # Route: POST /transactions/analyze
        if "/transactions/analyze" in path and http_method.upper() == "POST":
            raw_body = event.get("body", "{}")
            if isinstance(raw_body, str):
                body = json.loads(raw_body) if raw_body else {}
            else:
                body = raw_body
                
            result = service.analyze_transaction(body)
            return build_response(200, result)

        # Route: GET /transactions/{id}
        if "/transactions/" in path and http_method.upper() == "GET" and not path.endswith("/transactions"):
            tx_id = path.rstrip("/").split("/")[-1]
            tx = service.get_transaction(tx_id)
            if not tx:
                return build_response(404, {"error": f"Transaction '{tx_id}' not found."})
            return build_response(200, tx)

        # Route: GET /transactions
        if path.rstrip("/").endswith("/transactions") and http_method.upper() == "GET":
            params = event.get("queryStringParameters") or {}
            limit = int(params.get("limit", 20))
            offset = int(params.get("offset", 0))
            risk_level = params.get("risk_level")
            records, total = service.list_transactions(limit=limit, offset=offset, risk_level=risk_level)
            return build_response(200, {
                "items": records,
                "total": total,
                "limit": limit,
                "offset": offset
            })

        # Route: GET /alerts
        if "/alerts" in path and http_method.upper() == "GET":
            params = event.get("queryStringParameters") or {}
            limit = int(params.get("limit", 50))
            alerts = service.list_alerts(limit=limit)
            return build_response(200, {"alerts": alerts, "count": len(alerts)})

        # Route: GET /stats
        if "/stats" in path and http_method.upper() == "GET":
            stats = service.get_dashboard_stats()
            return build_response(200, stats)

        # Unknown Route
        return build_response(404, {"error": f"Endpoint '{http_method} {path}' not found."})

    except ValueError as e:
        return build_response(400, {"error": str(e)})
    except Exception as e:
        print(f"[Error in lambda_handler] {str(e)}")
        return build_response(500, {"error": "Internal serverless execution error."})
