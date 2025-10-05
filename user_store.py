from __future__ import annotations
import sqlite3, hashlib, hmac, secrets, datetime
from pathlib import Path
from typing import Tuple, Optional

DB_PATH = Path(__file__).resolve().parent / "users.db"

def init_db(db_path: Optional[str] = None) -> None:
    path = str(db_path or DB_PATH)
    with sqlite3.connect(path) as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            pwd_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """)
        c.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        conn.commit()

def _hash_password(password: str, salt_hex: Optional[str] = None) -> Tuple[str, str]:
    if salt_hex is None:
        salt_hex = secrets.token_hex(16)  # 16 bytes -> 32 hex chars
    salt = bytes.fromhex(salt_hex)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return salt_hex, dk.hex()

def create_user_record(name: str, email: str, password: str) -> Tuple[bool, str]:
    email_l = email.strip().lower()
    with sqlite3.connect(str(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute("SELECT 1 FROM users WHERE email=?", (email_l,))
        if c.fetchone():
            return False, "An account with this email already exists. Try logging in."
        salt_hex, pwd_hash = _hash_password(password)
        c.execute(
            "INSERT INTO users(name, email, pwd_hash, salt, created_at) VALUES(?,?,?,?,?)",
            (name.strip(), email_l, pwd_hash, salt_hex, datetime.datetime.utcnow().isoformat())
        )
        conn.commit()
    return True, "Account created."

def verify_user_record(email: str, password: str) -> Tuple[bool, Optional[str]]:
    email_l = email.strip().lower()
    with sqlite3.connect(str(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute("SELECT name, pwd_hash, salt FROM users WHERE email=?", (email_l,))
        row = c.fetchone()
    if not row:
        return False, None
    name, stored_hash_hex, salt_hex = row
    _, check_hash_hex = _hash_password(password, salt_hex)
    return (hmac.compare_digest(stored_hash_hex, check_hash_hex), name if hmac.compare_digest(stored_hash_hex, check_hash_hex) else None)
