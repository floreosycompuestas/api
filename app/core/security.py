from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import uuid
from jose import JWTError, jwt
from passlib.context import CryptContext
from api.app.core.config import settings
from api.app.core.redis_client import RedisClient

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
ALGORITHM = settings.ALGORITHM
SECRET_KEY = settings.SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRES_MINUTES
REFRESH_TOKEN_EXPIRE_MINUTES = settings.REFRESH_TOKEN_EXPIRES_MINUTES

# Bcrypt max password length
BCRYPT_MAX_PASSWORD_LENGTH = 72


def hash_password(password: str) -> str:
    """Hash a password using bcrypt. Truncates to 72 bytes (bcrypt limit)."""
    # Bcrypt has a 72-byte limit, truncate if necessary
    password_bytes = password.encode('utf-8')[:BCRYPT_MAX_PASSWORD_LENGTH]
    password_truncated = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.hash(password_truncated)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hashed version. Truncates to 72 bytes."""
    # Bcrypt has a 72-byte limit, truncate if necessary
    password_bytes = plain_password.encode('utf-8')[:BCRYPT_MAX_PASSWORD_LENGTH]
    password_truncated = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.verify(password_truncated, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token with jti for revocation support."""
    to_encode = data.copy()
    to_encode["jti"] = str(uuid.uuid4())
    to_encode["type"] = "access"

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None, remember_me: bool = False) -> str:
    """Create a JWT refresh token with optional extended expiration for 'remember me' feature."""
    to_encode = data.copy()
    to_encode["jti"] = str(uuid.uuid4())
    to_encode["type"] = "refresh"
    to_encode["remember_me"] = remember_me  # Track if this is a "remember me" token

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    elif remember_me:
        # Use extended expiration (30 days) for "remember me"
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.REMEMBER_ME_REFRESH_TOKEN_EXPIRES_MINUTES)
    else:
        # Default expiration (7 days)
        expire = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and verify a JWT token. Check Redis for revocation."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Check if token is revoked in Redis
        jti = payload.get("jti")
        if jti and RedisClient.is_token_revoked(jti):
            return None
        return payload
    except JWTError:
        return None


def revoke_token(token: str) -> bool:
    """Revoke a token by adding its jti to Redis."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        jti = payload.get("jti")
        exp = payload.get("exp")

        if jti and exp:
            # Calculate seconds until token expiration
            expiration_seconds = int(exp - datetime.now(timezone.utc).timestamp())
            # Only revoke if token hasn't already expired
            if expiration_seconds > 0:
                return RedisClient.revoke_token(jti, expiration_seconds)
        return False
    except JWTError:
        return False
