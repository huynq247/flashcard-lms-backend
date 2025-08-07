from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId
from enum import Enum
from app.utils.objectid import PyObjectId

class AchievementType(str, Enum):
    STREAK = "streak"
    MASTERY = "mastery"
    COMPLETION = "completion"
    SPEED = "speed"
    CONSISTENCY = "consistency"
    MILESTONE = "milestone"

class AchievementCategory(str, Enum):
    STUDY = "study"
    SOCIAL = "social"
    PROGRESS = "progress"
    SPECIAL = "special"

class AchievementRarity(str, Enum):
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

class AchievementModel(BaseModel):
    """Achievement model for gamification system"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True
    )
    
    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")
    user_id: PyObjectId = Field(..., description="Reference to users._id")
    
    # Achievement Classification
    achievement_type: AchievementType = Field(..., description="Type of achievement")
    title: str = Field(..., min_length=1, max_length=100, description="Achievement title")
    description: str = Field(..., min_length=1, max_length=500, description="Achievement description")
    category: AchievementCategory = Field(..., description="Achievement category")
    
    # Achievement Data
    points_awarded: int = Field(..., ge=1, le=10000, description="Points awarded for achievement")
    badge_icon: Optional[str] = Field(None, description="Badge icon identifier")
    rarity: AchievementRarity = Field(default=AchievementRarity.COMMON, description="Achievement rarity")
    earned_date: datetime = Field(default_factory=datetime.utcnow, description="Date achievement was earned")
    
    # Progress Data (flexible structure for different achievement types)
    progress_data: Optional[Dict[str, Any]] = Field(None, description="Additional achievement data")
    
    # Related Objects (for context)
    related_class_id: Optional[PyObjectId] = Field(None, description="Reference to classes._id")
    related_course_id: Optional[PyObjectId] = Field(None, description="Reference to courses._id")
    related_lesson_id: Optional[PyObjectId] = Field(None, description="Reference to lessons._id")
    related_deck_id: Optional[PyObjectId] = Field(None, description="Reference to decks._id")
    
    # Meta
    is_visible: bool = Field(default=True, description="Whether achievement is visible to user")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AchievementTemplate(BaseModel):
    """Template for predefined achievements"""
    template_id: str = Field(..., description="Unique template identifier")
    achievement_type: AchievementType
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    category: AchievementCategory
    points_awarded: int = Field(..., ge=1, le=10000)
    badge_icon: Optional[str] = None
    rarity: AchievementRarity = AchievementRarity.COMMON
    requirements: Dict[str, Any] = Field(..., description="Achievement requirements")

class AchievementCreate(BaseModel):
    """Schema for creating achievements"""
    user_id: PyObjectId
    achievement_type: AchievementType
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    category: AchievementCategory
    points_awarded: int = Field(..., ge=1, le=10000)
    badge_icon: Optional[str] = None
    rarity: AchievementRarity = AchievementRarity.COMMON
    progress_data: Optional[Dict[str, Any]] = None
    related_class_id: Optional[PyObjectId] = None
    related_course_id: Optional[PyObjectId] = None
    related_lesson_id: Optional[PyObjectId] = None
    related_deck_id: Optional[PyObjectId] = None

class AchievementUpdate(BaseModel):
    """Schema for updating achievements"""
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    progress_data: Optional[Dict[str, Any]] = None
    is_visible: Optional[bool] = None

class AchievementResponse(BaseModel):
    """Schema for achievement responses"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )
    
    id: PyObjectId = Field(alias="_id")
    user_id: PyObjectId
    achievement_type: AchievementType
    title: str
    description: str
    category: AchievementCategory
    points_awarded: int
    badge_icon: Optional[str] = None
    rarity: AchievementRarity
    earned_date: datetime
    progress_data: Optional[Dict[str, Any]] = None
    related_class_id: Optional[PyObjectId] = None
    related_course_id: Optional[PyObjectId] = None
    related_lesson_id: Optional[PyObjectId] = None
    related_deck_id: Optional[PyObjectId] = None
    is_visible: bool
    created_at: datetime
    
    @classmethod
    def from_orm(cls, achievement: AchievementModel):
        """Create AchievementResponse from AchievementModel"""
        return cls(
            _id=achievement.id,
            user_id=achievement.user_id,
            achievement_type=achievement.achievement_type,
            title=achievement.title,
            description=achievement.description,
            category=achievement.category,
            points_awarded=achievement.points_awarded,
            badge_icon=achievement.badge_icon,
            rarity=achievement.rarity,
            earned_date=achievement.earned_date,
            progress_data=achievement.progress_data,
            related_class_id=achievement.related_class_id,
            related_course_id=achievement.related_course_id,
            related_lesson_id=achievement.related_lesson_id,
            related_deck_id=achievement.related_deck_id,
            is_visible=achievement.is_visible,
            created_at=achievement.created_at
        )

# Predefined Achievement Templates
ACHIEVEMENT_TEMPLATES = [
    AchievementTemplate(
        template_id="first_deck_created",
        achievement_type=AchievementType.MILESTONE,
        title="Deck Creator",
        description="Created your first flashcard deck",
        category=AchievementCategory.PROGRESS,
        points_awarded=50,
        badge_icon="deck_create",
        rarity=AchievementRarity.COMMON,
        requirements={"decks_created": 1}
    ),
    AchievementTemplate(
        template_id="study_streak_7",
        achievement_type=AchievementType.STREAK,
        title="Week Warrior",
        description="Studied for 7 consecutive days",
        category=AchievementCategory.STUDY,
        points_awarded=150,
        badge_icon="streak_7",
        rarity=AchievementRarity.RARE,
        requirements={"consecutive_days": 7}
    ),
    AchievementTemplate(
        template_id="perfect_accuracy",
        achievement_type=AchievementType.MASTERY,
        title="Perfectionist",
        description="Achieved 100% accuracy in a study session",
        category=AchievementCategory.STUDY,
        points_awarded=100,
        badge_icon="perfect",
        rarity=AchievementRarity.EPIC,
        requirements={"session_accuracy": 1.0, "min_cards": 10}
    ),
    AchievementTemplate(
        template_id="speed_demon",
        achievement_type=AchievementType.SPEED,
        title="Speed Demon",
        description="Completed 50 cards in under 5 minutes",
        category=AchievementCategory.STUDY,
        points_awarded=200,
        badge_icon="speed",
        rarity=AchievementRarity.EPIC,
        requirements={"cards_completed": 50, "max_time": 300}
    ),
    AchievementTemplate(
        template_id="course_completion",
        achievement_type=AchievementType.COMPLETION,
        title="Course Graduate",
        description="Completed your first course",
        category=AchievementCategory.PROGRESS,
        points_awarded=300,
        badge_icon="graduation",
        rarity=AchievementRarity.RARE,
        requirements={"courses_completed": 1}
    )
]
