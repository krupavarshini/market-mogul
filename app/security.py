# app/security.py
import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from jose import jwt
from app.core.config import settings

def hash_password(password: str) -> str:
    # Simple SHA256 hashing (good enough for a game project)
    salt = settings.SECRET_KEY
    return hashlib.sha256((password + salt).encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Compare hashes using constant-time comparison
    new_hash = hash_password(plain_password)
    return hmac.compare_digest(new_hash, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)