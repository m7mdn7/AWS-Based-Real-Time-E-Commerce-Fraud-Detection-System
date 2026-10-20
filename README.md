# AWS FraudShield — Real-Time E-Commerce Fraud Detection

## Overview
AWS FraudShield is a planned cloud-based fraud detection application that analyzes e-commerce transactions using machine learning and user-behavior features to identify potentially suspicious activity.

## Problem Statement
Traditional fraud checks can miss account takeovers and unusual transaction patterns. High transaction amounts alone are not sufficient to determine fraud.

## Objectives
- Analyze transaction patterns and user history.
- Train and compare machine learning classifiers.
- Generate transaction risk scores.
- Expose predictions through an API.
- Store transaction history and flagged alerts.
- Visualize results in a dashboard.

## Technology Stack
- Python, Pandas, NumPy, scikit-learn
- AWS S3
- Amazon SageMaker
- AWS Lambda
- Amazon API Gateway
- Amazon DynamoDB
- Amazon CloudWatch
- React (planned frontend)

## Architecture
Transaction Simulator → API Gateway → Lambda → DynamoDB / SageMaker → Risk Result → Dashboard

S3 stores the training dataset and model artifacts.

## Machine Learning
Planned models: Logistic Regression, Random Forest, and XGBoost.

Evaluation metrics: Precision, Recall, F1-score, ROC-AUC, and Confusion Matrix.

## Scenarios
- Normal purchase
- Legitimate high-value purchase
- Compromised account with unusual activity
- Multiple rapid transactions
- Travel or a new device

## Security and Limitations
The project uses simulated transactions and does not process real payments. Predictions indicate risk, not proof of fraud. No credentials, personal payment information, or AWS secrets should be committed.

## Project Status
In development.

## Future Enhancements
- Simulated step-up verification
- Improved device and location signals
- Real-time transaction ingestion
- Automated fraud alerts
