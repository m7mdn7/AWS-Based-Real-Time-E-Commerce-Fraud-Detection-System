# AWS FraudShield — Infrastructure & Cloud Deployment

This folder contains Infrastructure-as-Code (IaC) templates, architecture specifications, and security policies for deploying AWS FraudShield onto Amazon Web Services.

---

## 1. Cloud Architecture Overview

```
                                      +------------------------------------+
                                      |         Amazon CloudWatch          |
                                      | - Transaction log aggregation      |
                                      | - Latency & 4xx/5xx alarms         |
                                      +-----------------+------------------+
                                                        ^
                                                        | logs
+-------------------+        +--------------------+     |      +------------------------+
|   React Client    |------->| Amazon API Gateway |---->+----->|       AWS Lambda       |
| (Vite/TypeScript) |  HTTPS | (REST API, CORS)   |            | (fraudshield-analyzer) |
+-------------------+        +--------------------+            +-----------+------------+
                                                                           |
                                              +----------------------------+----------------------------+
                                              |                                                         |
                                              v                                                         v
                                 +-------------------------+                               +-------------------------+
                                 |     Amazon DynamoDB     |                               |     Amazon SageMaker    |
                                 | - Transactions Table    |                               | - Real-time Inference   |
                                 | - UserProfiles Table    |                               |   Endpoint (XGBoost)    |
                                 +-------------------------+                               +------------+------------+
                                                                                                        ^
                                                                                                        | loads model
                                                                                           +------------+------------+
                                                                                           |        Amazon S3        |
                                                                                           | - Artifacts & Tarballs  |
                                                                                           +-------------------------+
```

---

## 2. Resource Inventory & Least-Privilege IAM Policies

### A. AWS Lambda (`fraudshield-analyzer`)
- **Runtime**: Python 3.11 / container image with scikit-learn & joblib.
- **Memory**: 512 MB – 1024 MB.
- **Timeout**: 15 seconds.
- **Environment Variables**:
  - `ENVIRONMENT=aws`
  - `DYNAMODB_TRANSACTIONS_TABLE=FraudShieldTransactions`
  - `DYNAMODB_USERS_TABLE=FraudShieldUserProfiles`
  - `SAGEMAKER_ENDPOINT_NAME=fraudshield-xgb-endpoint`
  - `RISK_THRESHOLD_LOW=0.30`
  - `RISK_THRESHOLD_HIGH=0.70`

### B. Amazon DynamoDB Tables
1. **`FraudShieldTransactions`**:
   - Partition Key: `transaction_id` (String)
   - Global Secondary Index (GSI): `user_id-timestamp-index` (`user_id` as PK, `timestamp` as SK)
   - Billing Mode: PAY_PER_REQUEST (On-Demand)
2. **`FraudShieldUserProfiles`**:
   - Partition Key: `user_id` (String)
   - Attributes: `avg_amount`, `std_amount`, `total_transactions`, `known_devices`, `frequent_locations`, `frequent_merchants`, `last_transaction_time`
   - Billing Mode: PAY_PER_REQUEST (On-Demand)

### C. Amazon SageMaker Endpoint
- **Instance Type**: `ml.t2.medium` (for cost-effective dev) or `ml.m5.large` (production).
- **Framework**: Scikit-learn / XGBoost container.
- **Alternative**: For lightweight serverless inference, the model `.joblib` can be packaged inside an AWS Lambda Layer / ECR container image without provisioning a continuous 24/7 SageMaker instance.

### D. Amazon S3 Bucket
- **Bucket**: `fraudshield-artifacts-<unique-id>`
- Encrypted with AES-256 (SSE-S3), public access blocked.

---

## 3. Least-Privilege IAM Role Example

Attached to Lambda execution role `FraudShieldLambdaRole`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DynamoDBAccess",
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": [
        "arn:aws:dynamodb:*:*:table/FraudShieldTransactions*",
        "arn:aws:dynamodb:*:*:table/FraudShieldUserProfiles*"
      ]
    },
    {
      "Sid": "SageMakerInference",
      "Effect": "Allow",
      "Action": [
        "sagemaker:InvokeEndpoint"
      ],
      "Resource": "arn:aws:sagemaker:*:*:endpoint/fraudshield-xgb-endpoint"
    },
    {
      "Sid": "CloudWatchLogs",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:log-group:/aws/lambda/fraudshield-analyzer:*"
    }
  ]
}
```

---

## 4. Cost Optimization & Cleanup

> [!WARNING]
> Amazon SageMaker endpoints incur hourly charges even when idle! For development, prefer the local container or Lambda-embedded model inference.

If deploying to AWS:
1. **Teardown Command**:
   ```bash
   aws sagemaker delete-endpoint --endpoint-name fraudshield-xgb-endpoint
   aws sagemaker delete-endpoint-config --endpoint-config-name fraudshield-xgb-endpoint
   aws dynamodb delete-table --table-name FraudShieldTransactions
   aws dynamodb delete-table --table-name FraudShieldUserProfiles
   aws lambda delete-function --function-name fraudshield-analyzer
   ```
2. Free tier compatibility:
   - DynamoDB offers 25 GB free storage and 25 WCU/RCU in the AWS Free Tier.
   - Lambda offers 1,000,000 free requests per month.
   - API Gateway offers 1,000,000 free REST calls per month.
