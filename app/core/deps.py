"""
FastAPI dependencies for authentication and authorization.
"""
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from app.core.security import JWTUtils, token_blacklist
from app.models.enums import UserRole, Permission, ROLE_PERMISSIONS
from app.models.user import UserModel
from app.services.database_service import database_service


# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/v1/auth/login",
    scheme_name="JWT"
)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserModel:
    """
    Get current authenticated user from JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Check if token is blacklisted
    if token_blacklist.is_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Verify token
        payload = JWTUtils.verify_token(token)
        if payload is None:
            raise credentials_exception
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    try:
        user = await database_service.get_user_by_id(user_id)
        if user is None:
            raise credentials_exception
        return user
    except Exception:
        raise credentials_exception


async def get_current_active_user(
    current_user: UserModel = Depends(get_current_user)
) -> UserModel:
    """
    Get current active user (must be active).
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def require_role(*allowed_roles: UserRole):
    """
    Dependency factory for role-based access control.
    
    Usage:
        @app.get("/admin-only")
        async def admin_endpoint(user: UserModel = Depends(require_role(UserRole.ADMIN))):
            pass
    """
    def dependency(current_user: UserModel = Depends(get_current_active_user)) -> UserModel:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[role.value for role in allowed_roles]}"
            )
        return current_user
    
    return dependency


def require_permission(*required_permissions: Permission):
    """
    Dependency factory for permission-based access control.
    
    Usage:
        @app.post("/decks")
        async def create_deck(user: UserModel = Depends(require_permission(Permission.DECK_CREATE))):
            pass
    """
    def dependency(current_user: UserModel = Depends(get_current_active_user)) -> UserModel:
        user_permissions = ROLE_PERMISSIONS.get(current_user.role, [])
        
        for permission in required_permissions:
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required permission: {permission.value}"
                )
        
        return current_user
    
    return dependency


async def require_ownership(
    resource_type: str,
    resource_id: str,
    current_user: UserModel = Depends(get_current_active_user)
) -> UserModel:
    """
    Dependency for resource ownership validation.
    
    Args:
        resource_type: Type of resource (deck, class, course, lesson)
        resource_id: ID of the resource
        current_user: Current authenticated user
    
    Returns:
        UserModel if user owns the resource
    
    Raises:
        HTTPException if user doesn't own the resource
    """
    # Admin can access everything
    if current_user.role == UserRole.ADMIN:
        return current_user
    
    try:
        if resource_type == "deck":
            deck = await database_service.get_deck_by_id(resource_id)
            if deck and str(deck.owner_id) == str(current_user.id):
                return current_user
        
        elif resource_type == "class":
            class_obj = await database_service.get_class_by_id(resource_id)
            if class_obj and str(class_obj.teacher_id) == str(current_user.id):
                return current_user
        
        elif resource_type == "course":
            course = await database_service.get_course_by_id(resource_id)
            if course and str(course.creator_id) == str(current_user.id):
                return current_user
        
        # Add more resource types as needed
        
    except Exception:
        pass
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"Access denied. You don't own this {resource_type}"
    )


async def require_membership(
    membership_type: str,
    resource_id: str,
    current_user: UserModel = Depends(get_current_active_user)
) -> UserModel:
    """
    Dependency for membership validation (class, course enrollment).
    
    Args:
        membership_type: Type of membership (class, course, lesson)
        resource_id: ID of the resource
        current_user: Current authenticated user
    
    Returns:
        UserModel if user has access to the resource
    
    Raises:
        HTTPException if user doesn't have access
    """
    # Admin and teachers have broader access
    if current_user.role in [UserRole.ADMIN, UserRole.TEACHER]:
        return current_user
    
    try:
        if membership_type == "class":
            # Check if user is enrolled in class
            enrollment = await database_service.get_enrollment_by_user_and_class(
                str(current_user.id), resource_id
            )
            if enrollment:
                return current_user
        
        elif membership_type == "course":
            # Check if user is enrolled in course
            enrollment = await database_service.get_enrollment_by_user_and_course(
                str(current_user.id), resource_id
            )
            if enrollment:
                return current_user
        
        # Add more membership types as needed
        
    except Exception:
        pass
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"Access denied. You don't have access to this {membership_type}"
    )


# Convenience dependencies for common roles
require_admin = require_role(UserRole.ADMIN)
require_teacher = require_role(UserRole.TEACHER, UserRole.ADMIN)
require_student = require_role(UserRole.STUDENT, UserRole.TEACHER, UserRole.ADMIN)
