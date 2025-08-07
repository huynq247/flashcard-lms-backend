"""
Mock database service for testing purposes.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from unittest.mock import MagicMock

from app.models.user import UserModel
from app.models.deck import DeckModel
from app.models.classroom import ClassModel
from app.models.enums import UserRole, DeckPrivacyLevel


class MockDatabaseService:
    """Mock database service for testing."""
    
    def __init__(self):
        self._users: Dict[str, UserModel] = {}
        self._decks: Dict[str, DeckModel] = {}
        self._classes: Dict[str, ClassModel] = {}
        self._enrollments: List[Dict[str, str]] = []
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserModel]:
        """Get user by ID."""
        return self._users.get(user_id)
    
    async def get_user_by_email(self, email: str) -> Optional[UserModel]:
        """Get user by email."""
        for user in self._users.values():
            if user.email == email:
                return user
        return None
    
    async def get_user_by_username(self, username: str) -> Optional[UserModel]:
        """Get user by username."""
        for user in self._users.values():
            if user.username == username:
                return user
        return None
    
    async def create_user(self, user_data: Dict[str, Any]) -> UserModel:
        """Create a new user."""
        user = UserModel(**user_data)
        self._users[user.id] = user
        return user
    
    async def update_user_password(self, user_id: str, new_password_hash: str) -> None:
        """Update user password."""
        if user_id in self._users:
            self._users[user_id].hashed_password = new_password_hash
    
    async def get_deck(self, deck_id: str) -> Optional[DeckModel]:
        """Get deck by ID."""
        return self._decks.get(deck_id)
    
    async def get_class(self, class_id: str) -> Optional[ClassModel]:
        """Get class by ID."""
        return self._classes.get(class_id)
    
    async def is_student_in_class(self, student_id: str, class_id: str) -> bool:
        """Check if student is enrolled in class."""
        for enrollment in self._enrollments:
            if enrollment["student_id"] == student_id and enrollment["class_id"] == class_id:
                return True
        return False
    
    async def get_user_decks(self, user_id: str, privacy_level: Optional[DeckPrivacyLevel] = None) -> List[DeckModel]:
        """Get user's decks."""
        decks = []
        for deck in self._decks.values():
            if deck.owner_id == user_id:
                if privacy_level is None or deck.privacy_level == privacy_level:
                    decks.append(deck)
        return decks
    
    async def get_class_assignments(self, student_id: str) -> List[str]:
        """Get class IDs where student is enrolled."""
        class_ids = []
        for enrollment in self._enrollments:
            if enrollment["student_id"] == student_id:
                class_ids.append(enrollment["class_id"])
        return class_ids


# Create singleton instance
database_service = MockDatabaseService()
