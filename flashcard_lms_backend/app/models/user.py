from datetime import datetime, time
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from bson import ObjectId
from enum import Enum
from app.utils.objectid import PyObjectId

class UserRole(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

class LearningPreferences(BaseModel):
    """Learning preferences for extended profile"""
    preferred_study_time: Optional[str] = None  # morning, afternoon, evening
    session_duration: Optional[int] = None  # minutes
    daily_goal: Optional[int] = None  # cards per day
    spaced_repetition: bool = True
    auto_advance: bool = False
    card_order: str = "random"  # random, created, difficulty

class StudySchedule(BaseModel):
    """Weekly study schedule"""
    monday: Optional[time] = None
    tuesday: Optional[time] = None
    wednesday: Optional[time] = None
    thursday: Optional[time] = None
    friday: Optional[time] = None
    saturday: Optional[time] = None
    sunday: Optional[time] = None
    timezone: str = "UTC"

class UserModel(BaseModel):
    """User model with extended profile (Decision #4)"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True
    )
    
    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")
    email: EmailStr = Field(..., description="Unique email address")
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    password_hash: str = Field(..., description="Hashed password")
    role: UserRole = Field(default=UserRole.STUDENT, description="User role")
    
    # Extended Profile Data (Decision #4)
    full_name: str = Field(..., min_length=2, max_length=100)
    avatar_url: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=500)
    learning_preferences: Optional[LearningPreferences] = None
    learning_goals: List[str] = Field(default_factory=list)
    study_schedule: Optional[StudySchedule] = None
    achievements: List[PyObjectId] = Field(default_factory=list)
    
    # Email Verification (Decision #2: Optional)
    email_verified: bool = Field(default=False)
    
    # Meta
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Stats
    total_study_time: int = Field(default=0, description="Total study time in seconds")
    cards_studied: int = Field(default=0)
    study_streak: int = Field(default=0)
    last_study_date: Optional[datetime] = None

class UserCreate(BaseModel):
    """Schema for creating a new user"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password_hash: str
    full_name: str = Field(..., min_length=2, max_length=100)
    role: UserRole = UserRole.STUDENT
    bio: Optional[str] = Field(None, max_length=500)
    learning_preferences: Optional[LearningPreferences] = None
    study_schedule: Optional[StudySchedule] = None

class UserUpdate(BaseModel):
    """Schema for updating user data"""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None
    learning_preferences: Optional[LearningPreferences] = None
    learning_goals: Optional[List[str]] = None
    study_schedule: Optional[StudySchedule] = None
    email_verified: Optional[bool] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    """Schema for user responses (without sensitive data)"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )
    
    id: PyObjectId = Field(alias="_id")
    email: EmailStr
    username: str
    role: UserRole
    full_name: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    learning_preferences: Optional[LearningPreferences] = None
    learning_goals: List[str] = Field(default_factory=list)
    study_schedule: Optional[StudySchedule] = None
    achievements: List[PyObjectId] = Field(default_factory=list)
    email_verified: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    total_study_time: int
    cards_studied: int
    study_streak: int
    last_study_date: Optional[datetime] = None
    
    @classmethod
    def from_orm(cls, user: UserModel):
        """Create UserResponse from UserModel"""
        return cls(
            _id=user.id,
            email=user.email,
            username=user.username,
            role=user.role,
            full_name=user.full_name,
            avatar_url=user.avatar_url,
            bio=user.bio,
            learning_preferences=user.learning_preferences,
            learning_goals=user.learning_goals,
            study_schedule=user.study_schedule,
            achievements=user.achievements,
            email_verified=user.email_verified,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            total_study_time=user.total_study_time,
            cards_studied=user.cards_studied,
            study_streak=user.study_streak,
            last_study_date=user.last_study_date
        )
