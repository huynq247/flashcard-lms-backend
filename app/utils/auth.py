"""
Authentication utilities for JWT tokens, passwords, and security.
"""
import os
import jwt
import hashlib
from datetime import datetime, timedelta, UTC
from typing import Optional, Dict, Any, Set
from passlib.context import CryptContext
from fastapi import HTTPException, status

from app.core.config import settings
from app.models.enums import TokenType

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token blacklist (in production, use Redis)
token_blacklist: Set[str] = set()


# ==================== PASSWORD FUNCTIONS ====================

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def validate_password_strength(password: str) -> bool:
    """
    Validate password strength.
    Requirements: min 8 chars, 1 uppercase, 1 lowercase, 1 digit, 1 special char
    """
    if len(password) < 8:
        return False
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    return all([has_upper, has_lower, has_digit, has_special])


# ==================== JWT TOKEN FUNCTIONS ====================

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(UTC),
        "type": TokenType.ACCESS.value
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(UTC),
        "type": TokenType.REFRESH.value
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


def verify_token_type(payload: Dict[str, Any], expected_type: TokenType) -> bool:
    """Verify token type matches expected type."""
    token_type = payload.get("type")
    return token_type == expected_type.value


# ==================== TOKEN BLACKLIST FUNCTIONS ====================

def add_token_to_blacklist(token: str) -> None:
    """Add token to blacklist."""
    # Create a hash of the token for security
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    token_blacklist.add(token_hash)


def is_token_blacklisted(token: str) -> bool:
    """Check if token is blacklisted."""
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    return token_hash in token_blacklist


def clear_token_blacklist() -> None:
    """Clear token blacklist (for testing)."""
    global token_blacklist
    token_blacklist.clear()


# ==================== SPECIAL TOKEN FUNCTIONS ====================

def create_password_reset_token(user_id: str) -> str:
    """Create password reset token."""
    data = {
        "user_id": user_id,
        "type": TokenType.PASSWORD_RESET.value
    }
    expire = datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
    
    data.update({
        "exp": expire,
        "iat": datetime.utcnow()
    })
    
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_email_verification_token(user_id: str, email: str) -> str:
    """Create email verification token."""
    data = {
        "user_id": user_id,
        "email": email,
        "type": TokenType.EMAIL_VERIFICATION.value
    }
    expire = datetime.utcnow() + timedelta(hours=24)  # 24 hours expiry
    
    data.update({
        "exp": expire,
        "iat": datetime.utcnow()
    })
    
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_api_key_token(user_id: str, api_key_name: str) -> str:
    """Create API key token (long-lived)."""
    data = {
        "user_id": user_id,
        "api_key_name": api_key_name,
        "type": TokenType.API_KEY.value
    }
    expire = datetime.utcnow() + timedelta(days=365)  # 1 year expiry
    
    data.update({
        "exp": expire,
        "iat": datetime.utcnow()
    })
    
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# ==================== TOKEN VALIDATION FUNCTIONS ====================

def validate_access_token(token: str) -> Dict[str, Any]:
    """Validate access token and return payload."""
    if is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked"
        )
    
    payload = decode_token(token)
    
    if not verify_token_type(payload, TokenType.ACCESS):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    return payload


def validate_refresh_token(token: str) -> Dict[str, Any]:
    """Validate refresh token and return payload."""
    if is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked"
        )
    
    payload = decode_token(token)
    
    if not verify_token_type(payload, TokenType.REFRESH):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token type"
        )
    
    return payload


def validate_special_token(token: str, expected_type: TokenType) -> Dict[str, Any]:
    """Validate special token (password reset, email verification, etc)."""
    payload = decode_token(token)
    
    if not verify_token_type(payload, expected_type):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid {expected_type.value} token"
        )
    
    return payload


# ==================== UTILITY FUNCTIONS ====================

def extract_token_from_header(authorization: str) -> str:
    """Extract token from Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )
    
    return authorization.split(" ")[1]


def get_token_expiry(token: str) -> datetime:
    """Get token expiry time."""
    payload = decode_token(token)
    exp_timestamp = payload.get("exp")
    
    if exp_timestamp:
        return datetime.fromtimestamp(exp_timestamp)
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token has no expiry information"
    )


def is_token_expired(token: str) -> bool:
    """Check if token is expired."""
    try:
        expiry = get_token_expiry(token)
        return datetime.utcnow() > expiry
    except HTTPException:
        return True  # If we can't get expiry, consider it expired
