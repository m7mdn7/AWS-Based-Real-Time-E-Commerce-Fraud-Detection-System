"""
AWS FraudShield - Storage Adapters
Provides an abstract storage interface with implementations for SQLite (local dev),
In-Memory (unit tests), and Amazon DynamoDB (AWS cloud).
"""

import json
import os
import sqlite3
import threading
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from backend.config import settings


class StorageAdapter(ABC):
    """Abstract interface defining required storage operations."""
    
    @abstractmethod
    def save_transaction(self, tx: dict) -> dict:
        pass
        
    @abstractmethod
    def get_transaction(self, tx_id: str) -> Optional[dict]:
        pass
        
    @abstractmethod
    def list_transactions(
        self,
        limit: int = 20,
        offset: int = 0,
        risk_level: Optional[str] = None
    ) -> Tuple[List[dict], int]:
        pass
        
    @abstractmethod
    def list_alerts(self, limit: int = 50) -> List[dict]:
        pass
        
    @abstractmethod
    def update_alert_status(self, tx_id: str, review_status: str, notes: str = "") -> Optional[dict]:
        pass
        
    @abstractmethod
    def get_user_profile(self, user_id: str) -> Optional[dict]:
        pass
        
    @abstractmethod
    def get_dashboard_stats(self) -> dict:
        pass


class SQLiteStorageAdapter(StorageAdapter):
    """Local thread-safe SQLite storage implementation."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.SQLITE_DB_PATH
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        self._lock = threading.Lock()
        self._init_db()
        self._seed_profiles_if_empty()
        
    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
        
    def _init_db(self):
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS transactions (
                        transaction_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        amount REAL NOT NULL,
                        merchant TEXT NOT NULL,
                        merchant_category TEXT,
                        location TEXT NOT NULL,
                        device_id TEXT NOT NULL,
                        ip_address TEXT,
                        timestamp TEXT NOT NULL,
                        risk_score REAL NOT NULL,
                        risk_level TEXT NOT NULL,
                        prediction TEXT NOT NULL,
                        recommended_action TEXT NOT NULL,
                        risk_factors TEXT NOT NULL,
                        review_status TEXT DEFAULT 'PENDING_REVIEW',
                        review_notes TEXT DEFAULT '',
                        created_at TEXT NOT NULL
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_profiles (
                        user_id TEXT PRIMARY KEY,
                        profile_data TEXT NOT NULL
                    )
                """)
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_tx_user ON transactions(user_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_tx_risk ON transactions(risk_level)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_tx_created ON transactions(created_at)")
                conn.commit()
            finally:
                conn.close()
                
    def _seed_profiles_if_empty(self):
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) as count FROM user_profiles")
                count = cursor.fetchone()["count"]
                if count == 0 and os.path.exists(settings.USER_PROFILES_PATH):
                    with open(settings.USER_PROFILES_PATH, "r", encoding="utf-8") as f:
                        profiles = json.load(f)
                    for uid, prof in profiles.items():
                        cursor.execute(
                            "INSERT OR REPLACE INTO user_profiles (user_id, profile_data) VALUES (?, ?)",
                            (uid, json.dumps(prof))
                        )
                    conn.commit()
            finally:
                conn.close()

    def _row_to_tx(self, row: sqlite3.Row) -> dict:
        d = dict(row)
        try:
            d["risk_factors"] = json.loads(d["risk_factors"])
        except Exception:
            d["risk_factors"] = []
        return d

    def save_transaction(self, tx: dict) -> dict:
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                now_str = datetime.now(timezone.utc).isoformat()
                risk_factors_json = json.dumps(tx.get("risk_factors", []))
                
                cursor.execute("""
                    INSERT OR REPLACE INTO transactions (
                        transaction_id, user_id, amount, merchant, merchant_category,
                        location, device_id, ip_address, timestamp, risk_score,
                        risk_level, prediction, recommended_action, risk_factors,
                        review_status, review_notes, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    tx["transaction_id"],
                    tx["user_id"],
                    float(tx["amount"]),
                    tx.get("merchant", "Unknown Merchant"),
                    tx.get("merchant_category", "general"),
                    tx.get("location", "Unknown Location"),
                    tx.get("device_id", "UNKNOWN_DEV"),
                    tx.get("ip_address", "127.0.0.1"),
                    tx.get("timestamp", now_str),
                    float(tx["risk_score"]),
                    tx["risk_level"],
                    tx["prediction"],
                    tx["recommended_action"],
                    risk_factors_json,
                    tx.get("review_status", "PENDING_REVIEW"),
                    tx.get("review_notes", ""),
                    now_str
                ))
                conn.commit()
                return tx
            finally:
                conn.close()

    def get_transaction(self, tx_id: str) -> Optional[dict]:
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM transactions WHERE transaction_id = ?", (tx_id,))
                row = cursor.fetchone()
                return self._row_to_tx(row) if row else None
            finally:
                conn.close()

    def list_transactions(
        self,
        limit: int = 20,
        offset: int = 0,
        risk_level: Optional[str] = None
    ) -> Tuple[List[dict], int]:
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                if risk_level and risk_level.upper() != "ALL":
                    cursor.execute("SELECT COUNT(*) as total FROM transactions WHERE risk_level = ?", (risk_level.upper(),))
                    total = cursor.fetchone()["total"]
                    cursor.execute(
                        "SELECT * FROM transactions WHERE risk_level = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
                        (risk_level.upper(), limit, offset)
                    )
                else:
                    cursor.execute("SELECT COUNT(*) as total FROM transactions")
                    total = cursor.fetchone()["total"]
                    cursor.execute(
                        "SELECT * FROM transactions ORDER BY created_at DESC LIMIT ? OFFSET ?",
                        (limit, offset)
                    )
                rows = cursor.fetchall()
                return [self._row_to_tx(r) for r in rows], total
            finally:
                conn.close()

    def list_alerts(self, limit: int = 50) -> List[dict]:
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM transactions WHERE risk_level IN ('HIGH', 'MEDIUM') ORDER BY created_at DESC LIMIT ?",
                    (limit,)
                )
                rows = cursor.fetchall()
                return [self._row_to_tx(r) for r in rows]
            finally:
                conn.close()

    def update_alert_status(self, tx_id: str, review_status: str, notes: str = "") -> Optional[dict]:
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE transactions SET review_status = ?, review_notes = ? WHERE transaction_id = ?",
                    (review_status, notes, tx_id)
                )
                conn.commit()
                return self.get_transaction(tx_id)
            finally:
                conn.close()

    def get_user_profile(self, user_id: str) -> Optional[dict]:
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT profile_data FROM user_profiles WHERE user_id = ?", (user_id,))
                row = cursor.fetchone()
                if row:
                    return json.loads(row["profile_data"])
                return None
            finally:
                conn.close()

    def get_dashboard_stats(self) -> dict:
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) as total FROM transactions")
                total = cursor.fetchone()["total"]
                
                cursor.execute("SELECT COUNT(*) as high FROM transactions WHERE risk_level = 'HIGH'")
                high = cursor.fetchone()["high"]
                
                cursor.execute("SELECT COUNT(*) as med FROM transactions WHERE risk_level = 'MEDIUM'")
                med = cursor.fetchone()["med"]
                
                cursor.execute("SELECT COUNT(*) as low FROM transactions WHERE risk_level = 'LOW'")
                low = cursor.fetchone()["low"]
                
                return {
                    "total_transactions": total,
                    "high_risk_count": high,
                    "medium_risk_count": med,
                    "low_risk_count": low,
                    "alert_count": high + med
                }
            finally:
                conn.close()


class MemoryStorageAdapter(StorageAdapter):
    """In-memory storage adapter for zero-IO unit testing."""
    
    def __init__(self):
        self.transactions: Dict[str, dict] = {}
        self.user_profiles: Dict[str, dict] = {}
        
    def save_transaction(self, tx: dict) -> dict:
        tx_copy = dict(tx)
        tx_copy.setdefault("created_at", datetime.now(timezone.utc).isoformat())
        tx_copy.setdefault("review_status", "PENDING_REVIEW")
        tx_copy.setdefault("review_notes", "")
        self.transactions[tx["transaction_id"]] = tx_copy
        return tx_copy

    def get_transaction(self, tx_id: str) -> Optional[dict]:
        return self.transactions.get(tx_id)

    def list_transactions(
        self,
        limit: int = 20,
        offset: int = 0,
        risk_level: Optional[str] = None
    ) -> Tuple[List[dict], int]:
        all_tx = list(self.transactions.values())
        if risk_level and risk_level.upper() != "ALL":
            filtered = [t for t in all_tx if t.get("risk_level") == risk_level.upper()]
        else:
            filtered = all_tx
            
        filtered.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return filtered[offset:offset+limit], len(filtered)

    def list_alerts(self, limit: int = 50) -> List[dict]:
        alerts = [t for t in self.transactions.values() if t.get("risk_level") in ("HIGH", "MEDIUM")]
        alerts.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return alerts[:limit]

    def update_alert_status(self, tx_id: str, review_status: str, notes: str = "") -> Optional[dict]:
        if tx_id in self.transactions:
            self.transactions[tx_id]["review_status"] = review_status
            self.transactions[tx_id]["review_notes"] = notes
            return self.transactions[tx_id]
        return None

    def get_user_profile(self, user_id: str) -> Optional[dict]:
        return self.user_profiles.get(user_id)

    def get_dashboard_stats(self) -> dict:
        total = len(self.transactions)
        high = sum(1 for t in self.transactions.values() if t.get("risk_level") == "HIGH")
        med = sum(1 for t in self.transactions.values() if t.get("risk_level") == "MEDIUM")
        low = sum(1 for t in self.transactions.values() if t.get("risk_level") == "LOW")
        return {
            "total_transactions": total,
            "high_risk_count": high,
            "medium_risk_count": med,
            "low_risk_count": low,
            "alert_count": high + med
        }


class DynamoDBStorageAdapter(StorageAdapter):
    """AWS DynamoDB storage adapter for cloud deployments."""
    
    def __init__(self):
        try:
            import boto3
            self.dynamodb = boto3.resource("dynamodb", region_name=settings.AWS_REGION)
            self.tx_table = self.dynamodb.Table(settings.DYNAMODB_TRANSACTIONS_TABLE)
            self.users_table = self.dynamodb.Table(settings.DYNAMODB_USERS_TABLE)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize AWS DynamoDB client: {str(e)}")

    def save_transaction(self, tx: dict) -> dict:
        from decimal import Decimal
        item = json.loads(json.dumps(tx), parse_float=Decimal)
        item.setdefault("created_at", datetime.now(timezone.utc).isoformat())
        item.setdefault("review_status", "PENDING_REVIEW")
        item.setdefault("review_notes", "")
        self.tx_table.put_item(Item=item)
        return tx

    def get_transaction(self, tx_id: str) -> Optional[dict]:
        resp = self.tx_table.get_item(Key={"transaction_id": tx_id})
        return resp.get("Item")

    def list_transactions(
        self,
        limit: int = 20,
        offset: int = 0,
        risk_level: Optional[str] = None
    ) -> Tuple[List[dict], int]:
        # For production at scale, use GSI queries. Scan is fallback for simple demo.
        resp = self.tx_table.scan(Limit=limit)
        items = resp.get("Items", [])
        return items, len(items)

    def list_alerts(self, limit: int = 50) -> List[dict]:
        from boto3.dynamodb.conditions import Attr
        resp = self.tx_table.scan(
            FilterExpression=Attr("risk_level").is_in(["HIGH", "MEDIUM"]),
            Limit=limit
        )
        return resp.get("Items", [])

    def update_alert_status(self, tx_id: str, review_status: str, notes: str = "") -> Optional[dict]:
        resp = self.tx_table.update_item(
            Key={"transaction_id": tx_id},
            UpdateExpression="SET review_status = :s, review_notes = :n",
            ExpressionAttributeValues={":s": review_status, ":n": notes},
            ReturnValues="ALL_NEW"
        )
        return resp.get("Attributes")

    def get_user_profile(self, user_id: str) -> Optional[dict]:
        resp = self.users_table.get_item(Key={"user_id": user_id})
        return resp.get("Item")

    def get_dashboard_stats(self) -> dict:
        # Basic scan counts for demo deployment
        items, _ = self.list_transactions(limit=100)
        return {
            "total_transactions": len(items),
            "high_risk_count": sum(1 for t in items if t.get("risk_level") == "HIGH"),
            "medium_risk_count": sum(1 for t in items if t.get("risk_level") == "MEDIUM"),
            "low_risk_count": sum(1 for t in items if t.get("risk_level") == "LOW"),
            "alert_count": sum(1 for t in items if t.get("risk_level") in ("HIGH", "MEDIUM"))
        }


def get_storage_adapter(backend: Optional[str] = None) -> StorageAdapter:
    """Storage factory adhering to configured storage backend."""
    b = (backend or settings.STORAGE_BACKEND).lower()
    if b == "dynamodb" or settings.ENVIRONMENT == "aws":
        try:
            return DynamoDBStorageAdapter()
        except Exception:
            # Fall back to SQLite if AWS credentials/table not ready
            return SQLiteStorageAdapter()
    elif b == "memory":
        return MemoryStorageAdapter()
    else:
        return SQLiteStorageAdapter()
