"""
Authentication service for handling auth operations.
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status

from app.core.security import SecurityUtils, JWTUtils, token_blacklist
from app.core.config import settings
from app.models.enums import UserRole, TokenType
from app.models.user import UserModel, UserCreateRequest
from app.schemas.auth import (
    UserRegisterRequest,
    UserRegisterResponse,
    UserLoginRequest,
    TokenResponse,
    UserInfo,
    PasswordResetRequest,
    PasswordResetResponse,
    TeacherPasswordResetRequest
)
from app.services.database_service import database_service


class AuthService:
    """Service for authentication operations."""
    
    async def register_user(self, request: UserRegisterRequest) -> UserRegisterResponse:
        """
        Register a new user.
        
        Args:
            request: User registration data
            
        Returns:
            UserRegisterResponse with user info
            
        Raises:
            HTTPException if email/username already exists
        """
        # Check if email already exists
        existing_user = await database_service.get_user_by_email(request.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if username already exists
        existing_username = await database_service.get_user_by_username(request.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Validate role assignment
        if request.role == UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admin role can only be assigned manually"
            )
        
        # Hash password
        hashed_password = SecurityUtils.get_password_hash(request.password)
        
        # Create user model
        user_data = UserCreateRequest(
            email=request.email,
            username=request.username,
            hashed_password=hashed_password,
            full_name=request.full_name,
            role=request.role,
            email_verified=False,  # Will be verified later if email system is set up
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Save user to database
        try:
            created_user = await database_service.create_user(user_data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user: {str(e)}"
            )
        
        return UserRegisterResponse(
            user_id=str(created_user.id),
            email=created_user.email,
            username=created_user.username,
            full_name=created_user.full_name,
            role=created_user.role,
            email_verified=created_user.email_verified,
            created_at=created_user.created_at,
            message="Registration successful"
        )
    
    async def login_user(self, request: UserLoginRequest) -> TokenResponse:
        """
        Authenticate user and return JWT tokens.
        
        Args:
            request: Login credentials
            
        Returns:
            TokenResponse with access and refresh tokens
            
        Raises:
            HTTPException if credentials are invalid
        """
        # Get user by email
        user = await database_service.get_user_by_email(request.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify password
        if not SecurityUtils.verify_password(request.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is disabled"
            )
        
        # Create tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        access_token = JWTUtils.create_access_token(
            subject=str(user.id),
            expires_delta=access_token_expires,
            additional_claims={
                "email": user.email,
                "username": user.username,
                "role": user.role
            }
        )
        
        refresh_token = JWTUtils.create_refresh_token(
            subject=str(user.id),
            expires_delta=refresh_token_expires
        )
        
        # Update last login time
        await database_service.update_user_last_login(str(user.id))
        
        # Create user info
        user_info = UserInfo(
            id=str(user.id),
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            role=user.role,
            email_verified=user.email_verified,
            is_active=user.is_active,
            created_at=user.created_at
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # in seconds
            user=user_info
        )
    
    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            TokenResponse with new tokens
            
        Raises:
            HTTPException if refresh token is invalid
        """
        # Verify refresh token
        payload = JWTUtils.verify_token(refresh_token, TokenType.REFRESH)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user
        user = await database_service.get_user_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create new tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        new_access_token = JWTUtils.create_access_token(
            subject=str(user.id),
            expires_delta=access_token_expires,
            additional_claims={
                "email": user.email,
                "username": user.username,
                "role": user.role
            }
        )
        
        new_refresh_token = JWTUtils.create_refresh_token(
            subject=str(user.id),
            expires_delta=refresh_token_expires
        )
        
        # Blacklist old refresh token
        token_blacklist.add_token(refresh_token)
        
        # Create user info
        user_info = UserInfo(
            id=str(user.id),
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            role=user.role,
            email_verified=user.email_verified,
            is_active=user.is_active,
            created_at=user.created_at
        )
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_info
        )
    
    async def logout_user(self, access_token: str, refresh_token: Optional[str] = None) -> dict:
        """
        Logout user by blacklisting tokens.
        
        Args:
            access_token: User's access token
            refresh_token: User's refresh token (optional)
            
        Returns:
            Success message
        """
        # Add tokens to blacklist
        token_blacklist.add_token(access_token)
        if refresh_token:
            token_blacklist.add_token(refresh_token)
        
        return {"message": "Successfully logged out"}
    
    async def reset_password_admin(
        self,
        target_user_id: str,
        request: PasswordResetRequest,
        admin_user_id: str
    ) -> PasswordResetResponse:
        """
        Admin reset user password.
        
        Args:
            target_user_id: ID of user whose password to reset
            request: Password reset data
            admin_user_id: ID of admin performing reset
            
        Returns:
            PasswordResetResponse
            
        Raises:
            HTTPException if user not found
        """
        # Get target user
        target_user = await database_service.get_user_by_id(target_user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Hash new password
        new_password_hash = SecurityUtils.get_password_hash(request.new_password)
        
        # Update user password
        await database_service.update_user_password(
            target_user_id,
            new_password_hash,
            force_change=request.force_change_on_login
        )
        
        # Log password reset (you might want to implement audit logging)
        # await audit_service.log_password_reset(admin_user_id, target_user_id, request.reset_reason)
        
        return PasswordResetResponse(
            user_id=target_user_id,
            message="Password reset successfully",
            reset_by=admin_user_id,
            reset_at=datetime.utcnow(),
            force_change_required=request.force_change_on_login
        )
    
    async def reset_password_teacher(
        self,
        request: TeacherPasswordResetRequest,
        teacher_user_id: str
    ) -> PasswordResetResponse:
        """
        Teacher reset student password.
        
        Args:
            request: Password reset data
            teacher_user_id: ID of teacher performing reset
            
        Returns:
            PasswordResetResponse
            
        Raises:
            HTTPException if validation fails
        """
        # Get student user
        student_user = await database_service.get_user_by_id(request.student_id)
        if not student_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
        # Verify student role
        if student_user.role != UserRole.STUDENT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Target user is not a student"
            )
        
        # Verify teacher-student relationship (check if student is in teacher's class)
        has_relationship = await database_service.check_teacher_student_relationship(
            teacher_user_id, request.student_id
        )
        if not has_relationship:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to reset this student's password"
            )
        
        # Hash new password
        new_password_hash = SecurityUtils.get_password_hash(request.new_password)
        
        # Update student password
        await database_service.update_user_password(
            request.student_id,
            new_password_hash,
            force_change=True
        )
        
        return PasswordResetResponse(
            user_id=request.student_id,
            message="Student password reset successfully",
            reset_by=teacher_user_id,
            reset_at=datetime.utcnow(),
            force_change_required=True
        )


# Global auth service instance
auth_service = AuthService()
