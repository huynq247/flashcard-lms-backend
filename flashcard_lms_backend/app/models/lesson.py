from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId
from .user import PyObjectId

class CompletionCriteria(BaseModel):
    """Lesson completion criteria"""
    min_accuracy: float = Field(default=0.8, ge=0.0, le=1.0, description="Minimum accuracy required")
    min_cards: int = Field(default=0, ge=0, description="Minimum cards to review")
    min_time: Optional[int] = Field(None, gt=0, description="Minimum time in minutes")
    required_reviews: int = Field(default=1, ge=1, description="Required number of reviews")

class LessonModel(BaseModel):
    """Lesson model for 3-level hierarchy"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    course_id: PyObjectId = Field(..., description="Reference to courses._id")
    
    # Lesson content
    deck_ids: List[PyObjectId] = Field(default_factory=list, description="Reference to decks._id (assigned flashcard decks)")
    order_index: int = Field(..., ge=0, description="Position in course")
    
    # Lesson Content
    learning_objectives: List[str] = Field(default_factory=list)
    estimated_time: Optional[int] = Field(None, gt=0, description="Estimated time in minutes")
    prerequisite_lessons: List[PyObjectId] = Field(default_factory=list, description="Reference to lessons._id")
    
    # Progress Tracking
    completion_criteria: CompletionCriteria = Field(default_factory=CompletionCriteria)
    pass_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Pass threshold (70% to pass)")
    
    # Additional content
    instructions: Optional[str] = Field(None, max_length=2000)
    study_tips: List[str] = Field(default_factory=list)
    resources: List[Dict[str, Any]] = Field(default_factory=list, description="Additional resources")
    
    # Lesson statistics
    completion_count: int = Field(default=0, ge=0)
    average_completion_time: Optional[float] = Field(None, gt=0.0)
    average_accuracy: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    # Meta
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Status
    is_active: bool = Field(default=True)
    is_published: bool = Field(default=False)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "title": "Spanish Verbs - Present Tense",
                "description": "Learn conjugation of regular Spanish verbs in present tense",
                "order_index": 1,
                "learning_objectives": [
                    "Conjugate regular -ar verbs",
                    "Conjugate regular -er verbs",
                    "Conjugate regular -ir verbs"
                ],
                "estimated_time": 45,
                "instructions": "Study each flashcard carefully and practice conjugations",
                "study_tips": [
                    "Practice verb endings daily",
                    "Use mnemonics for irregular verbs"
                ],
                "completion_criteria": {
                    "min_accuracy": 0.85,
                    "min_cards": 20,
                    "required_reviews": 2
                }
            }
        }

class LessonCreate(BaseModel):
    """Lesson creation model"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    order_index: int = Field(..., ge=0)
    deck_ids: List[PyObjectId] = Field(default_factory=list)
    learning_objectives: List[str] = Field(default_factory=list)
    estimated_time: Optional[int] = Field(None, gt=0)
    prerequisite_lessons: List[PyObjectId] = Field(default_factory=list)
    completion_criteria: Optional[CompletionCriteria] = None
    pass_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    instructions: Optional[str] = Field(None, max_length=2000)
    study_tips: List[str] = Field(default_factory=list)
    resources: List[Dict[str, Any]] = Field(default_factory=list)

class LessonUpdate(BaseModel):
    """Lesson update model"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    order_index: Optional[int] = Field(None, ge=0)
    deck_ids: Optional[List[PyObjectId]] = None
    learning_objectives: Optional[List[str]] = None
    estimated_time: Optional[int] = Field(None, gt=0)
    prerequisite_lessons: Optional[List[PyObjectId]] = None
    completion_criteria: Optional[CompletionCriteria] = None
    pass_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    instructions: Optional[str] = Field(None, max_length=2000)
    study_tips: Optional[List[str]] = None
    resources: Optional[List[Dict[str, Any]]] = None
    is_active: Optional[bool] = None
    is_published: Optional[bool] = None

class LessonResponse(BaseModel):
    """Lesson response model"""
    id: PyObjectId = Field(alias="_id")
    title: str
    description: Optional[str]
    course_id: PyObjectId
    deck_ids: List[PyObjectId]
    order_index: int
    learning_objectives: List[str]
    estimated_time: Optional[int]
    prerequisite_lessons: List[PyObjectId]
    completion_criteria: CompletionCriteria
    pass_threshold: float
    instructions: Optional[str]
    study_tips: List[str]
    resources: List[Dict[str, Any]]
    completion_count: int
    average_completion_time: Optional[float]
    average_accuracy: Optional[float]
    created_at: datetime
    updated_at: datetime
    is_active: bool
    is_published: bool

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class LessonProgress(BaseModel):
    """Lesson progress tracking"""
    lesson_id: PyObjectId
    user_id: PyObjectId
    completion_percentage: float
    current_accuracy: float
    cards_reviewed: int
    time_spent: int  # seconds
    is_completed: bool
    completion_date: Optional[datetime]
    last_activity: datetime
