# AWS FraudShield — Comprehensive Project Report
## Machine Learning-Powered Real-Time E-Commerce Fraud Detection System

**Author**: Senior Full-Stack Developer, ML Engineer & AWS Cloud Architect  
**Project**: AWS FraudShield  
**Date**: October 2026  
**License**: MIT License  

---

## 1. Abstract

Electronic commerce platforms face evolving threats ranging from automated credential stuffing to account takeover (ATO) and card testing. Traditional rule-based antifraud filters (such as flat monetary limits or country blacklists) frequently create unacceptable customer friction by declining legitimate high-value purchases (e.g., consumer electronics) or authentic travel transactions, while simultaneously missing sophisticated micro-amount card-testing attacks.

**AWS FraudShield** addresses this challenge by combining client behavioral profiling with machine-learning risk assessment. Rather than evaluating transactions in isolation, FraudShield benchmarks incoming payment requests against a customer's known behavioral baseline (typical spend distribution, familiar device fingerprints, frequent merchant categories, and geographic habits). Built on a decoupled hexagonal architecture, FraudShield supports 100% functional, zero-credential local development alongside enterprise serverless deployment across Amazon API Gateway, AWS Lambda, Amazon DynamoDB, Amazon SageMaker, and Amazon CloudWatch.

---

## 2. Problem Definition

### 2.1 The Challenge of Imbalanced Fraud Data
In real-world retail commerce, fraudulent transactions represent between 0.5% and 5% of overall transactional volume. In such imbalanced settings, standard classification accuracy is a deceptive metric. A naive model that classifies every transaction as legitimate will achieve 95%–99% accuracy while failing to intercept any malicious activity. Antifraud systems must instead prioritize **Precision**, **Recall**, and the **Area Under the Precision-Recall Curve (PR-AUC)**.

### 2.2 The Inadequacy of Single-Factor Rules
- **High Transaction Amount Alone is Not Fraud**: An established customer purchasing a ₹45,000 laptop from their verified home computer should not be declined simply because the amount exceeds typical spend.
- **Unfamiliar Location Alone is Not Fraud**: A customer purchasing dining or lodging while on holiday using their primary smartphone represents legitimate travel.
- **Account Takeover (ATO) Signals**: True ATO attacks manifest as **correlated multidimensional deviations**: a large monetary spike executed from an unrecognized device hash, originating from an abnormal IP/location, at an unusual hour.

---

## 3. Objectives

1. **Behavioral Feature Engineering**: Implement a pipeline that extracts baseline behavioral ratios and anomaly indicators without temporal target leakage.
2. **Model Training & Model Selection**: Train and compare Logistic Regression, Random Forest, and Gradient Tree Boosting pipelines using stratified partitioning and class-imbalance reweighting.
3. **Calibrated Decision Logic**: Map probabilistic model scores to policy actions (`APPROVE`, `VERIFY_MFA`, `FLAG_FOR_REVIEW`) accompanied by transparent, human-readable signal explanations.
4. **Hexagonal Software Architecture**: Provide swappable adapters for local SQLite / Scikit-Learn execution and AWS Cloud DynamoDB / SageMaker execution.
5. **Interactive Operations Dashboard**: Build a modern React/TypeScript user interface featuring real-time transaction simulation, scenario testing, transaction search, and alert triage.

---

## 4. Methodology & Data Pipeline

### 4.1 Data Generation and Behavioral Modeling
To overcome the limitations of anonymized public PCA datasets (which strip device identifiers, user identity, and merchant categories), FraudShield includes a synthetic behavioral transaction engine (`src/data_generator.py`).
- **User Baselines**: Generates 60 distinct customer profiles with parameterized spending distributions ($\mu, \sigma$), primary and secondary cities, and verified hardware hashes (`DEV-ANDR-xxx`, `DEV-LAP-xxx`).
- **Attack & Benign Scenarios**:
  - Normal everyday purchases (₹400–₹1,200) on familiar devices.
  - Account Takeover attacks: ₹10,000+ spend on unseen device in foreign location.
  - Legitimate high-value purchases: ₹45,000 laptop on known device in home city.
  - Legitimate travel: ₹1,800 purchase in resort destination on primary phone.
  - Card-testing bursts: Micro-amounts (₹49) targeting digital gift vouchers.

### 4.2 Feature Engineering (Zero Leakage)
Features are computed solely using data available before or at the moment of the transaction:
- `amount_to_avg_ratio`: Current amount divided by user historical baseline average.
- `amount_z_score`: Standard deviations away from user historical mean.
- `is_device_known`: Binary flag indicating presence in verified hardware registry.
- `is_location_unusual`: Binary flag indicating deviation from frequent cities.
- `is_merchant_familiar`: Binary flag indicating historical merchant interaction.
- Temporal factors: Hour of day, weekend indicator, night transaction flag.

### 4.3 Candidate Classifiers & Evaluation
Models are trained under stratified 80/20 partitioning with `RANDOM_STATE = 42`:
- **Logistic Regression**: Scaled baseline with balanced class weights.
- **Random Forest Classifier**: Non-linear ensemble with 120 decision trees.
- **Gradient Boosting / HistGradientBoosting**: Boosting tree ensemble with negative-to-positive class weight scaling.

---

## 5. Software & Cloud Architecture

### 5.1 Local Development Stack
- **Backend API**: Python 3.11+, FastAPI, Uvicorn, Pydantic V2.
- **Storage Adapter**: SQLite with automatic schema creation and user profile seeding.
- **Inference Adapter**: Scikit-Learn pipeline loaded via Joblib with fallback heuristic scoring.
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons, Recharts.

### 5.2 AWS Serverless Cloud Stack
- **Amazon API Gateway**: HTTP proxy routing requests to AWS Lambda.
- **AWS Lambda (`fraudshield-analyzer`)**: Serverless function executing transaction analysis.
- **Amazon DynamoDB**: Key-value and document database hosting `FraudShieldTransactions` and `FraudShieldUserProfiles`.
- **Amazon SageMaker**: Hosted container endpoint for real-time model inference.
- **Amazon S3**: Artifact repository for trained `.joblib` and model tarballs.
- **Amazon CloudWatch**: Centralized log streams, invocation metrics, and latency alarms.

---

## 6. Testing Strategy

The test suite (`pytest`) covers unit, integration, and resiliency testing across 19 automated tests:
1. **Preprocessing & Cleaning**: Duplicate transaction ID deduplication, negative amount filtering, and missing attribute imputation.
2. **Feature Engineering**: Ratio computation for established accounts and graceful fallback to population baselines for new guest accounts.
3. **Prediction & Decision Bands**: Verification that normal purchases receive `APPROVE`, ATO attacks trigger `FLAG_FOR_REVIEW`, and legitimate high-value purchases are not falsely marked as guaranteed fraud.
4. **Resiliency & Fallback**: Verification that the inference engine falls back to heuristic scoring if a model file is missing or corrupted.
5. **Idempotency**: Ensuring duplicate requests return previously computed records without re-processing.
6. **API Endpoints**: Full HTTP request/response validation for `/health`, `/transactions/analyze`, `/transactions`, `/alerts`, and `/stats`.

---

## 7. Limitations & Future Work

### 7.1 Limitations
- **Simulated Environment**: All transactions and cardholder behaviors are simulated; the system does not connect to actual banking gateways or live payment networks.
- **Model Drift**: Consumer purchasing behaviors shift over time (e.g., holiday seasons or inflation); deployed models require scheduled retraining.
- **Cold Start for New Accounts**: Customers with zero prior history must initially be evaluated against population medians until a baseline is established.

### 7.2 Future Enhancements
- **Graph Neural Networks (GNNs)**: Constructing identity graphs linking shared device fingerprints, IP subnets, and delivery addresses to catch organized fraud syndicates.
- **Streaming Pipeline**: Transitioning from synchronous REST calls to event-driven streaming with Apache Kafka / Amazon Kinesis and AWS Step Functions.
- **Automated MFA Orchestration**: Direct integration with Amazon SNS / Twilio to dispatch biometric or one-time passcode challenges automatically when `VERIFY_MFA` is returned.

---

## 8. Conclusion

AWS FraudShield demonstrates that modern fraud prevention requires intelligent, contextual analysis rather than rigid static thresholds. By combining behavioral baselines with explainable machine learning and a decoupled cloud-ready architecture, FraudShield achieves high fraud interception rates while safeguarding authentic customer experiences.
