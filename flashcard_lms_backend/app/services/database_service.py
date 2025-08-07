from motor.motor_asyncio import AsyncIOMotorDatabase
from app.utils.database import get_database
from app.models.user import UserModel, UserCreate, UserUpdate
from app.models.deck import DeckModel, DeckCreate, DeckUpdate
from app.models.flashcard import FlashcardModel, FlashcardCreate, FlashcardUpdate
from app.models.class_model import ClassModel, ClassCreate, ClassUpdate
from app.models.course import CourseModel, CourseCreate, CourseUpdate
from app.models.lesson import LessonModel, LessonCreate, LessonUpdate
from app.models.study_session import StudySessionModel, StudySessionCreate, StudySessionUpdate
from app.models.user_progress import UserProgressModel, UserProgressCreate, UserProgressUpdate
from app.models.achievement import AchievementModel, AchievementCreate, AchievementUpdate
from app.models.notification import NotificationModel, NotificationCreate, NotificationUpdate
from app.models.deck_assignment import DeckAssignmentModel, DeckAssignmentCreate, DeckAssignmentUpdate
from app.models.enrollment import EnrollmentModel, EnrollmentCreate, EnrollmentUpdate
from bson import ObjectId
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    """Service for database operations"""
    
    def __init__(self):
        self.db: Optional[AsyncIOMotorDatabase] = None
    
    async def initialize(self):
        """Initialize database connection"""
        self.db = await get_database()
        await self._create_indexes()
        logger.info("Database service initialized")
    
    async def _create_indexes(self):
        """Create all required indexes for performance (Decision #16: Standard Performance)"""
        if not self.db:
            return
        
        try:
            # User indexes
            await self.db.users.create_index("email", unique=True)
            await self.db.users.create_index("username", unique=True)
            await self.db.users.create_index("role")
            await self.db.users.create_index("is_active")
            await self.db.users.create_index([("role", 1), ("is_active", 1)])
            await self.db.users.create_index([("email_verified", 1), ("is_active", 1)])
            
            # Deck indexes
            await self.db.decks.create_index("owner_id")
            await self.db.decks.create_index("privacy_level")
            await self.db.decks.create_index("category")
            await self.db.decks.create_index([("created_at", -1)])
            await self.db.decks.create_index([("owner_id", 1), ("privacy_level", 1)])
            await self.db.decks.create_index([("category", 1), ("difficulty_level", 1)])
            await self.db.decks.create_index([("privacy_level", 1), ("is_active", 1)])
            
            # Flashcard indexes
            await self.db.flashcards.create_index("deck_id")
            await self.db.flashcards.create_index("sm2_data.next_review")
            await self.db.flashcards.create_index([("deck_id", 1), ("sm2_data.next_review", 1)])
            await self.db.flashcards.create_index([("deck_id", 1), ("created_at", 1)])
            await self.db.flashcards.create_index([("deck_id", 1), ("order_index", 1)])
            
            # Class indexes
            await self.db.classes.create_index("teacher_id")
            await self.db.classes.create_index([("teacher_id", 1), ("is_active", 1)])
            await self.db.classes.create_index("student_ids")
            await self.db.classes.create_index("class_code", unique=True, sparse=True)
            
            # Course indexes
            await self.db.courses.create_index("creator_id")
            await self.db.courses.create_index([("is_public", 1), ("category", 1)])
            await self.db.courses.create_index("lesson_ids")
            await self.db.courses.create_index([("category", 1), ("difficulty_level", 1)])
            
            # Lesson indexes
            await self.db.lessons.create_index("course_id")
            await self.db.lessons.create_index([("course_id", 1), ("order_index", 1)])
            await self.db.lessons.create_index("deck_ids")
            await self.db.lessons.create_index([("course_id", 1), ("is_published", 1)])
            
            # Study session indexes
            await self.db.study_sessions.create_index("user_id")
            await self.db.study_sessions.create_index([("user_id", 1), ("deck_id", 1)])
            await self.db.study_sessions.create_index([("user_id", 1), ("started_at", -1)])
            await self.db.study_sessions.create_index([("deck_id", 1), ("started_at", -1)])
            await self.db.study_sessions.create_index([("user_id", 1), ("status", 1)])
            
            # User progress indexes
            await self.db.user_progress.create_index("user_id")
            await self.db.user_progress.create_index([("user_id", 1), ("progress_type", 1)])
            await self.db.user_progress.create_index([("user_id", 1), ("class_id", 1)])
            await self.db.user_progress.create_index([("user_id", 1), ("course_id", 1)])
            await self.db.user_progress.create_index([("user_id", 1), ("lesson_id", 1)])
            await self.db.user_progress.create_index([("user_id", 1), ("deck_id", 1)])
            
            # Achievement indexes
            await self.db.achievements.create_index("user_id")
            await self.db.achievements.create_index([("user_id", 1), ("achievement_type", 1)])
            await self.db.achievements.create_index([("user_id", 1), ("earned_date", -1)])
            await self.db.achievements.create_index("category")
            
            # Notification indexes
            await self.db.notifications.create_index("user_id")
            await self.db.notifications.create_index([("user_id", 1), ("is_read", 1)])
            await self.db.notifications.create_index([("user_id", 1), ("created_at", -1)])
            await self.db.notifications.create_index([("expires_at", 1)], expireAfterSeconds=0)
            
            # Deck assignment indexes
            await self.db.deck_assignments.create_index("deck_id")
            await self.db.deck_assignments.create_index("assigned_by")
            await self.db.deck_assignments.create_index([("class_id", 1), ("status", 1)])
            await self.db.deck_assignments.create_index([("course_id", 1), ("status", 1)])
            await self.db.deck_assignments.create_index([("lesson_id", 1), ("status", 1)])
            await self.db.deck_assignments.create_index([("student_id", 1), ("status", 1)])
            await self.db.deck_assignments.create_index([("due_date", 1), ("status", 1)])
            
            # Enrollment indexes
            await self.db.enrollments.create_index("user_id")
            await self.db.enrollments.create_index([("user_id", 1), ("enrollment_type", 1)])
            await self.db.enrollments.create_index([("user_id", 1), ("class_id", 1)])
            await self.db.enrollments.create_index([("user_id", 1), ("course_id", 1)])
            await self.db.enrollments.create_index([("user_id", 1), ("lesson_id", 1)])
            await self.db.enrollments.create_index([("class_id", 1), ("status", 1)])
            await self.db.enrollments.create_index([("course_id", 1), ("status", 1)])
            await self.db.enrollments.create_index([("lesson_id", 1), ("status", 1)])
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    # User operations
    async def create_user(self, user_data: UserCreate) -> UserModel:
        """Create a new user"""
        user_dict = user_data.dict()
        user_dict["created_at"] = user_dict["updated_at"] = datetime.utcnow()
        
        result = await self.db.users.insert_one(user_dict)
        user_dict["_id"] = result.inserted_id
        
        return UserModel(**user_dict)
    
    async def get_user_by_id(self, user_id: ObjectId) -> Optional[UserModel]:
        """Get user by ID"""
        user_data = await self.db.users.find_one({"_id": user_id})
        return UserModel(**user_data) if user_data else None
    
    async def get_user_by_email(self, email: str) -> Optional[UserModel]:
        """Get user by email"""
        user_data = await self.db.users.find_one({"email": email})
        return UserModel(**user_data) if user_data else None
    
    async def get_user_by_username(self, username: str) -> Optional[UserModel]:
        """Get user by username"""
        user_data = await self.db.users.find_one({"username": username})
        return UserModel(**user_data) if user_data else None
    
    async def update_user(self, user_id: ObjectId, user_data: UserUpdate) -> Optional[UserModel]:
        """Update user"""
        update_data = user_data.dict(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            await self.db.users.update_one(
                {"_id": user_id},
                {"$set": update_data}
            )
        return await self.get_user_by_id(user_id)
    
    # Deck operations
    async def create_deck(self, deck_data: DeckCreate, owner_id: ObjectId) -> DeckModel:
        """Create a new deck"""
        deck_dict = deck_data.dict()
        deck_dict["owner_id"] = owner_id
        deck_dict["created_at"] = deck_dict["updated_at"] = datetime.utcnow()
        
        result = await self.db.decks.insert_one(deck_dict)
        deck_dict["_id"] = result.inserted_id
        
        return DeckModel(**deck_dict)
    
    async def get_deck_by_id(self, deck_id: ObjectId) -> Optional[DeckModel]:
        """Get deck by ID"""
        deck_data = await self.db.decks.find_one({"_id": deck_id})
        return DeckModel(**deck_data) if deck_data else None
    
    async def get_decks_by_owner(self, owner_id: ObjectId, skip: int = 0, limit: int = 20) -> List[DeckModel]:
        """Get decks by owner"""
        cursor = self.db.decks.find({"owner_id": owner_id}).skip(skip).limit(limit)
        decks = []
        async for deck_data in cursor:
            decks.append(DeckModel(**deck_data))
        return decks
    
    async def update_deck(self, deck_id: ObjectId, deck_data: DeckUpdate) -> Optional[DeckModel]:
        """Update deck"""
        update_data = deck_data.dict(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            await self.db.decks.update_one(
                {"_id": deck_id},
                {"$set": update_data}
            )
        return await self.get_deck_by_id(deck_id)
    
    # Flashcard operations
    async def create_flashcard(self, flashcard_data: FlashcardCreate, deck_id: ObjectId) -> FlashcardModel:
        """Create a new flashcard"""
        flashcard_dict = flashcard_data.dict()
        flashcard_dict["deck_id"] = deck_id
        flashcard_dict["created_at"] = flashcard_dict["updated_at"] = datetime.utcnow()
        
        result = await self.db.flashcards.insert_one(flashcard_dict)
        flashcard_dict["_id"] = result.inserted_id
        
        # Update deck card count
        await self.db.decks.update_one(
            {"_id": deck_id},
            {"$inc": {"card_count": 1}}
        )
        
        return FlashcardModel(**flashcard_dict)
    
    async def get_flashcards_by_deck(self, deck_id: ObjectId, skip: int = 0, limit: int = 100) -> List[FlashcardModel]:
        """Get flashcards by deck"""
        cursor = self.db.flashcards.find({"deck_id": deck_id, "is_active": True}).skip(skip).limit(limit)
        flashcards = []
        async for flashcard_data in cursor:
            flashcards.append(FlashcardModel(**flashcard_data))
        return flashcards
    
    async def get_flashcard_by_id(self, flashcard_id: ObjectId) -> Optional[FlashcardModel]:
        """Get flashcard by ID"""
        flashcard_data = await self.db.flashcards.find_one({"_id": flashcard_id})
        return FlashcardModel(**flashcard_data) if flashcard_data else None

# Global database service instance
db_service = DatabaseService()
