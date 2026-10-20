# AWS FraudShield — Real-Time E-Commerce Fraud Detection System

[![Python 3.11+](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.15-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3-61DAFB.svg)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6.svg)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38B2AC.svg)](https://tailwindcss.com/)
[![AWS Serverless](https://img.shields.io/badge/AWS-Lambda%20%7C%20DynamoDB%20%7C%20SageMaker-FF9900.svg)](https://aws.amazon.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**AWS FraudShield** is an end-to-end, machine-learning-powered fraud detection system designed for modern e-commerce architectures. It intercepts simulated payment transactions in real time, evaluates them against historical customer behavioral baselines, computes calibrated fraud risk probabilities, and returns actionable recommendations (`APPROVE`, `VERIFY_MFA`, or `FLAG_FOR_REVIEW`) accompanied by transparent, human-readable signal explanations.

> **Important Operational Note**:  
> All transactions, customer profiles, and banking signals in this repository are **strictly simulated**. FraudShield does not connect to actual financial institutions, payment gateways, or live banking accounts. Model predictions represent probabilistic risk indicators, not definitive proof of fraud.

---

## Table of Contents

1. [Problem Statement & Key Philosophy](#1-problem-statement--key-philosophy)
2. [End-to-End System Architecture](#2-end-to-end-system-architecture)
3. [Technology Stack](#3-technology-stack)
4. [Repository Structure](#4-repository-structure)
5. [Machine Learning Pipeline & Evaluation](#5-machine-learning-pipeline--evaluation)
6. [Local Quickstart (Zero AWS Credentials Required)](#6-local-quickstart-zero-aws-credentials-required)
7. [Running Tests](#7-running-tests)
8. [API Documentation & Sample Payloads](#8-api-documentation--sample-payloads)
9. [Interactive React Operations Dashboard](#9-interactive-react-operations-dashboard)
10. [AWS Cloud Deployment Guide](#10-aws-cloud-deployment-guide)
11. [Cost Optimization & Teardown](#11-cost-optimization--teardown)
12. [How to Push to GitHub](#12-how-to-push-to-github)
13. [Limitations & Roadmap](#13-limitations--roadmap)

---

## 1. Problem Statement & Key Philosophy

In retail e-commerce, fraud accounts for 0.5%–5% of transactional volume. Traditional rule-based filters (such as flat monetary caps or country blocks) introduce extreme customer friction:
- **Legitimate High-Value Spend**: An established customer purchasing a ₹45,000 laptop from their verified home computer should not be declined simply because of high spend.
- **Legitimate Travel**: A customer booking dinner in Goa on their familiar smartphone represents normal holiday spending.
- **Account Takeover (ATO) Attacks**: Real ATO attacks manifest through **correlated multidimensional anomalies**: an amount 10x higher than normal, executed from an unrecognized device hash, originating from an unusual foreign IP, during late-night hours.

### The FraudShield Principle:
**High transaction amount, new location, or new device alone must never automatically establish fraud.** Predictions are probabilistic risk scores derived from multidimensional signals, paired with human-in-the-loop audit tools.

---

## 2. End-to-End System Architecture

FraudShield implements a **Hexagonal Port-Adapter Pattern**. The core machine learning engine does not hardcode cloud dependencies. In development, it executes locally using SQLite and Scikit-Learn. In production, it deploys serverlessly onto AWS.

```
                              +---------------------------------------+
                              |         Amazon CloudWatch             |
                              | - Structured JSON transaction logs    |
                              | - Latency & 4xx/5xx alarms            |
                              +-------------------+-------------------+
                                                  ^
                                                  | logs
+---------------------+     HTTPS      +----------+---------+                +-------------------------+
|    React Dashboard  | -------------> | Amazon API Gateway | -------------> |        AWS Lambda       |
| (Vite / TypeScript) | <------------- |  (REST Endpoints)  | <------------- | (fraudshield-analyzer)  |
+---------------------+                +--------------------+                +------------+------------+
                                                                                          |
                                           +----------------------------------------------+--------------------+
                                           |                                                                   |
                                           v                                                                   v
                              +-------------------------+                                         +-------------------------+
                              |     Amazon DynamoDB     |                                         |     Amazon SageMaker    |
                              | - FraudShieldTx         |                                         | - Real-time Inference   |
                              | - FraudShieldProfiles   |                                         |   Endpoint (XGBoost)    |
                              +-------------------------+                                         +------------+------------+
                                                                                                               ^
                                                                                                               | loads model
                                                                                                  +------------+------------+
                                                                                                  |        Amazon S3        |
                                                                                                  | - Model Tarballs & CSVs |
                                                                                                  +-------------------------+
```

### Local Development vs AWS Cloud Mapping

| Component | Local Development Mode | AWS Cloud Production Mode |
|---|---|---|
| **API Server** | FastAPI (`backend/server.py` on Uvicorn) | Amazon API Gateway + AWS Lambda |
| **Storage** | SQLite (`backend/fraudshield.db`) | Amazon DynamoDB (`FraudShieldTransactions`) |
| **User Profiles** | Local JSON (`models/user_profiles.json`) | Amazon DynamoDB (`FraudShieldUserProfiles`) |
| **Model Serving** | Joblib Scikit-Learn Pipeline (`models/*.joblib`) | Amazon SageMaker Real-Time Endpoint |
| **Logging** | Console & Local File Logs | Amazon CloudWatch Logs (`/aws/lambda/...`) |

---

## 3. Technology Stack

### Machine Learning & Data Science
- **Language**: Python 3.11 / 3.12 / 3.15
- **Libraries**: NumPy, Pandas, Scikit-Learn, Joblib, Scipy
- **Visualization**: Matplotlib, Seaborn
- **Algorithms Evaluated**: Logistic Regression, Random Forest, HistGradientBoosting / XGBoost

### Backend & Cloud
- **Framework**: FastAPI, Pydantic V2, Uvicorn
- **Cloud Providers**: AWS Lambda, API Gateway, DynamoDB, SageMaker, S3, CloudWatch
- **SDK**: Boto3

### Frontend Application
- **Runtime**: Node.js 20+ / 24+ LTS
- **Framework**: React 18, TypeScript, Vite
- **Styling**: Tailwind CSS
- **Visualization**: Recharts (Area charts, Donut charts)
- **Icons**: Lucide React

### Testing & Validation
- **Test Runner**: Pytest (19 unit & integration tests)
- **HTTP Testing**: Httpx / FastAPI TestClient

---

## 4. Repository Structure

```
aws-fraudshield/
├── README.md                      # Primary project overview, setup & AWS deployment guide
├── LICENSE                        # MIT Open Source License
├── .gitignore                     # Git ignore rules for Python, Node, data binaries & secrets
├── .env.example                   # Environment variable template with safe defaults
├── requirements.txt               # Top-level Python ML and API dependencies
├── docs/
│   ├── project-report.md          # Comprehensive academic/architectural project report
│   └── architecture.md            # Detailed Mermaid diagrams and cloud topologies
├── data/
│   ├── README.md                  # Dataset documentation, schema, and limitations
│   └── fraud_transactions.csv     # Generated 6,000-sample transaction benchmark
├── notebooks/
│   └── fraud_detection_eda.ipynb  # Interactive Jupyter exploratory data analysis notebook
├── src/
│   ├── __init__.py                # ML package initializer
│   ├── data_generator.py          # Synthetic behavioral transaction & user profile generator
│   ├── feature_engineering.py     # Behavioral deviation features (zero temporal leakage)
│   ├── preprocessing.py           # Missing value cleaning, deduplication, and stratified split
│   ├── train.py                   # Multi-model training, class reweighting, and model selection
│   └── evaluate.py                # Standalone evaluation tool printing confusion matrices
├── models/
│   ├── README.md                  # Model card, decision band calibration, and metrics
│   ├── fraud_detector_pipeline.joblib # Serialized winning model pipeline
│   ├── user_profiles.json         # 60 historical user behavioral profiles
│   └── metrics.json               # Real evaluation metrics recorded from training run
├── backend/
│   ├── __init__.py
│   ├── config.py                  # Environment-based configuration dataclass
│   ├── storage.py                 # SQLite, In-Memory, and DynamoDB storage adapters
│   ├── inference.py               # Local Scikit-Learn and SageMaker inference engines
│   ├── service.py                 # Core domain service coordinating validation and scoring
│   ├── server.py                  # Local FastAPI REST server with CORS
│   ├── lambda_function.py         # AWS Lambda serverless handler for API Gateway
│   └── requirements.txt           # Minimal runtime dependencies for cloud packaging
├── infrastructure/
│   ├── README.md                  # AWS architecture specification and IAM least-privilege matrix
│   └── template.yaml              # AWS SAM / CloudFormation deployment template
├── frontend/
│   ├── package.json               # React, Vite, Tailwind, Recharts dependencies
│   ├── tsconfig.json              # TypeScript strict configuration
│   ├── vite.config.ts             # Vite build and proxy configuration
│   ├── tailwind.config.js         # Custom navy/cyan financial software styling
│   ├── index.html                 # Single page application entry point
│   └── src/
│       ├── main.tsx               # React DOM bootstrap
│       ├── App.tsx                # Main view router and global state
│       ├── api.ts                 # Typed REST client with error fallbacks
│       ├── types.ts               # Core domain TypeScript interfaces
│       ├── index.css              # Tailwind directives and custom scrollbars
│       ├── components/
│       │   ├── Header.tsx         # Top bar with environment badge & live polling
│       │   ├── Sidebar.tsx        # Dark navy navigational sidebar
│       │   └── RiskBadge.tsx      # Calibrated risk level and action badges
│       └── pages/
│           ├── Dashboard.tsx      # Telemetry KPIs, Recharts volume trend, risk donut
│           ├── Simulator.tsx      # Interactive transaction submission sandbox
│           ├── Scenarios.tsx      # 5 pre-configured attack and benign scenarios
│           ├── Transactions.tsx   # Searchable, filterable transaction table with slide-over
│           ├── Alerts.tsx         # Security operations incident triage console
│           └── ArchitectureView.tsx # Cloud topology viewer and IAM boundary matrix
└── tests/
    ├── test_preprocessing.py      # Tests cleaning, deduplication, and feature ratios
    ├── test_prediction.py         # Tests model scoring, ATO detection, and fallback resilience
    └── test_api.py                # Tests FastAPI HTTP routes, validation, and error responses
```

---

## 5. Machine Learning Pipeline & Evaluation

### Feature Engineering (Zero Target Leakage)
All behavioral signals are computed using historical user baselines without peeking into future transactions:
1. `amount_to_avg_ratio`: Current amount $\div$ historical mean
2. `amount_z_score`: $( \text{amount} - \mu ) \div \sigma$
3. `is_device_known`: Binary check against customer's registered hardware hashes
4. `is_location_unusual`: Binary check against customer's frequent cities
5. `is_merchant_familiar`: Historical merchant interaction flag
6. `hour_of_day`, `day_of_week`, `is_weekend`, `is_night_transaction`, `is_amount_spike`

### Model Comparison & Real Training Metrics
The pipeline trains candidate models under identical stratified 80/20 train/test splits (`RANDOM_STATE = 42`). The real metrics recorded from the training run (`models/metrics.json`):

| Model Candidate | Precision (Fraud) | Recall (Fraud) | F1-Score | ROC-AUC | PR-AUC |
|---|---|---|---|---|---|
| **Logistic Regression (Balanced)** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** |
| **Random Forest (120 Trees)** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** |
| **HistGradientBoosting** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **1.0000** |

#### Holdout Test Set Confusion Matrix (1,200 samples)
- **True Negatives** (Legitimate approved): 1,137
- **False Positives** (Legitimate flagged): 0 (Zero unnecessary customer friction)
- **False Negatives** (Fraud missed): 0 (Zero financial leakage)
- **True Positives** (Fraud intercepted): 63

---

## 6. Local Quickstart (Zero AWS Credentials Required)

Follow these steps to run FraudShield entirely on your local machine:

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/aws-fraudshield.git
cd aws-fraudshield
```

### Step 2: Set Up Python Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Generate Synthetic Behavioral Data & Train Models
```bash
# Generate 6,000 transactions and baseline profiles
python src/data_generator.py --samples 6000 --users 60 --seed 42

# Train models, select the winner, and serialize artifacts
python src/train.py

# Evaluate the serialized pipeline
python src/evaluate.py
```

### Step 5: Start the Backend API Server
```bash
# Runs FastAPI on http://127.0.0.1:8000
python backend/server.py
```
Test the health endpoint in your browser or curl:
```bash
curl http://127.0.0.1:8000/health
```

### Step 6: Launch the React Operations Dashboard
In a separate terminal window:
```bash
cd frontend
npm install
npm run dev
```
Open **`http://localhost:5173`** in your browser to interact with the live dashboard!

---

## 7. Running Tests

The test suite covers data validation, feature leakage prevention, ATO attack scoring, legitimate high-value edge cases, and API error codes:

```bash
pytest tests -v
```

Expected result:
```
tests/test_api.py::test_health_check_endpoint PASSED
tests/test_api.py::test_analyze_transaction_endpoint PASSED
tests/test_api.py::test_analyze_transaction_invalid_amount PASSED
tests/test_api.py::test_list_transactions_endpoint PASSED
tests/test_api.py::test_get_transaction_by_id PASSED
tests/test_api.py::test_get_transaction_not_found PASSED
tests/test_api.py::test_get_alerts_endpoint PASSED
tests/test_api.py::test_get_stats_endpoint PASSED
tests/test_prediction.py::test_normal_transaction_prediction PASSED
tests/test_prediction.py::test_account_takeover_attack_detection PASSED
tests/test_prediction.py::test_legitimate_high_value_transaction PASSED
tests/test_prediction.py::test_idempotency_prevents_duplicate_processing PASSED
tests/test_prediction.py::test_validation_rejects_missing_and_negative_amounts PASSED
tests/test_prediction.py::test_inference_engine_fallback_resilience PASSED
tests/test_preprocessing.py::test_clean_raw_data_removes_duplicates PASSED
tests/test_preprocessing.py::test_clean_raw_data_filters_invalid_amounts PASSED
tests/test_preprocessing.py::test_clean_raw_data_imputes_missing_categoricals PASSED
tests/test_preprocessing.py::test_feature_engineering_known_user_features PASSED
tests/test_preprocessing.py::test_feature_engineering_unknown_user_fallback PASSED

======================== 19 passed in 2.76s ========================
```

---

## 8. API Documentation & Sample Payloads

### 1. Analyze Transaction: `POST /transactions/analyze`

**Request Payload:**
```json
{
  "transaction_id": "TX-ATO-9001",
  "user_id": "USR-1001",
  "amount": 10000.0,
  "merchant": "Crypto Voucher Hub",
  "merchant_category": "digital_goods",
  "location": "Lagos, Nigeria",
  "device_id": "DEV-ATTACK-9999",
  "ip_address": "185.220.101.5",
  "timestamp": "2026-10-20T22:30:00Z"
}
```

**Response (HTTP 200 OK):**
```json
{
  "transaction_id": "TX-ATO-9001",
  "user_id": "USR-1001",
  "amount": 10000.0,
  "merchant": "Crypto Voucher Hub",
  "merchant_category": "digital_goods",
  "location": "Lagos, Nigeria",
  "device_id": "DEV-ATTACK-9999",
  "ip_address": "185.220.101.5",
  "timestamp": "2026-10-20T22:30:00Z",
  "risk_score": 0.985,
  "risk_level": "HIGH",
  "prediction": "SUSPICIOUS",
  "recommended_action": "FLAG_FOR_REVIEW",
  "risk_factors": [
    "Transaction amount ₹10,000.00 is 13.3x higher than user average (₹750.00)",
    "Transaction initiated from a previously unseen device",
    "Unusual or foreign geographic location: 'Lagos, Nigeria'"
  ],
  "engine_info": "local_scikit_learn_pipeline",
  "review_status": "FLAGGED_FOR_REVIEW"
}
```

### 2. Transaction Registry: `GET /transactions`
- Query parameters: `limit` (default 20), `offset` (default 0), `risk_level` (`ALL`, `LOW`, `MEDIUM`, `HIGH`)

### 3. Flagged Alerts Queue: `GET /alerts`
- Returns active transactions with risk level `HIGH` or `MEDIUM` requiring human-in-the-loop review.

### 4. Incident Review: `POST /alerts/{transaction_id}/review`
- Body: `{"review_status": "CONFIRMED_FRAUD", "notes": "Customer confirmed ATO attempt."}`

---

## 9. Interactive React Operations Dashboard

The dashboard provides a financial-security user experience:
1. **Executive Dashboard**: Telemetry metric cards, Recharts 24-hour volume trend, risk band donut chart, and real-time flagged activity table.
2. **Transaction Simulator**: Real-time evaluation sandbox with numeric dial, animated risk gauge, and raw JSON inspector.
3. **5 Scenario Demonstrations**:
   - *Scenario 1*: Normal ₹750 grocery purchase on familiar phone $\to$ `APPROVE`
   - *Scenario 2*: Legitimate ₹45,000 laptop on known device in home city $\to$ `APPROVE`
   - *Scenario 3*: Account Takeover ₹10,000 on unknown device in Lagos $\to$ `FLAG_FOR_REVIEW`
   - *Scenario 4*: Legitimate ₹1,800 travel dining in Goa $\to$ `APPROVE`
   - *Scenario 5*: Card-testing burst ₹49 micro-spend $\to$ `FLAG_FOR_REVIEW`
4. **Transaction History**: Filterable, paginated audit table with slide-over detail drawer.
5. **Alerts Triage**: Security operations center allowing analysts to mark `CONFIRMED_FRAUD`, `FALSE_POSITIVE`, or `WHITELISTED`.
6. **Cloud Architecture View**: Visual cloud topology viewer with IAM least-privilege matrix.

---

## 10. AWS Cloud Deployment Guide

When ready to deploy into a real AWS account:

### Prerequisites
- AWS CLI configured (`aws configure`)
- AWS SAM CLI installed (`sam --version`)
- IAM permissions for CloudFormation, Lambda, DynamoDB, S3, and API Gateway

### Deployment Steps
```bash
# 1. Package and deploy infrastructure with AWS SAM
cd infrastructure
sam build
sam deploy --guided \
  --stack-name aws-fraudshield \
  --region us-east-1 \
  --capabilities CAPABILITY_IAM

# 2. Upload model artifacts to the created S3 bucket
aws s3 cp ../models/fraud_detector_pipeline.joblib s3://<ArtifactsBucketName>/models/

# 3. Seed user historical baselines into DynamoDB
python -c "
import json, boto3
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('FraudShieldUserProfiles')
with open('../models/user_profiles.json') as f:
    profiles = json.load(f)
for uid, p in profiles.items():
    table.put_item(Item={'user_id': uid, 'profile_data': json.dumps(p)})
print('DynamoDB user profiles successfully seeded!')
"
```

---

## 11. Cost Optimization & Teardown

> [!WARNING]
> Continuous 24/7 SageMaker endpoints incur hourly instance costs. For lightweight cloud deployments, keep the model inside the AWS Lambda layer or container.

To prevent any unexpected AWS charges when finished:

```bash
# Delete the entire CloudFormation stack and all provisioned resources
aws cloudformation delete-stack --stack-name aws-fraudshield

# Delete SageMaker endpoint if manually deployed
aws sagemaker delete-endpoint --endpoint-name fraudshield-xgb-endpoint
aws sagemaker delete-endpoint-config --endpoint-config-name fraudshield-xgb-endpoint

# Empty and delete the S3 artifacts bucket
aws s3 rm s3://<ArtifactsBucketName> --recursive
aws s3 rb s3://<ArtifactsBucketName>
```

---

## 12. How to Push to GitHub

To push this completed project to your GitHub repository named `aws-fraudshield` **without committing secrets or overwriting existing repositories**:

```bash
# 1. Navigate to the project root
cd C:\Users\Makil\.gemini\antigravity\scratch\aws-fraudshield

# 2. Verify git status and ensure no .env files or credentials are tracked
git init
git status

# 3. Add all project files
git add .

# 4. Commit with a meaningful message
git commit -m "feat: complete runnable AWS FraudShield e-commerce fraud detection system"

# 5. Add your remote GitHub repository
git remote add origin https://github.com/your-username/aws-fraudshield.git

# 6. Set main branch and push safely
git branch -M main
git push -u origin main
```

---

## 13. Limitations & Roadmap

- **Graph Identity Analysis**: Future versions can incorporate Amazon Neptune to detect synthetic identity syndicates sharing device fingerprints.
- **Biometric MFA Triggers**: Future integrations with Amazon SNS to trigger instant SMS OTP or push notification when `VERIFY_MFA` is returned.
- **Model Drift Retraining**: EventBridge cron automation to retrain models periodically as consumer spend habits drift.

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
