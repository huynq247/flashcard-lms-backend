from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from bson import ObjectId
from .user import PyObjectId

class StudyMode(str, Enum):
    """Multiple study modes (Decision #11: Multiple Modes)"""
    REVIEW = "review"
    PRACTICE = "practice"
    CRAM = "cram"
    TEST = "test"
    LEARN = "learn"

class SessionStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

class StudySessionModel(BaseModel):
    """Study session model with advanced features (Decision #10 + #11)"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId = Field(..., description="Reference to users._id")
    deck_id: PyObjectId = Field(..., description="Reference to decks._id")
    lesson_id: Optional[PyObjectId] = Field(None, description="Reference to lessons._id")
    
    # Multiple Study Modes (Decision #11)
    study_mode: StudyMode = Field(..., description="Current study mode")
    
    # Advanced Features (Decision #10)
    target_time: Optional[int] = Field(None, gt=0, description="Target time in minutes")
    target_cards: Optional[int] = Field(None, gt=0, description="Target number of cards")
    break_reminders_enabled: bool = Field(default=True)
    
    # Session Data
    cards_studied: int = Field(default=0, ge=0)
    correct_answers: int = Field(default=0, ge=0)
    incorrect_answers: int = Field(default=0, ge=0)
    total_time: int = Field(default=0, ge=0, description="Total time in seconds")
    break_count: int = Field(default=0, ge=0)
    status: SessionStatus = Field(default=SessionStatus.ACTIVE)
    
    # Session Analytics
    accuracy_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    average_response_time: Optional[float] = Field(None, ge=0.0, description="Average response time in seconds")
    cards_per_minute: Optional[float] = Field(None, ge=0.0)
    
    # Session settings
    card_order: str = Field(default="random", description="Card order: random, sequential, smart")
    show_timer: bool = Field(default=True)
    auto_advance: bool = Field(default=False)
    
    # Break tracking
    break_intervals: List[int] = Field(default_factory=list, description="Break intervals in minutes")
    break_duration: int = Field(default=5, ge=1, le=60, description="Break duration in minutes")
    
    # Progress tracking
    session_progress: List[Dict[str, Any]] = Field(default_factory=list, description="Card-by-card progress")
    
    # Meta
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Additional analytics
    streak_data: Dict[str, Any] = Field(default_factory=dict)
    difficulty_progression: List[float] = Field(default_factory=list)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "study_mode": "review",
                "target_time": 30,
                "target_cards": 25,
                "break_reminders_enabled": True,
                "card_order": "smart",
                "show_timer": True,
                "break_intervals": [15, 30],
                "break_duration": 5
            }
        }

class StudySessionCreate(BaseModel):
    """Study session creation model"""
    deck_id: PyObjectId
    lesson_id: Optional[PyObjectId] = None
    study_mode: StudyMode
    target_time: Optional[int] = Field(None, gt=0)
    target_cards: Optional[int] = Field(None, gt=0)
    break_reminders_enabled: bool = Field(default=True)
    card_order: str = Field(default="random")
    show_timer: bool = Field(default=True)
    auto_advance: bool = Field(default=False)
    break_intervals: List[int] = Field(default_factory=list)
    break_duration: int = Field(default=5, ge=1, le=60)

class StudySessionUpdate(BaseModel):
    """Study session update model"""
    status: Optional[SessionStatus] = None
    cards_studied: Optional[int] = Field(None, ge=0)
    correct_answers: Optional[int] = Field(None, ge=0)
    incorrect_answers: Optional[int] = Field(None, ge=0)
    total_time: Optional[int] = Field(None, ge=0)
    break_count: Optional[int] = Field(None, ge=0)
    accuracy_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    average_response_time: Optional[float] = Field(None, ge=0.0)

class StudySessionResponse(BaseModel):
    """Study session response model"""
    id: PyObjectId = Field(alias="_id")
    user_id: PyObjectId
    deck_id: PyObjectId
    lesson_id: Optional[PyObjectId]
    study_mode: StudyMode
    target_time: Optional[int]
    target_cards: Optional[int]
    break_reminders_enabled: bool
    cards_studied: int
    correct_answers: int
    incorrect_answers: int
    total_time: int
    break_count: int
    status: SessionStatus
    accuracy_rate: Optional[float]
    average_response_time: Optional[float]
    cards_per_minute: Optional[float]
    started_at: datetime
    completed_at: Optional[datetime]
    updated_at: datetime

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class SessionAnalytics(BaseModel):
    """Session analytics model"""
    session_id: PyObjectId
    total_sessions: int
    average_accuracy: float
    total_study_time: int
    improvement_rate: float
    consistency_score: float
    preferred_study_modes: List[str]
    peak_performance_times: List[str]
    common_mistakes: List[Dict[str, Any]]
