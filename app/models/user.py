"""
User model definitions for the application.
"""
from typing import Optional, List
from datetime import datetime, UTC
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.models.enums import UserRole


class UserModel(BaseModel):
    """User model for database operations."""
    id: str = Field(..., description="Unique user identifier")
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    full_name: str = Field(..., min_length=1, max_length=100, description="Full name")
    hashed_password: str = Field(..., description="Hashed password")
    role: UserRole = Field(default=UserRole.STUDENT, description="User role")
    email_verified: bool = Field(default=False, description="Email verification status")
    is_active: bool = Field(default=True, description="Account active status")
    force_password_change: bool = Field(default=False, description="Force password change on next login")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Account creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    last_login: Optional[datetime] = Field(default=None, description="Last login timestamp")
    
    model_config = ConfigDict(from_attributes=True)


class UserCreateRequest(BaseModel):
    """Request model for user creation."""
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=8, description="Password")
    full_name: str = Field(..., min_length=1, max_length=100, description="Full name")
    role: UserRole = Field(default=UserRole.STUDENT, description="User role")


class UserResponse(BaseModel):
    """Response model for user data."""
    id: str = Field(..., description="Unique user identifier")
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., description="Username")
    full_name: str = Field(..., description="Full name")
    role: UserRole = Field(..., description="User role")
    email_verified: bool = Field(..., description="Email verification status")
    is_active: bool = Field(..., description="Account active status")
    created_at: datetime = Field(..., description="Account creation timestamp")
    last_login: Optional[datetime] = Field(default=None, description="Last login timestamp")
    
    model_config = ConfigDict(from_attributes=True)


class UserUpdateRequest(BaseModel):
    """Request model for user updates."""
    full_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Full name")
    email: Optional[EmailStr] = Field(None, description="User email address")
    
    model_config = ConfigDict(extra="forbid")


class PasswordChangeRequest(BaseModel):
    """Request model for password change."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")


class AdminPasswordResetRequest(BaseModel):
    """Request model for admin password reset."""
    new_password: str = Field(..., min_length=8, description="New password")
    reset_reason: str = Field(..., min_length=5, description="Reason for password reset")
    force_change_on_login: bool = Field(default=True, description="Force password change on next login")


class UserLoginRequest(BaseModel):
    """Request model for user login."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="Password")


class UserLoginResponse(BaseModel):
    """Response model for user login."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: UserResponse = Field(..., description="User information")


class TokenRefreshRequest(BaseModel):
    """Request model for token refresh."""
    refresh_token: str = Field(..., description="Refresh token")


class LogoutRequest(BaseModel):
    """Request model for logout."""
    access_token: str = Field(..., description="Access token to blacklist")
    refresh_token: str = Field(..., description="Refresh token to blacklist")


class LogoutResponse(BaseModel):
    """Response model for logout."""
    message: str = Field(..., description="Logout confirmation message")


class UserListResponse(BaseModel):
    """Response model for user list."""
    users: List[UserResponse] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")


class UserRegistrationResponse(BaseModel):
    """Response model for user registration."""
    user_id: str = Field(..., description="Created user ID")
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., description="Username")
    full_name: str = Field(..., description="Full name")
    role: UserRole = Field(..., description="User role")
    email_verified: bool = Field(..., description="Email verification status")
    created_at: datetime = Field(..., description="Account creation timestamp")
    message: str = Field(..., description="Registration confirmation message")
    
    model_config = ConfigDict()
