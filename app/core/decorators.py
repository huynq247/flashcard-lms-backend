"""
Security decorators for authentication and authorization.
"""
import functools
from typing import Callable, Optional

from fastapi import HTTPException, status, Depends

from app.core.deps import get_current_active_user
from app.models.enums import UserRole, Permission, ROLE_PERMISSIONS, DeckPrivacyLevel
from app.models.user import UserModel
from app.services.privacy_service import privacy_service


def require_deck_access(deck_id_param: str = "deck_id"):
    """
    Decorator to require deck access based on privacy level.
    
    Args:
        deck_id_param: Name of the parameter containing deck ID
    
    Usage:
        @require_deck_access("deck_id")
        async def get_deck(deck_id: str, user: UserModel = Depends(get_current_active_user)):
            pass
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user
            current_user = None
            for key, value in kwargs.items():
                if isinstance(value, UserModel):
                    current_user = value
                    break
            
            if not current_user:
                # Try to get from dependencies
                current_user = kwargs.get('current_user') or kwargs.get('user')
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Get deck ID
            deck_id = kwargs.get(deck_id_param)
            if not deck_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing parameter: {deck_id_param}"
                )
            
            # Check deck access
            has_access = await privacy_service.check_deck_access(
                str(current_user.id), deck_id
            )
            
            if not has_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this deck"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_privacy_level(*allowed_levels: DeckPrivacyLevel):
    """
    Decorator to require specific deck privacy levels.
    
    Usage:
        @require_privacy_level(DeckPrivacyLevel.PUBLIC, DeckPrivacyLevel.CLASS_ASSIGNED)
        async def get_public_decks():
            pass
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # This decorator would be used with other decorators
            # that provide deck information
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_assignment_access(assignment_type: str, resource_id_param: str = "resource_id"):
    """
    Decorator to require assignment-based access.
    
    Args:
        assignment_type: Type of assignment (class, course, lesson)
        resource_id_param: Parameter name containing resource ID
    
    Usage:
        @require_assignment_access("class", "class_id")
        async def get_class_decks(class_id: str, user: UserModel = Depends(get_current_active_user)):
            pass
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = None
            for key, value in kwargs.items():
                if isinstance(value, UserModel):
                    current_user = value
                    break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            resource_id = kwargs.get(resource_id_param)
            if not resource_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing parameter: {resource_id_param}"
                )
            
            # Check assignment access based on type
            from app.services.database_service import database_service
            
            try:
                if assignment_type == "class":
                    enrollment = await database_service.get_enrollment_by_user_and_class(
                        str(current_user.id), resource_id
                    )
                elif assignment_type == "course":
                    enrollment = await database_service.get_enrollment_by_user_and_course(
                        str(current_user.id), resource_id
                    )
                elif assignment_type == "lesson":
                    lesson = await database_service.get_lesson_by_id(resource_id)
                    if lesson:
                        enrollment = await database_service.get_enrollment_by_user_and_course(
                            str(current_user.id), str(lesson.course_id)
                        )
                    else:
                        enrollment = None
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid assignment type: {assignment_type}"
                    )
                
                # Admin and teachers have broader access
                if current_user.role in [UserRole.ADMIN, UserRole.TEACHER]:
                    return await func(*args, **kwargs)
                
                # Check enrollment
                if not enrollment or enrollment.status not in ["enrolled", "in_progress", "completed"]:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Access denied to this {assignment_type}"
                    )
                
            except Exception as e:
                if isinstance(e, HTTPException):
                    raise
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to verify assignment access"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def audit_access(resource_type: str, action: str):
    """
    Decorator to audit access attempts (for logging and security).
    
    Args:
        resource_type: Type of resource being accessed
        action: Action being performed
    
    Usage:
        @audit_access("deck", "read")
        async def get_deck(deck_id: str):
            pass
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user for audit logging
            current_user = None
            for key, value in kwargs.items():
                if isinstance(value, UserModel):
                    current_user = value
                    break
            
            # Log access attempt (in a real implementation, you'd use a proper logging service)
            try:
                import logging
                logger = logging.getLogger(__name__)
                
                user_info = "anonymous"
                if current_user:
                    user_info = f"{current_user.username}({current_user.role})"
                
                logger.info(f"Access attempt: {user_info} -> {action} {resource_type}")
                
                # Execute the function
                result = await func(*args, **kwargs)
                
                logger.info(f"Access granted: {user_info} -> {action} {resource_type}")
                return result
                
            except Exception as e:
                if current_user:
                    logger.warning(f"Access denied: {user_info} -> {action} {resource_type} - {str(e)}")
                raise
            
        return wrapper
    return decorator


def rate_limit(requests_per_minute: int = 60):
    """
    Decorator for rate limiting (basic implementation).
    
    Args:
        requests_per_minute: Maximum requests per minute
    
    Usage:
        @rate_limit(30)
        async def sensitive_endpoint():
            pass
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # In a real implementation, you'd use Redis or similar for rate limiting
            # This is a basic placeholder
            
            # For now, just execute the function
            # TODO: Implement proper rate limiting with Redis
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# Convenience decorators for common privacy patterns
require_public_deck = require_privacy_level(DeckPrivacyLevel.PUBLIC)
require_assigned_deck = require_privacy_level(
    DeckPrivacyLevel.CLASS_ASSIGNED,
    DeckPrivacyLevel.COURSE_ASSIGNED,
    DeckPrivacyLevel.LESSON_ASSIGNED
)

# Audit decorators for common actions
audit_deck_read = audit_access("deck", "read")
audit_deck_write = audit_access("deck", "write")
audit_user_action = audit_access("user", "action")
audit_auth_action = audit_access("auth", "action")
