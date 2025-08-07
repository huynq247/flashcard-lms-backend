"""
Authentication endpoints for user registration, login, and password management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.deps import get_current_active_user, require_admin, require_teacher
from app.models.user import UserModel
from app.schemas.auth import (
    UserRegisterRequest,
    UserRegisterResponse,
    UserLoginRequest,
    TokenResponse,
    TokenRefreshRequest,
    TokenRefreshResponse,
    LogoutRequest,
    PasswordResetRequest,
    PasswordResetResponse,
    TeacherPasswordResetRequest,
    ChangePasswordRequest,
    ChangePasswordResponse
)
from app.services.auth_service import auth_service


router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserRegisterResponse)
async def register(request: UserRegisterRequest):
    """
    Register a new user.
    
    - **email**: Valid email address (unique)
    - **username**: Username 3-50 characters (unique, alphanumeric)
    - **password**: Password with strength requirements
    - **full_name**: User's full name
    - **role**: User role (default: student)
    """
    return await auth_service.register_user(request)


@router.post("/login", response_model=TokenResponse)
async def login(request: UserLoginRequest):
    """
    Authenticate user and return JWT tokens.
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns access token (30 min) and refresh token (7 days).
    """
    return await auth_service.login_user(request)


@router.post("/login/form", response_model=TokenResponse)
async def login_form(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible login endpoint for form data.
    
    This endpoint accepts form data (username/password) and is compatible
    with OAuth2 password flow for automatic API documentation.
    """
    # Convert form data to login request (username field contains email)
    login_request = UserLoginRequest(
        email=form_data.username,  # OAuth2 uses 'username' field for email
        password=form_data.password
    )
    return await auth_service.login_user(login_request)


@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(request: TokenRefreshRequest):
    """
    Refresh access token using refresh token.
    
    - **refresh_token**: Valid refresh token
    
    Returns new access and refresh tokens.
    """
    token_response = await auth_service.refresh_token(request.refresh_token)
    return TokenRefreshResponse(
        access_token=token_response.access_token,
        refresh_token=token_response.refresh_token,
        token_type=token_response.token_type,
        expires_in=token_response.expires_in
    )


@router.post("/logout")
async def logout(
    request: LogoutRequest,
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Logout user by blacklisting tokens.
    
    - **access_token**: User's current access token
    - **refresh_token**: User's refresh token (optional)
    """
    return await auth_service.logout_user(
        request.access_token,
        request.refresh_token
    )


@router.post("/change-password", response_model=ChangePasswordResponse)
async def change_password(
    request: ChangePasswordRequest,
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Change user's own password.
    
    - **current_password**: User's current password
    - **new_password**: New password with strength requirements
    """
    from app.core.security import SecurityUtils
    from app.services.database_service import database_service
    from datetime import datetime
    
    # Verify current password
    if not SecurityUtils.verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Hash new password
    new_password_hash = SecurityUtils.get_password_hash(request.new_password)
    
    # Update password
    await database_service.update_user_password(
        str(current_user.id),
        new_password_hash,
        force_change=False
    )
    
    return ChangePasswordResponse(
        user_id=str(current_user.id),
        message="Password changed successfully",
        changed_at=datetime.utcnow()
    )


@router.get("/me", response_model=UserRegisterResponse)
async def get_current_user_info(
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Get current user information.
    """
    return UserRegisterResponse(
        user_id=str(current_user.id),
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        role=current_user.role,
        email_verified=current_user.email_verified,
        created_at=current_user.created_at,
        message="User information retrieved successfully"
    )


# Admin endpoints
@router.put("/admin/users/{user_id}/reset-password", response_model=PasswordResetResponse)
async def admin_reset_password(
    user_id: str,
    request: PasswordResetRequest,
    admin_user: UserModel = Depends(require_admin)
):
    """
    Admin reset user password.
    
    **Admin only**: Reset any user's password.
    
    - **user_id**: ID of user whose password to reset
    - **new_password**: New password with strength requirements
    - **reset_reason**: Reason for password reset (optional)
    - **force_change_on_login**: Force user to change password on next login
    """
    return await auth_service.reset_password_admin(
        target_user_id=user_id,
        request=request,
        admin_user_id=str(admin_user.id)
    )


# Teacher endpoints
@router.put("/teacher/students/{student_id}/reset-password", response_model=PasswordResetResponse)
async def teacher_reset_student_password(
    student_id: str,
    request: TeacherPasswordResetRequest,
    teacher_user: UserModel = Depends(require_teacher)
):
    """
    Teacher reset student password.
    
    **Teacher only**: Reset password for students in their classes.
    
    - **student_id**: ID of student whose password to reset
    - **new_password**: New password with strength requirements
    - **reset_reason**: Reason for password reset (optional)
    
    Note: Teacher-student relationship is verified before allowing reset.
    """
    # Override student_id in request to match URL parameter
    request.student_id = student_id
    
    return await auth_service.reset_password_teacher(
        request=request,
        teacher_user_id=str(teacher_user.id)
    )


# Health check endpoint
@router.get("/health")
async def auth_health_check():
    """
    Authentication service health check.
    """
    return {
        "status": "healthy",
        "service": "authentication",
        "timestamp": "2025-08-07T18:31:00Z"
    }
