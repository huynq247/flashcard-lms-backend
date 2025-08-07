"""
Pydantic schemas for authentication and authorization.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.enums import UserRole


class UserRegisterRequest(BaseModel):
    """User registration request schema."""
    email: EmailStr
    username: str = Field(min_length=3, max_length=50, description="Username must be 3-50 characters")
    password: str = Field(min_length=8, description="Password must be at least 8 characters")
    full_name: str = Field(min_length=1, max_length=100, description="Full name is required")
    role: UserRole = Field(default=UserRole.STUDENT, description="User role (default: student)")
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not v.isalnum():
            raise ValueError('Username must contain only alphanumeric characters')
        return v.lower()
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        from app.core.security import SecurityUtils
        is_valid, message = SecurityUtils.validate_password_strength(v)
        if not is_valid:
            raise ValueError(message)
        return v


class UserRegisterResponse(BaseModel):
    """User registration response schema."""
    user_id: str
    email: EmailStr
    username: str
    full_name: str
    role: UserRole
    email_verified: bool = False
    created_at: datetime
    message: str = "Registration successful"


class UserLoginRequest(BaseModel):
    """User login request schema."""
    email: EmailStr
    password: str


class UserInfo(BaseModel):
    """User information included in token response."""
    id: str
    email: EmailStr
    username: str
    full_name: str
    role: UserRole
    email_verified: bool
    is_active: bool
    created_at: datetime


class TokenResponse(BaseModel):
    """JWT token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: UserInfo


class TokenRefreshRequest(BaseModel):
    """Token refresh request schema."""
    refresh_token: str


class TokenRefreshResponse(BaseModel):
    """Token refresh response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class LogoutRequest(BaseModel):
    """Logout request schema."""
    access_token: str
    refresh_token: Optional[str] = None


class PasswordResetRequest(BaseModel):
    """Admin password reset request schema."""
    new_password: str = Field(min_length=8, description="New password must be at least 8 characters")
    reset_reason: Optional[str] = Field(None, max_length=200, description="Reason for password reset")
    force_change_on_login: bool = Field(default=True, description="Force user to change password on next login")
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        from app.core.security import SecurityUtils
        is_valid, message = SecurityUtils.validate_password_strength(v)
        if not is_valid:
            raise ValueError(message)
        return v


class TeacherPasswordResetRequest(BaseModel):
    """Teacher password reset request schema."""
    new_password: str = Field(min_length=8, description="New password must be at least 8 characters")
    student_id: str = Field(description="Student ID to reset password for")
    reset_reason: Optional[str] = Field(None, max_length=200, description="Reason for password reset")
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        from app.core.security import SecurityUtils
        is_valid, message = SecurityUtils.validate_password_strength(v)
        if not is_valid:
            raise ValueError(message)
        return v


class PasswordResetResponse(BaseModel):
    """Password reset response schema."""
    user_id: str
    message: str
    reset_by: str
    reset_at: datetime
    force_change_required: bool


class EmailVerificationRequest(BaseModel):
    """Email verification request schema."""
    token: str


class EmailVerificationResponse(BaseModel):
    """Email verification response schema."""
    email: EmailStr
    verified_at: datetime
    message: str = "Email verified successfully"


class ChangePasswordRequest(BaseModel):
    """Change password request schema."""
    current_password: str
    new_password: str = Field(min_length=8, description="New password must be at least 8 characters")
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        from app.core.security import SecurityUtils
        is_valid, message = SecurityUtils.validate_password_strength(v)
        if not is_valid:
            raise ValueError(message)
        return v


class ChangePasswordResponse(BaseModel):
    """Change password response schema."""
    user_id: str
    message: str = "Password changed successfully"
    changed_at: datetime


# Error response schemas
class AuthErrorResponse(BaseModel):
    """Authentication error response schema."""
    detail: str
    error_code: str
    timestamp: datetime


class ValidationErrorResponse(BaseModel):
    """Validation error response schema."""
    detail: str
    field_errors: Optional[dict] = None
    timestamp: datetime
