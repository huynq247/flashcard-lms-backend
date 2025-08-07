from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId
from enum import Enum
from app.utils.objectid import PyObjectId

class PrivacyLevel(str, Enum):
    """Deck privacy levels (Decision #5: Advanced Privacy)"""
    PRIVATE = "private"
    CLASS_ASSIGNED = "class-assigned"
    COURSE_ASSIGNED = "course-assigned"
    LESSON_ASSIGNED = "lesson-assigned"
    PUBLIC = "public"

class DeckCategory(str, Enum):
    """Predefined deck categories (Decision #7: Predefined Categories)"""
    LANGUAGE = "language"
    SCIENCE = "science"
    MATHEMATICS = "mathematics"
    HISTORY = "history"
    GEOGRAPHY = "geography"
    LITERATURE = "literature"
    COMPUTER_SCIENCE = "computer-science"
    MEDICINE = "medicine"
    BUSINESS = "business"
    ART = "art"
    MUSIC = "music"
    SPORTS = "sports"
    GENERAL_KNOWLEDGE = "general-knowledge"
    OTHER = "other"

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class DeckModel(BaseModel):
    """Deck model with advanced privacy and categories"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True
    )
    
    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    owner_id: PyObjectId = Field(..., description="Reference to users._id")
    
    # Advanced Privacy (Decision #5)
    privacy_level: PrivacyLevel = Field(default=PrivacyLevel.PRIVATE)
    
    # Category System (Decision #7: Predefined)
    category: DeckCategory = Field(..., description="Predefined category")
    tags: List[str] = Field(default_factory=list, description="Custom tags")
    
    difficulty_level: DifficultyLevel = Field(default=DifficultyLevel.BEGINNER)
    card_count: int = Field(default=0, ge=0)
    
    # Multimedia Support (Decision #6)
    supports_multimedia: bool = Field(default=True)
    
    # Meta
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    study_count: int = Field(default=0, ge=0)
    average_rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    
    # Performance tracking
    total_reviews: int = Field(default=0, ge=0)
    completion_rate: float = Field(default=0.0, ge=0.0, le=1.0)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "title": "Spanish Vocabulary - Beginner",
                "description": "Essential Spanish words for beginners",
                "privacy_level": "public",
                "category": "language",
                "tags": ["spanish", "vocabulary", "basic"],
                "difficulty_level": "beginner",
                "supports_multimedia": True
            }
        }

class DeckCreate(BaseModel):
    """Deck creation model"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    privacy_level: PrivacyLevel = Field(default=PrivacyLevel.PRIVATE)
    category: DeckCategory
    tags: List[str] = Field(default_factory=list)
    difficulty_level: DifficultyLevel = Field(default=DifficultyLevel.BEGINNER)
    supports_multimedia: bool = Field(default=True)

class DeckUpdate(BaseModel):
    """Deck update model"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    privacy_level: Optional[PrivacyLevel] = None
    category: Optional[DeckCategory] = None
    tags: Optional[List[str]] = None
    difficulty_level: Optional[DifficultyLevel] = None
    supports_multimedia: Optional[bool] = None

class DeckResponse(BaseModel):
    """Deck response model"""
    id: PyObjectId = Field(alias="_id")
    title: str
    description: Optional[str]
    owner_id: PyObjectId
    privacy_level: PrivacyLevel
    category: DeckCategory
    tags: List[str]
    difficulty_level: DifficultyLevel
    card_count: int
    supports_multimedia: bool
    created_at: datetime
    updated_at: datetime
    study_count: int
    average_rating: Optional[float]
    completion_rate: float

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class DeckStats(BaseModel):
    """Deck statistics model"""
    deck_id: PyObjectId
    total_cards: int
    cards_mastered: int
    average_accuracy: float
    total_study_time: int  # seconds
    last_studied: Optional[datetime]
    study_sessions: int
    completion_percentage: float
