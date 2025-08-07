"""
Authentication Models for JWT and Auth-related schemas
Implements Decision #19: Basic Auth + Decision #3: Admin Reset
"""

from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from enum import Enum

from .user import UserRole


class TokenType(str, Enum):
    """Token types for JWT"""
    ACCESS = "access"
    REFRESH = "refresh"


class AuthStatus(str, Enum):
    """Authentication status"""
    SUCCESS = "success"
    FAILED = "failed"
    LOCKED = "locked"
    INACTIVE = "inactive"


# ===== REQUEST MODELS =====

class UserRegisterRequest(BaseModel):
    """User registration request (Decision #2: Optional Email)"""
    email: EmailStr
    username: str = Field(min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$")
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=1, max_length=100)
    role: UserRole = UserRole.STUDENT  # Default to student
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )


class UserLoginRequest(BaseModel):
    """User login request (Decision #19: Basic Auth)"""
    email: EmailStr
    password: str = Field(min_length=1)
    
    model_config = ConfigDict(
        str_strip_whitespace=True
    )


class PasswordResetRequest(BaseModel):
    """Admin password reset request (Decision #3: Admin Reset)"""
    new_password: str = Field(min_length=8)
    reset_reason: Optional[str] = None
    force_change_on_login: bool = True
    
    model_config = ConfigDict(
        str_strip_whitespace=True
    )


class TeacherPasswordResetRequest(BaseModel):
    """Teacher password reset for students"""
    new_password: str = Field(min_length=8)
    student_id: str = Field(min_length=24, max_length=24)
    reset_reason: Optional[str] = None
    
    model_config = ConfigDict(
        str_strip_whitespace=True
    )


class TokenRefreshRequest(BaseModel):
    """Token refresh request"""
    refresh_token: str = Field(min_length=1)


class EmailVerificationRequest(BaseModel):
    """Email verification request"""
    token: str = Field(min_length=1)


# ===== RESPONSE MODELS =====

class UserInfo(BaseModel):
    """User information in token response"""
    id: str
    email: str
    username: str
    full_name: str
    role: UserRole
    email_verified: bool
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True
    )


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: UserInfo
    
    model_config = ConfigDict(
        from_attributes=True
    )


class UserRegisterResponse(BaseModel):
    """User registration response"""
    user_id: str
    email: str
    username: str
    role: UserRole
    email_verified: bool = False
    message: str = "Registration successful"
    
    model_config = ConfigDict(
        from_attributes=True
    )


class PasswordResetResponse(BaseModel):
    """Password reset response"""
    user_id: str
    message: str
    reset_by: str
    reset_at: datetime
    force_change_required: bool
    
    model_config = ConfigDict(
        from_attributes=True
    )


class EmailVerificationResponse(BaseModel):
    """Email verification response"""
    user_id: str
    email: str
    verified_at: datetime
    message: str = "Email verified successfully"
    
    model_config = ConfigDict(
        from_attributes=True
    )


# ===== JWT PAYLOAD MODEL =====

class JWTPayload(BaseModel):
    """JWT token payload structure"""
    sub: str  # Subject (user ID)
    email: str
    username: str
    role: UserRole
    exp: int  # Expiration timestamp
    iat: int  # Issued at timestamp
    type: TokenType  # Token type (access/refresh)
    
    model_config = ConfigDict(
        from_attributes=True
    )


# ===== AUDIT MODELS =====

class AuthAttemptModel(BaseModel):
    """Authentication attempt tracking"""
    email: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status: AuthStatus
    attempted_at: datetime
    failure_reason: Optional[str] = None
    
    model_config = ConfigDict(
        from_attributes=True
    )


class PasswordResetAuditModel(BaseModel):
    """Password reset audit logging"""
    user_id: str
    reset_by_user_id: str
    reset_by_role: UserRole
    reset_reason: Optional[str] = None
    ip_address: Optional[str] = None
    reset_at: datetime
    force_change_required: bool
    
    model_config = ConfigDict(
        from_attributes=True
    )


# ===== TOKEN BLACKLIST MODEL =====

class TokenBlacklistModel(BaseModel):
    """JWT token blacklist for logout"""
    jti: str  # JWT ID (unique token identifier)
    user_id: str
    token_type: TokenType
    blacklisted_at: datetime
    expires_at: datetime
    reason: str = "logout"
    
    model_config = ConfigDict(
        from_attributes=True
    )


# ===== EMAIL VERIFICATION MODEL =====

class EmailVerificationTokenModel(BaseModel):
    """Email verification token"""
    user_id: str
    email: str
    token: str
    created_at: datetime
    expires_at: datetime
    is_used: bool = False
    used_at: Optional[datetime] = None
    
    model_config = ConfigDict(
        from_attributes=True
    )
