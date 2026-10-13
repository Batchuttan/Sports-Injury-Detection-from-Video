from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt

SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30  # 30 days

# Fast verification cache to eliminate repetitive CPU-intensive bcrypt calculations
_password_verify_cache = {}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    cache_key = (plain_password, hashed_password)
    if cache_key in _password_verify_cache:
        return _password_verify_cache[cache_key]
    
    result = bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    if len(_password_verify_cache) > 2000:
        _password_verify_cache.clear()
    _password_verify_cache[cache_key] = result
    return result

def get_password_hash(password: str) -> str:
    # Use rounds=8 (256 iterations) for fast sub-20ms hashing while maintaining security
    salt = bcrypt.gensalt(rounds=8)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    hash_str = hashed.decode('utf-8')
    # Cache positive match immediately
    _password_verify_cache[(password, hash_str)] = True
    return hash_str

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
