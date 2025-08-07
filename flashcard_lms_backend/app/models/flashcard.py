from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId
from .user import PyObjectId

class MultimediaContent(BaseModel):
    """Multimedia content for flashcards (Decision #6: Multimedia)"""
    question_image: Optional[str] = Field(None, description="Question image file path")
    answer_image: Optional[str] = Field(None, description="Answer image file path")
    question_audio: Optional[str] = Field(None, description="Question audio file path")
    answer_audio: Optional[str] = Field(None, description="Answer audio file path")
    formatting_data: Optional[Dict[str, Any]] = Field(None, description="Rich text formatting")

class SM2Data(BaseModel):
    """SM-2 Algorithm data (Decision #9: SM-2)"""
    repetitions: int = Field(default=0, ge=0, description="Number of repetitions")
    ease_factor: float = Field(default=2.5, ge=1.3, le=5.0, description="Ease factor")
    interval: int = Field(default=0, ge=0, description="Current interval in days")
    next_review: Optional[datetime] = Field(None, description="Next review date")
    quality: Optional[int] = Field(None, ge=0, le=5, description="Last quality rating (0-5)")

class FlashcardStats(BaseModel):
    """Flashcard statistics"""
    review_count: int = Field(default=0, ge=0)
    correct_count: int = Field(default=0, ge=0)
    incorrect_count: int = Field(default=0, ge=0)
    
    @property
    def accuracy_rate(self) -> float:
        """Calculate accuracy rate"""
        if self.review_count == 0:
            return 0.0
        return self.correct_count / self.review_count

class FlashcardModel(BaseModel):
    """Flashcard model with multimedia and SM-2 support"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    deck_id: PyObjectId = Field(..., description="Reference to decks._id")
    
    # Core content
    question: str = Field(..., min_length=1, max_length=2000)
    answer: str = Field(..., min_length=1, max_length=2000)
    hint: Optional[str] = Field(None, max_length=500)
    explanation: Optional[str] = Field(None, max_length=1000)
    
    # Multimedia Content (Decision #6: Multimedia)
    multimedia: Optional[MultimediaContent] = None
    
    # SM-2 Algorithm Data (Decision #9)
    sm2_data: SM2Data = Field(default_factory=SM2Data)
    
    # Statistics
    stats: FlashcardStats = Field(default_factory=FlashcardStats)
    
    # Meta
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Additional metadata
    order_index: Optional[int] = Field(None, description="Order in deck")
    is_active: bool = Field(default=True)
    difficulty_rating: Optional[float] = Field(None, ge=1.0, le=5.0)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "question": "What is the capital of France?",
                "answer": "Paris",
                "hint": "It's known as the City of Light",
                "explanation": "Paris has been the capital of France since 1792",
                "multimedia": {
                    "question_image": "/uploads/images/france_map.jpg",
                    "answer_image": "/uploads/images/paris.jpg"
                }
            }
        }

class FlashcardCreate(BaseModel):
    """Flashcard creation model"""
    question: str = Field(..., min_length=1, max_length=2000)
    answer: str = Field(..., min_length=1, max_length=2000)
    hint: Optional[str] = Field(None, max_length=500)
    explanation: Optional[str] = Field(None, max_length=1000)
    multimedia: Optional[MultimediaContent] = None
    order_index: Optional[int] = None

class FlashcardUpdate(BaseModel):
    """Flashcard update model"""
    question: Optional[str] = Field(None, min_length=1, max_length=2000)
    answer: Optional[str] = Field(None, min_length=1, max_length=2000)
    hint: Optional[str] = Field(None, max_length=500)
    explanation: Optional[str] = Field(None, max_length=1000)
    multimedia: Optional[MultimediaContent] = None
    order_index: Optional[int] = None
    is_active: Optional[bool] = None

class FlashcardResponse(BaseModel):
    """Flashcard response model"""
    id: PyObjectId = Field(alias="_id")
    deck_id: PyObjectId
    question: str
    answer: str
    hint: Optional[str]
    explanation: Optional[str]
    multimedia: Optional[MultimediaContent]
    sm2_data: SM2Data
    stats: FlashcardStats
    created_at: datetime
    updated_at: datetime
    order_index: Optional[int]
    is_active: bool
    difficulty_rating: Optional[float]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class FlashcardReview(BaseModel):
    """Flashcard review submission"""
    quality: int = Field(..., ge=0, le=5, description="Quality rating (0-5)")
    response_time: Optional[float] = Field(None, ge=0.0, description="Response time in seconds")
    was_correct: bool = Field(..., description="Whether the answer was correct")

class FlashcardReviewResponse(BaseModel):
    """Response after reviewing a flashcard"""
    flashcard_id: PyObjectId
    next_review_date: Optional[datetime]
    new_interval: int
    new_ease_factor: float
    repetitions: int
    was_correct: bool
    quality: int
