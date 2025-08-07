from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId
from enum import Enum
from app.utils.objectid import PyObjectId

class ProgressType(str, Enum):
    CLASS = "class"
    COURSE = "course"
    LESSON = "lesson"
    DECK = "deck"

class DailyProgress(BaseModel):
    """Daily progress tracking"""
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    cards_studied: int = Field(default=0, ge=0)
    time_spent: int = Field(default=0, ge=0, description="Time in seconds")
    accuracy_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    sessions_completed: int = Field(default=0, ge=0)

class WeeklyProgress(BaseModel):
    """Weekly aggregated progress"""
    week_start: str = Field(..., description="Week start date in YYYY-MM-DD format")
    total_cards: int = Field(default=0, ge=0)
    total_time: int = Field(default=0, ge=0, description="Time in seconds")
    average_accuracy: Optional[float] = Field(None, ge=0.0, le=1.0)
    sessions_count: int = Field(default=0, ge=0)
    days_active: int = Field(default=0, ge=0, le=7)

class UserProgressModel(BaseModel):
    """User progress collection with multi-level tracking (Decision #12: Standard Analytics)"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True
    )
    
    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")
    user_id: PyObjectId = Field(..., description="Reference to users._id")
    
    # Multi-level Progress Tracking
    class_id: Optional[PyObjectId] = Field(None, description="Reference to classes._id")
    course_id: Optional[PyObjectId] = Field(None, description="Reference to courses._id")
    lesson_id: Optional[PyObjectId] = Field(None, description="Reference to lessons._id")
    deck_id: Optional[PyObjectId] = Field(None, description="Reference to decks._id")
    
    progress_type: ProgressType = Field(..., description="Type of progress tracking")
    
    # Standard Analytics (Decision #12)
    completion_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    accuracy_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    time_spent: int = Field(default=0, ge=0, description="Total time in seconds")
    cards_mastered: int = Field(default=0, ge=0)
    current_streak: int = Field(default=0, ge=0)
    
    # Charts Data
    daily_progress: List[DailyProgress] = Field(default_factory=list)
    weekly_progress: List[WeeklyProgress] = Field(default_factory=list)
    
    # Additional Analytics
    total_sessions: int = Field(default=0, ge=0)
    average_session_time: Optional[float] = Field(None, ge=0.0)
    best_streak: int = Field(default=0, ge=0)
    last_activity: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserProgressCreate(BaseModel):
    """Schema for creating user progress"""
    user_id: PyObjectId
    progress_type: ProgressType
    class_id: Optional[PyObjectId] = None
    course_id: Optional[PyObjectId] = None
    lesson_id: Optional[PyObjectId] = None
    deck_id: Optional[PyObjectId] = None

class UserProgressUpdate(BaseModel):
    """Schema for updating user progress"""
    completion_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    accuracy_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    time_spent: Optional[int] = Field(None, ge=0)
    cards_mastered: Optional[int] = Field(None, ge=0)
    current_streak: Optional[int] = Field(None, ge=0)
    daily_progress: Optional[List[DailyProgress]] = None
    weekly_progress: Optional[List[WeeklyProgress]] = None
    total_sessions: Optional[int] = Field(None, ge=0)
    average_session_time: Optional[float] = Field(None, ge=0.0)
    best_streak: Optional[int] = Field(None, ge=0)
    last_activity: Optional[datetime] = None

class UserProgressResponse(BaseModel):
    """Schema for user progress responses"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )
    
    id: PyObjectId = Field(alias="_id")
    user_id: PyObjectId
    progress_type: ProgressType
    class_id: Optional[PyObjectId] = None
    course_id: Optional[PyObjectId] = None
    lesson_id: Optional[PyObjectId] = None
    deck_id: Optional[PyObjectId] = None
    completion_percentage: float
    accuracy_rate: Optional[float] = None
    time_spent: int
    cards_mastered: int
    current_streak: int
    daily_progress: List[DailyProgress]
    weekly_progress: List[WeeklyProgress]
    total_sessions: int
    average_session_time: Optional[float] = None
    best_streak: int
    last_activity: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_orm(cls, progress: UserProgressModel):
        """Create UserProgressResponse from UserProgressModel"""
        return cls(
            _id=progress.id,
            user_id=progress.user_id,
            progress_type=progress.progress_type,
            class_id=progress.class_id,
            course_id=progress.course_id,
            lesson_id=progress.lesson_id,
            deck_id=progress.deck_id,
            completion_percentage=progress.completion_percentage,
            accuracy_rate=progress.accuracy_rate,
            time_spent=progress.time_spent,
            cards_mastered=progress.cards_mastered,
            current_streak=progress.current_streak,
            daily_progress=progress.daily_progress,
            weekly_progress=progress.weekly_progress,
            total_sessions=progress.total_sessions,
            average_session_time=progress.average_session_time,
            best_streak=progress.best_streak,
            last_activity=progress.last_activity,
            created_at=progress.created_at,
            updated_at=progress.updated_at
        )
