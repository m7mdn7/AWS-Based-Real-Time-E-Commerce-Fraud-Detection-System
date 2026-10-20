# AWS FraudShield — Data Directory

This directory contains transaction data, behavioral user baselines, and dataset documentation for the FraudShield machine learning pipeline.

---

## 1. Dataset Strategy & Synthetic Behavioral Engine

In real-world e-commerce fraud prevention, risk scoring relies heavily on **behavioral deviations against a user's known profile**:
- Spending amount vs typical transaction distribution
- Device fingerprint familiarity (familiar device vs unseen device)
- Geographic location consistency (home city vs distant state/country)
- Transaction velocity (bursts within 1 hour or 24 hours)
- Merchant category familiarity

### Why Synthetic Behavioral Data for Development?
Popular public fraud datasets (such as the Kaggle Credit Card Fraud Detection dataset) contain anonymized numerical columns generated via PCA (V1 through V28) along with `Time` and `Amount`. While valuable for generic anomaly detection benchmarks, they:
1. Strip all customer behavioral identity, device headers, and merchant contexts.
2. Cannot evaluate device spoofing, credential stuffing, or geographic velocity anomalies.
3. Obscure the explainability signals required for fraud analysts.

To address this, FraudShield includes a deterministic, reproducible **Behavioral Transaction Generator** (`src/data_generator.py`) that models realistic consumer shopping habits, account takeover patterns, and edge cases.

---

## 2. Dataset Schema

Each generated transaction record adheres to the following schema:

| Column | Data Type | Description |
|---|---|---|
| `transaction_id` | string | Unique transaction identifier (e.g., `TX-100293`) |
| `user_id` | string | Account identifier (e.g., `USR-042`) |
| `timestamp` | string (ISO-8601) | Date and time the transaction was initiated |
| `amount` | float | Transaction value in INR (₹) |
| `merchant` | string | E-commerce merchant name (e.g., `Amazon India`, `Flipkart`, `Apple Store`) |
| `merchant_category` | string | Category: `electronics`, `fashion`, `groceries`, `travel`, `digital_goods` |
| `location` | string | City/region where transaction initiated (e.g., `Bengaluru`, `Mumbai`, `London`) |
| `device_id` | string | Device identifier or hardware fingerprint hash |
| `ip_address` | string | Client IP address |
| `is_fraud` | int (0 or 1) | Ground truth label (0 = Legitimate, 1 = Fraudulent) |
| `fraud_scenario` | string | Description of the attack vector (if fraud) or `legitimate` |

---

## 3. Behavioral Scenarios Modeled

1. **Normal Purchases**: Regular ₹400 - ₹1,200 purchases during daytime on known devices and home locations.
2. **Account Takeover (ATO)**: Sudden 10x-20x spike in amount (₹10,000+), new device fingerprint, unseen IP, and distant geographic location.
3. **Card Testing / Velocity Bursts**: Rapid succession of small transactions (4+ within 15 minutes) targeting digital goods.
4. **Legitimate High-Value Purchase**: A customer purchasing an expensive laptop (₹50,000) on their *known device* from their *primary home city*. Demonstrates that high value alone does not equal fraud.
5. **Legitimate Travel Purchase**: A customer purchasing dining or transport in a foreign city from their familiar smartphone.

---

## 4. How to Generate / Regenerate Data

Run the generator script with a reproducible seed:

```bash
python src/data_generator.py --samples 5000 --seed 42 --output data/fraud_transactions.csv
```

This will generate `data/fraud_transactions.csv` and initialize historical baselines.
