"""
AWS FraudShield - Backend Configuration
Supports environment-based configuration for both local execution and AWS deployment.
"""

import os
from dataclasses import dataclass


@dataclass
class Settings:
    # Runtime environment: 'local' | 'aws'
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "local")
    
    # Server configuration
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1")
    
    # Configurable Risk Threshold Bands
    # LOW: score < RISK_THRESHOLD_LOW (Default: 0.30)
    # MEDIUM: RISK_THRESHOLD_LOW <= score < RISK_THRESHOLD_HIGH (Default: 0.30 - 0.70)
    # HIGH: score >= RISK_THRESHOLD_HIGH (Default: 0.70)
    RISK_THRESHOLD_LOW: float = float(os.getenv("RISK_THRESHOLD_LOW", "0.30"))
    RISK_THRESHOLD_HIGH: float = float(os.getenv("RISK_THRESHOLD_HIGH", "0.70"))
    
    # Storage Backend: 'sqlite' | 'memory' | 'dynamodb'
    STORAGE_BACKEND: str = os.getenv("STORAGE_BACKEND", "sqlite")
    SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", "backend/fraudshield.db")
    
    # Model Paths & Inference
    INFERENCE_ENGINE: str = os.getenv("INFERENCE_ENGINE", "local")
    LOCAL_MODEL_PATH: str = os.getenv("LOCAL_MODEL_PATH", "models/fraud_detector_pipeline.joblib")
    USER_PROFILES_PATH: str = os.getenv("USER_PROFILES_PATH", "models/user_profiles.json")
    METRICS_PATH: str = os.getenv("METRICS_PATH", "models/metrics.json")
    
    # AWS Settings (used when ENVIRONMENT == 'aws')
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    DYNAMODB_TRANSACTIONS_TABLE: str = os.getenv("DYNAMODB_TRANSACTIONS_TABLE", "FraudShieldTransactions")
    DYNAMODB_USERS_TABLE: str = os.getenv("DYNAMODB_USERS_TABLE", "FraudShieldUserProfiles")
    SAGEMAKER_ENDPOINT_NAME: str = os.getenv("SAGEMAKER_ENDPOINT_NAME", "fraudshield-xgb-endpoint")


settings = Settings()
