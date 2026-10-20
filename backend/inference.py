"""
AWS FraudShield - Model Inference Engines
Encapsulates real-time model scoring via local Scikit-Learn pipeline
or AWS SageMaker real-time inference endpoint.
"""

import json
import os
import sys
from abc import ABC, abstractmethod
from typing import Optional, Tuple

import joblib
import pandas as pd

from backend.config import settings


class InferenceEngine(ABC):
    """Abstract interface for risk score computation."""
    
    @abstractmethod
    def predict_risk(self, features_df: pd.DataFrame) -> Tuple[float, str]:
        """
        Takes a 1-row DataFrame of engineered features.
        Returns:
            risk_score: float in [0.0, 1.0]
            engine_info: string identifying which engine scored the request
        """
        pass


class LocalInferenceEngine(InferenceEngine):
    """Local inference engine that executes the fitted scikit-learn pipeline."""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or settings.LOCAL_MODEL_PATH
        self.pipeline = None
        self._load_pipeline()
        
    def _load_pipeline(self):
        if os.path.exists(self.model_path):
            try:
                self.pipeline = joblib.load(self.model_path)
            except Exception as e:
                print(f"[Warning] Failed to load pipeline from {self.model_path}: {e}")
                self.pipeline = None
        else:
            print(f"[Warning] Model file not found at {self.model_path}. Running with fallback heuristic engine.")
            self.pipeline = None
            
    def predict_risk(self, features_df: pd.DataFrame) -> Tuple[float, str]:
        # Reload pipeline if it became available after initialization
        if self.pipeline is None and os.path.exists(self.model_path):
            self._load_pipeline()
            
        if self.pipeline is not None:
            try:
                # predict_proba returns [P(legit), P(fraud)]
                probabilities = self.pipeline.predict_proba(features_df)
                fraud_prob = float(probabilities[0][1])
                return round(fraud_prob, 4), "local_scikit_learn_pipeline"
            except Exception as e:
                print(f"[Inference Error] Pipeline execution failed: {e}. Falling back to rule scoring.")

        # Fallback heuristic calculation if model unavailable
        row = features_df.iloc[0]
        score = 0.05
        if row.get("amount_to_avg_ratio", 1.0) > 4.0:
            score += 0.40
        if row.get("is_device_known", 1) == 0:
            score += 0.35
        if row.get("is_location_unusual", 0) == 1:
            score += 0.20
        if row.get("is_night_transaction", 0) == 1:
            score += 0.10
        return min(round(score, 4), 0.99), "fallback_heuristic_engine"


class SageMakerInferenceEngine(InferenceEngine):
    """AWS SageMaker client for managed cloud inference endpoints."""
    
    def __init__(self, endpoint_name: Optional[str] = None, region: Optional[str] = None):
        self.endpoint_name = endpoint_name or settings.SAGEMAKER_ENDPOINT_NAME
        self.region = region or settings.AWS_REGION
        self.client = None
        try:
            import boto3
            self.client = boto3.client("sagemaker-runtime", region_name=self.region)
        except Exception as e:
            print(f"[Warning] SageMaker client initialization failed: {e}")

    def predict_risk(self, features_df: pd.DataFrame) -> Tuple[float, str]:
        if self.client is None:
            raise RuntimeError("SageMaker client is not initialized or AWS credentials missing.")
            
        payload = features_df.to_json(orient="split")
        response = self.client.invoke_endpoint(
            EndpointName=self.endpoint_name,
            ContentType="application/json",
            Body=payload
        )
        result = json.loads(response["Body"].read().decode("utf-8"))
        # Parse returned probability
        fraud_prob = float(result.get("predictions", [0.0])[0])
        return round(fraud_prob, 4), f"sagemaker_endpoint:{self.endpoint_name}"


def get_inference_engine(engine_type: Optional[str] = None) -> InferenceEngine:
    """Inference engine factory."""
    eng = (engine_type or settings.INFERENCE_ENGINE).lower()
    if eng == "sagemaker" and settings.ENVIRONMENT == "aws":
        try:
            return SageMakerInferenceEngine()
        except Exception:
            return LocalInferenceEngine()
    return LocalInferenceEngine()
