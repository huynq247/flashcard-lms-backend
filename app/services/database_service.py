"""
Real database service for production use with MongoDB.
"""
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError

from app.models.user import UserModel
from app.models.deck import DeckModel
from app.models.classroom import ClassModel
from app.models.enums import UserRole, DeckPrivacyLevel
from app.core.config import settings


class RealDatabaseService:
    """Real database service for production use."""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
    
    async def connect_to_database(self):
        """Connect to MongoDB database."""
        try:
            self.client = AsyncIOMotorClient(settings.MONGODB_URL)
            self.database = self.client[settings.DATABASE_NAME]
            
            # Test connection
            await self.client.admin.command('ping')
            print(f"✅ Connected to MongoDB: {settings.DATABASE_NAME}")
            
            # Create indexes
            await self._create_indexes()
            
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    async def close_database_connection(self):
        """Close database connection."""
        if self.client:
            self.client.close()
            print("🔐 Disconnected from MongoDB")
    
    async def _create_indexes(self):
        """Create database indexes for performance."""
        try:
            # User indexes
            await self.database.users.create_index("email", unique=True)
            await self.database.users.create_index("username", unique=True)
            
            # Deck indexes
            await self.database.decks.create_index("owner_id")
            await self.database.decks.create_index("privacy_level")
            await self.database.decks.create_index([("title", "text"), ("description", "text")])
            
            # Class indexes
            await self.database.classes.create_index("teacher_id")
            await self.database.classes.create_index("class_code", unique=True)
            
            # Enrollment indexes
            await self.database.enrollments.create_index([("student_id", 1), ("class_id", 1)], unique=True)
            
            print("✅ Database indexes created successfully")
            
        except Exception as e:
            print(f"⚠️ Error creating indexes: {e}")
    
    # User operations
    async def get_user_by_id(self, user_id: str) -> Optional[UserModel]:
        """Get user by ID."""
        user_doc = await self.database.users.find_one({"id": user_id})
        return UserModel(**user_doc) if user_doc else None
    
    async def get_user_by_email(self, email: str) -> Optional[UserModel]:
        """Get user by email."""
        user_doc = await self.database.users.find_one({"email": email})
        return UserModel(**user_doc) if user_doc else None
    
    async def get_user_by_username(self, username: str) -> Optional[UserModel]:
        """Get user by username."""
        user_doc = await self.database.users.find_one({"username": username})
        return UserModel(**user_doc) if user_doc else None
    
    async def create_user(self, user_data: Dict[str, Any]) -> UserModel:
        """Create a new user."""
        try:
            user = UserModel(**user_data)
            await self.database.users.insert_one(user.dict())
            return user
        except DuplicateKeyError as e:
            if "email" in str(e):
                raise ValueError("Email already registered")
            elif "username" in str(e):
                raise ValueError("Username already taken")
            else:
                raise ValueError("User already exists")
    
    async def update_user_password(self, user_id: str, new_password_hash: str) -> None:
        """Update user password."""
        await self.database.users.update_one(
            {"id": user_id},
            {
                "$set": {
                    "hashed_password": new_password_hash,
                    "updated_at": datetime.utcnow()
                }
            }
        )
    
    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Optional[UserModel]:
        """Update user information."""
        update_data["updated_at"] = datetime.utcnow()
        
        result = await self.database.users.update_one(
            {"id": user_id},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            return await self.get_user_by_id(user_id)
        return None
    
    # Deck operations
    async def get_deck(self, deck_id: str) -> Optional[DeckModel]:
        """Get deck by ID."""
        deck_doc = await self.database.decks.find_one({"id": deck_id})
        return DeckModel(**deck_doc) if deck_doc else None
    
    async def create_deck(self, deck_data: Dict[str, Any]) -> DeckModel:
        """Create a new deck."""
        deck = DeckModel(**deck_data)
        await self.database.decks.insert_one(deck.dict())
        return deck
    
    async def get_user_decks(self, user_id: str, privacy_level: Optional[DeckPrivacyLevel] = None) -> List[DeckModel]:
        """Get user's decks."""
        filter_query = {"owner_id": user_id}
        if privacy_level:
            filter_query["privacy_level"] = privacy_level.value
        
        deck_docs = await self.database.decks.find(filter_query).to_list(length=None)
        return [DeckModel(**doc) for doc in deck_docs]
    
    # Class operations
    async def get_class(self, class_id: str) -> Optional[ClassModel]:
        """Get class by ID."""
        class_doc = await self.database.classes.find_one({"id": class_id})
        return ClassModel(**class_doc) if class_doc else None
    
    async def is_student_in_class(self, student_id: str, class_id: str) -> bool:
        """Check if student is enrolled in class."""
        enrollment = await self.database.enrollments.find_one({
            "student_id": student_id,
            "class_id": class_id,
            "is_active": True
        })
        return enrollment is not None
    
    async def get_class_assignments(self, student_id: str) -> List[str]:
        """Get class IDs where student is enrolled."""
        enrollments = await self.database.enrollments.find({
            "student_id": student_id,
            "is_active": True
        }).to_list(length=None)
        
        return [enrollment["class_id"] for enrollment in enrollments]
    
    async def get_class_students(self, class_id: str) -> List[str]:
        """Get student IDs enrolled in class."""
        enrollments = await self.database.enrollments.find({
            "class_id": class_id,
            "is_active": True
        }).to_list(length=None)
        
        return [enrollment["student_id"] for enrollment in enrollments]


# Create singleton instance for production
database_service = RealDatabaseService()
