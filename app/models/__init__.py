"""
Model initialization and exports.
"""
from app.models.user import (
    UserModel,
    UserCreateRequest,
    UserResponse,
    UserUpdateRequest,
    PasswordChangeRequest,
    AdminPasswordResetRequest,
    UserLoginRequest,
    UserLoginResponse,
    TokenRefreshRequest,
    LogoutRequest,
    LogoutResponse,
    UserListResponse,
    UserRegistrationResponse
)

from app.models.deck import (
    DeckModel,
    DeckCreateRequest,
    DeckUpdateRequest,
    DeckResponse,
    DeckListResponse,
    CardModel,
    CardCreateRequest,
    CardUpdateRequest,
    CardResponse,
    CardListResponse
)

from app.models.classroom import (
    ClassModel,
    ClassCreateRequest,
    ClassUpdateRequest,
    ClassResponse,
    ClassListResponse,
    ClassEnrollmentModel,
    ClassJoinRequest,
    ClassJoinResponse
)

from app.models.enums import (
    UserRole,
    DeckPrivacyLevel,
    TokenType
)

__all__ = [
    # User models
    "UserModel",
    "UserCreateRequest", 
    "UserResponse",
    "UserUpdateRequest",
    "PasswordChangeRequest",
    "AdminPasswordResetRequest",
    "UserLoginRequest",
    "UserLoginResponse",
    "TokenRefreshRequest",
    "LogoutRequest",
    "LogoutResponse",
    "UserListResponse",
    "UserRegistrationResponse",
    
    # Deck models
    "DeckModel",
    "DeckCreateRequest",
    "DeckUpdateRequest", 
    "DeckResponse",
    "DeckListResponse",
    "CardModel",
    "CardCreateRequest",
    "CardUpdateRequest",
    "CardResponse",
    "CardListResponse",
    
    # Class models
    "ClassModel",
    "ClassCreateRequest",
    "ClassUpdateRequest",
    "ClassResponse", 
    "ClassListResponse",
    "ClassEnrollmentModel",
    "ClassJoinRequest",
    "ClassJoinResponse",
    
    # Enums
    "UserRole",
    "DeckPrivacyLevel",
    "TokenType"
]
