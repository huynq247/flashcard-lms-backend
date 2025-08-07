"""
Authentication utilities for JWT token handling and password management.
"""
import secrets
from datetime import datetime, timedelta
from typing import Any, Optional, Union

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import ValidationError

from app.core.config import settings


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength.
    Returns (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    
    # Check for special characters
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is strong"


def generate_secure_password(length: int = 12) -> str:
    """Generate a secure random password."""
    import string
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(characters) for _ in range(length))


def create_access_token(
    subject: Union[str, Any], 
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[dict] = None
) -> str:
    """Create JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {
        "exp": expire,
        "iat": datetime.utcnow(),
        "sub": str(subject),
        "type": "access"
    }
    
    if additional_claims:
        to_encode.update(additional_claims)
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT refresh token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    
    to_encode = {
        "exp": expire,
        "iat": datetime.utcnow(),
        "sub": str(subject),
        "type": "refresh"
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
    """
    Verify JWT token and return payload.
    Returns None if token is invalid.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        # Check token type
        if payload.get("type") != token_type:
            return None
        
        # Check expiration
        exp = payload.get("exp")
        if exp is None:
            return None
            
        if datetime.utcnow() > datetime.fromtimestamp(exp):
            return None
        
        return payload
        
    except JWTError:
        return None
    except Exception:
        return None


def get_subject_from_token(token: str) -> Optional[str]:
    """Extract subject (user_id) from token."""
    payload = verify_token(token)
    if payload:
        return payload.get("sub")
    return None


def decode_token(token: str) -> Optional[dict]:
    """
    Decode JWT token without verification (for debugging).
    """
    try:
        return jwt.get_unverified_claims(token)
    except JWTError:
        return None


def is_token_expired(token: str) -> bool:
    """Check if token is expired."""
    try:
        payload = jwt.get_unverified_claims(token)
        exp = payload.get("exp")
        if exp is None:
            return True
        return datetime.utcnow() > datetime.fromtimestamp(exp)
    except JWTError:
        return True


def get_token_expiry(token: str) -> Optional[datetime]:
    """Get token expiry datetime."""
    try:
        payload = jwt.get_unverified_claims(token)
        exp = payload.get("exp")
        if exp:
            return datetime.fromtimestamp(exp)
        return None
    except JWTError:
        return None


# Token blacklist for logout functionality
class TokenBlacklist:
    """Simple in-memory token blacklist."""
    
    def __init__(self):
        self._blacklisted_tokens = set()
    
    def add_token(self, token: str) -> None:
        """Add token to blacklist."""
        self._blacklisted_tokens.add(token)
    
    def is_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted."""
        return token in self._blacklisted_tokens
    
    def remove_token(self, token: str) -> None:
        """Remove token from blacklist."""
        self._blacklisted_tokens.discard(token)
    
    def cleanup_expired_tokens(self) -> None:
        """Remove expired tokens from blacklist."""
        valid_tokens = set()
        for token in self._blacklisted_tokens:
            if not is_token_expired(token):
                valid_tokens.add(token)
        self._blacklisted_tokens = valid_tokens
    
    def size(self) -> int:
        """Get number of blacklisted tokens."""
        return len(self._blacklisted_tokens)
    
    def clear(self) -> None:
        """Clear all blacklisted tokens."""
        self._blacklisted_tokens.clear()


# Global token blacklist instance
token_blacklist = TokenBlacklist()


def logout_user(access_token: str, refresh_token: Optional[str] = None) -> dict:
    """
    Logout user by blacklisting tokens.
    """
    token_blacklist.add_token(access_token)
    if refresh_token:
        token_blacklist.add_token(refresh_token)
    
    return {"message": "Successfully logged out"}


def check_token_blacklist(token: str) -> bool:
    """Check if token is in blacklist."""
    return token_blacklist.is_blacklisted(token)


def generate_password_reset_token(user_id: str) -> str:
    """Generate password reset token."""
    expire = datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
    
    to_encode = {
        "exp": expire,
        "iat": datetime.utcnow(),
        "sub": str(user_id),
        "type": "password_reset"
    }
    
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def verify_password_reset_token(token: str) -> Optional[str]:
    """Verify password reset token and return user_id."""
    payload = verify_token(token, "password_reset")
    if payload:
        return payload.get("sub")
    return None


def generate_email_verification_token(email: str) -> str:
    """Generate email verification token."""
    expire = datetime.utcnow() + timedelta(days=1)  # 24 hours expiry
    
    to_encode = {
        "exp": expire,
        "iat": datetime.utcnow(),
        "email": email,
        "type": "email_verification"
    }
    
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def verify_email_verification_token(token: str) -> Optional[str]:
    """Verify email verification token and return email."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        if payload.get("type") != "email_verification":
            return None
        
        # Check expiration
        exp = payload.get("exp")
        if exp is None or datetime.utcnow() > datetime.fromtimestamp(exp):
            return None
        
        return payload.get("email")
        
    except JWTError:
        return None


def create_api_key(user_id: str, name: str) -> str:
    """Create API key for user."""
    # API keys don't expire but include creation time
    to_encode = {
        "iat": datetime.utcnow(),
        "sub": str(user_id),
        "type": "api_key",
        "name": name,
        "key_id": secrets.token_hex(16)
    }
    
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def verify_api_key(api_key: str) -> Optional[dict]:
    """Verify API key and return payload."""
    try:
        payload = jwt.decode(
            api_key,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        if payload.get("type") != "api_key":
            return None
        
        return payload
        
    except JWTError:
        return None
