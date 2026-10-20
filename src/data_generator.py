"""
AWS FraudShield - Synthetic Behavioral E-Commerce Transaction Generator
Generates realistic customer shopping histories, behavioral baselines,
legitimate edge cases, and attack scenarios without target leakage.
"""

import json
import os
import random
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple

# Reproducible random seed
DEFAULT_SEED = 42

INDIAN_CITIES = [
    "Bengaluru", "Mumbai", "Delhi NCR", "Hyderabad", "Chennai",
    "Pune", "Kolkata", "Ahmedabad", "Jaipur", "Kochi"
]

SUSPICIOUS_LOCATIONS = [
    "Lagos, Nigeria", "Bucharest, Romania", "St. Petersburg, Russia",
    "Unknown / Tor Exit Node", "Reykjavik, Iceland", "Caracas, Venezuela"
]

MERCHANTS = {
    "electronics": ["Amazon India", "Flipkart", "Croma", "Reliance Digital", "Apple Store India"],
    "fashion": ["Myntra", "Ajio", "Zara India", "H&M India", "Tata CLiQ"],
    "groceries": ["Blinkit", "Zepto", "Swiggy Instamart", "BigBasket"],
    "travel": ["MakeMyTrip", "IRCTC", "Cleartrip", "Uber India", "Ola"],
    "digital_goods": ["Steam Games", "Google Play Store", "Sony PlayStation Store", "Crypto Voucher Hub"]
}


def create_user_baselines(num_users: int = 50, seed: int = DEFAULT_SEED) -> Dict[str, dict]:
    """
    Generates baseline user behavioral profiles.
    Used for calculating historical deviations without future leakage.
    """
    random.seed(seed)
    profiles = {}
    
    for i in range(1, num_users + 1):
        user_id = f"USR-{1000 + i}"
        primary_city = random.choice(INDIAN_CITIES)
        secondary_city = random.choice([c for c in INDIAN_CITIES if c != primary_city])
        
        # Base spend distribution
        base_avg_amount = round(random.uniform(450.0, 1200.0), 2)
        base_std_amount = round(base_avg_amount * random.uniform(0.25, 0.45), 2)
        
        # Primary devices
        primary_device = f"DEV-ANDR-{random.randint(10000, 99999)}"
        secondary_device = f"DEV-LAP-{random.randint(10000, 99999)}"
        
        # Frequent merchants
        frequent_merchants = [
            random.choice(MERCHANTS["groceries"]),
            random.choice(MERCHANTS["fashion"]),
            random.choice(MERCHANTS["electronics"])
        ]
        
        profiles[user_id] = {
            "user_id": user_id,
            "avg_amount": base_avg_amount,
            "std_amount": base_std_amount,
            "total_historical_transactions": random.randint(25, 120),
            "primary_city": primary_city,
            "frequent_locations": [primary_city, secondary_city],
            "known_devices": [primary_device, secondary_device],
            "frequent_merchants": frequent_merchants,
            "preferred_hours": [random.randint(9, 22) for _ in range(4)]
        }
        
    return profiles


def generate_transactions(
    user_profiles: Dict[str, dict],
    total_samples: int = 5000,
    fraud_rate: float = 0.05,
    seed: int = DEFAULT_SEED
) -> List[dict]:
    """
    Generates simulated transactions combining legitimate everyday purchases,
    benign anomalies (high value on known device, travel), and realistic fraud vectors.
    """
    random.seed(seed)
    transactions = []
    
    start_time = datetime(2026, 8, 1, 0, 0, 0, tzinfo=timezone.utc)
    users = list(user_profiles.keys())
    
    # Track user transaction timestamps for velocity calculation
    user_last_tx = {u: start_time for u in users}
    
    for i in range(1, total_samples + 1):
        tx_id = f"TX-{200000 + i}"
        user_id = random.choice(users)
        profile = user_profiles[user_id]
        
        # Advance time realistically
        time_delta_minutes = random.randint(5, 720)
        current_time = user_last_tx[user_id] + timedelta(minutes=time_delta_minutes)
        user_last_tx[user_id] = current_time
        
        # Determine whether this transaction is fraudulent or legitimate
        is_fraud = 1 if random.random() < fraud_rate else 0
        scenario = "legitimate"
        
        if is_fraud:
            # 1. Attack Scenarios
            attack_type = random.choice(["account_takeover", "card_testing_burst", "abnormal_spike"])
            
            if attack_type == "account_takeover":
                # High amount, unseen device, suspicious remote location, odd hours
                amount = round(profile["avg_amount"] * random.uniform(8.0, 22.0) + random.uniform(5000, 15000), 2)
                device_id = f"DEV-ATTACK-{random.randint(10000, 99999)}"
                location = random.choice(SUSPICIOUS_LOCATIONS)
                cat = "electronics"
                merchant = random.choice(MERCHANTS[cat])
                scenario = "account_takeover"
                
            elif attack_type == "card_testing_burst":
                # Micro-amounts on digital goods, unknown device
                amount = round(random.uniform(25.0, 199.0), 2)
                device_id = f"DEV-BOT-{random.randint(10000, 99999)}"
                location = random.choice(SUSPICIOUS_LOCATIONS)
                cat = "digital_goods"
                merchant = random.choice(MERCHANTS[cat])
                scenario = "card_testing_burst"
                
            else:
                # Moderate amount spike with spoofed/new device
                amount = round(profile["avg_amount"] * random.uniform(5.0, 9.0), 2)
                device_id = f"DEV-UNKNOWN-{random.randint(10000, 99999)}"
                location = random.choice([c for c in INDIAN_CITIES if c not in profile["frequent_locations"]])
                cat = random.choice(["electronics", "travel"])
                merchant = random.choice(MERCHANTS[cat])
                scenario = "abnormal_spike"
                
        else:
            # 2. Legitimate Scenarios (including legitimate high spend and travel!)
            legit_type = random.choices(
                ["normal_routine", "legitimate_high_value", "legitimate_travel", "new_device_login"],
                weights=[0.82, 0.08, 0.06, 0.04],
                k=1
            )[0]
            
            if legit_type == "normal_routine":
                # Regular spend within 1-2 standard deviations, known device, familiar location
                amount = max(50.0, round(random.gauss(profile["avg_amount"], profile["std_amount"]), 2))
                device_id = random.choice(profile["known_devices"])
                location = random.choice(profile["frequent_locations"])
                cat = random.choice(["groceries", "fashion", "electronics", "travel"])
                merchant = random.choice(MERCHANTS[cat])
                scenario = "normal_routine"
                
            elif legit_type == "legitimate_high_value":
                # High amount (e.g. laptop or holiday), but from KNOWN device and familiar location
                amount = round(random.uniform(15000.0, 48000.0), 2)
                device_id = profile["known_devices"][0]  # Known primary device!
                location = profile["primary_city"]      # Known home location!
                cat = "electronics"
                merchant = "Apple Store India"
                scenario = "legitimate_high_value"
                
            elif legit_type == "legitimate_travel":
                # Vacation/travel: unusual location, but using familiar mobile phone
                amount = round(random.uniform(800.0, 3500.0), 2)
                device_id = profile["known_devices"][0]  # Mobile phone
                location = random.choice(["Goa", "Jaipur", "Kochi", "Singapore"])
                cat = "travel"
                merchant = random.choice(MERCHANTS["travel"])
                scenario = "legitimate_travel"
                
            else:
                # User bought a new phone or laptop, normal amount, home city
                amount = round(random.gauss(profile["avg_amount"], profile["std_amount"]), 2)
                device_id = f"DEV-NEW-{random.randint(10000, 99999)}"
                location = profile["primary_city"]
                cat = "groceries"
                merchant = random.choice(MERCHANTS["groceries"])
                scenario = "new_device_login"

        ip_prefix = "103." if "India" in location or location in INDIAN_CITIES else "185."
        ip_address = f"{ip_prefix}{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"
        
        record = {
            "transaction_id": tx_id,
            "user_id": user_id,
            "timestamp": current_time.isoformat(),
            "amount": float(amount),
            "merchant": merchant,
            "merchant_category": cat,
            "location": location,
            "device_id": device_id,
            "ip_address": ip_address,
            "is_fraud": is_fraud,
            "fraud_scenario": scenario
        }
        transactions.append(record)
        
    return transactions


def generate_and_save_data(
    output_csv: str = "data/fraud_transactions.csv",
    profiles_json: str = "models/user_profiles.json",
    num_users: int = 60,
    num_samples: int = 5000,
    seed: int = DEFAULT_SEED
) -> Tuple[str, str]:
    """Generates baseline profiles and transactions, saving them to disk."""
    import pandas as pd
    
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    os.makedirs(os.path.dirname(profiles_json), exist_ok=True)
    
    profiles = create_user_baselines(num_users=num_users, seed=seed)
    with open(profiles_json, "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=2)
        
    records = generate_transactions(profiles, total_samples=num_samples, seed=seed)
    df = pd.DataFrame(records)
    df.to_csv(output_csv, index=False)
    
    print(f"Generated {len(df)} transactions ({df['is_fraud'].sum()} fraudulent, {len(df)-df['is_fraud'].sum()} legitimate).")
    print(f"Saved transactions to: {output_csv}")
    print(f"Saved user profiles to: {profiles_json}")
    return output_csv, profiles_json


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate synthetic fraud transaction data")
    parser.add_argument("--samples", type=int, default=5000)
    parser.add_argument("--users", type=int, default=60)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=str, default="data/fraud_transactions.csv")
    parser.add_argument("--profiles", type=str, default="models/user_profiles.json")
    args = parser.parse_args()
    
    generate_and_save_data(
        output_csv=args.output,
        profiles_json=args.profiles,
        num_users=args.users,
        num_samples=args.samples,
        seed=args.seed
    )
