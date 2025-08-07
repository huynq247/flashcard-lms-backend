from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId
from .user import PyObjectId
from .deck import DeckCategory, DifficultyLevel

class CourseModel(BaseModel):
    """Course model for 3-level hierarchy"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    creator_id: PyObjectId = Field(..., description="Reference to users._id (role: teacher/admin)")
    
    # Course structure
    lesson_ids: List[PyObjectId] = Field(default_factory=list, description="Reference to lessons._id (ordered)")
    category: DeckCategory = Field(..., description="Course category")
    difficulty_level: DifficultyLevel = Field(default=DifficultyLevel.BEGINNER)
    estimated_duration: Optional[int] = Field(None, gt=0, description="Estimated duration in minutes")
    
    # Course Settings
    is_public: bool = Field(default=False)
    requires_approval: bool = Field(default=False)
    enrollment_count: int = Field(default=0, ge=0)
    completion_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Additional metadata
    learning_objectives: List[str] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)
    target_audience: Optional[str] = Field(None, max_length=500)
    language: Optional[str] = Field(None, max_length=50)
    
    # Course statistics
    average_rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    total_reviews: int = Field(default=0, ge=0)
    
    # Meta
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Status
    is_active: bool = Field(default=True)
    is_featured: bool = Field(default=False)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "title": "Spanish Grammar Fundamentals",
                "description": "Complete course covering Spanish grammar basics",
                "category": "language",
                "difficulty_level": "beginner",
                "estimated_duration": 480,
                "learning_objectives": [
                    "Master basic Spanish verb conjugation",
                    "Understand noun and adjective agreement",
                    "Learn fundamental sentence structures"
                ],
                "target_audience": "Spanish language beginners",
                "language": "Spanish"
            }
        }

class CourseCreate(BaseModel):
    """Course creation model"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    category: DeckCategory
    difficulty_level: DifficultyLevel = Field(default=DifficultyLevel.BEGINNER)
    estimated_duration: Optional[int] = Field(None, gt=0)
    is_public: bool = Field(default=False)
    requires_approval: bool = Field(default=False)
    learning_objectives: List[str] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)
    target_audience: Optional[str] = Field(None, max_length=500)
    language: Optional[str] = Field(None, max_length=50)

class CourseUpdate(BaseModel):
    """Course update model"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    category: Optional[DeckCategory] = None
    difficulty_level: Optional[DifficultyLevel] = None
    estimated_duration: Optional[int] = Field(None, gt=0)
    is_public: Optional[bool] = None
    requires_approval: Optional[bool] = None
    learning_objectives: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None
    target_audience: Optional[str] = Field(None, max_length=500)
    language: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None

class CourseResponse(BaseModel):
    """Course response model"""
    id: PyObjectId = Field(alias="_id")
    title: str
    description: Optional[str]
    creator_id: PyObjectId
    lesson_ids: List[PyObjectId]
    category: DeckCategory
    difficulty_level: DifficultyLevel
    estimated_duration: Optional[int]
    is_public: bool
    requires_approval: bool
    enrollment_count: int
    completion_rate: float
    learning_objectives: List[str]
    prerequisites: List[str]
    target_audience: Optional[str]
    language: Optional[str]
    average_rating: Optional[float]
    total_reviews: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
    is_featured: bool

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class CourseStats(BaseModel):
    """Course statistics model"""
    course_id: PyObjectId
    total_lessons: int
    completed_lessons: int
    total_students: int
    completion_percentage: float
    average_progress: float
    total_study_time: int  # seconds
    last_activity: Optional[datetime]
