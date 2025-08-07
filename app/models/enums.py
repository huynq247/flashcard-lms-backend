"""
Enums for authentication and authorization system.
"""
from enum import Enum


class UserRole(str, Enum):
    """User role hierarchy for RBAC system."""
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class Permission(str, Enum):
    """Granular permissions for resources."""
    # User permissions
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    
    # Class permissions
    CLASS_CREATE = "class:create"
    CLASS_READ = "class:read"
    CLASS_UPDATE = "class:update"
    CLASS_DELETE = "class:delete"
    
    # Course permissions
    COURSE_CREATE = "course:create"
    COURSE_READ = "course:read"
    COURSE_UPDATE = "course:update"
    COURSE_DELETE = "course:delete"
    
    # Deck permissions
    DECK_CREATE = "deck:create"
    DECK_READ = "deck:read"
    DECK_UPDATE = "deck:update"
    DECK_DELETE = "deck:delete"
    
    # Study permissions
    STUDY_ALL = "study:all"
    STUDY_READ = "study:read"
    
    # Progress permissions
    PROGRESS_READ = "progress:read"
    PROGRESS_UPDATE = "progress:update"
    
    # Profile permissions
    PROFILE_UPDATE = "profile:update"
    
    # Student management
    STUDENT_MANAGE = "student:manage"
    
    # Assignment permissions
    ASSIGNMENT_CREATE = "assignment:create"
    ASSIGNMENT_READ = "assignment:read"
    ASSIGNMENT_UPDATE = "assignment:update"
    ASSIGNMENT_DELETE = "assignment:delete"
    
    # System permissions
    SYSTEM_MANAGE = "system:manage"


class DeckPrivacyLevel(str, Enum):
    """5-level deck privacy system."""
    PRIVATE = "private"                    # Owner only
    CLASS_ASSIGNED = "class-assigned"      # Assigned to specific class
    COURSE_ASSIGNED = "course-assigned"    # Assigned to specific course  
    LESSON_ASSIGNED = "lesson-assigned"    # Assigned to specific lesson
    PUBLIC = "public"                      # Everyone can access


class TokenType(str, Enum):
    """JWT token types."""
    ACCESS = "access"
    REFRESH = "refresh"
    PASSWORD_RESET = "password_reset"
    EMAIL_VERIFICATION = "email_verification"
    API_KEY = "api_key"


# Permission Matrix - Role-based permissions
ROLE_PERMISSIONS = {
    UserRole.ADMIN: [
        Permission.USER_CREATE, Permission.USER_READ, Permission.USER_UPDATE, Permission.USER_DELETE,
        Permission.CLASS_CREATE, Permission.CLASS_READ, Permission.CLASS_UPDATE, Permission.CLASS_DELETE,
        Permission.COURSE_CREATE, Permission.COURSE_READ, Permission.COURSE_UPDATE, Permission.COURSE_DELETE,
        Permission.DECK_CREATE, Permission.DECK_READ, Permission.DECK_UPDATE, Permission.DECK_DELETE,
        Permission.STUDY_ALL, Permission.PROGRESS_READ, Permission.PROGRESS_UPDATE,
        Permission.ASSIGNMENT_CREATE, Permission.ASSIGNMENT_READ, Permission.ASSIGNMENT_UPDATE, Permission.ASSIGNMENT_DELETE,
        Permission.SYSTEM_MANAGE
    ],
    UserRole.TEACHER: [
        Permission.USER_READ,  # Can read student profiles
        Permission.CLASS_CREATE, Permission.CLASS_READ, Permission.CLASS_UPDATE,
        Permission.COURSE_CREATE, Permission.COURSE_READ, Permission.COURSE_UPDATE, 
        Permission.DECK_CREATE, Permission.DECK_READ, Permission.DECK_UPDATE,
        Permission.STUDY_READ, Permission.PROGRESS_READ,
        Permission.STUDENT_MANAGE, Permission.ASSIGNMENT_CREATE, Permission.ASSIGNMENT_READ, Permission.ASSIGNMENT_UPDATE,
        Permission.PROFILE_UPDATE
    ],
    UserRole.STUDENT: [
        Permission.DECK_READ, Permission.STUDY_ALL, Permission.PROGRESS_READ,
        Permission.ASSIGNMENT_READ, Permission.PROFILE_UPDATE
    ]
}
