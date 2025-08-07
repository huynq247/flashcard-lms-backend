from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId
from enum import Enum
from app.utils.objectid import PyObjectId

class AssignmentType(str, Enum):
    CLASS = "class"
    COURSE = "course"
    LESSON = "lesson"
    INDIVIDUAL = "individual"

class AssignmentStatus(str, Enum):
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

class StudyModeRestriction(str, Enum):
    REVIEW = "review"
    PRACTICE = "practice"
    CRAM = "cram"
    TEST = "test"
    LEARN = "learn"
    ANY = "any"

class CompletionCriteria(BaseModel):
    """Completion criteria for deck assignments"""
    min_accuracy: Optional[float] = Field(None, ge=0.0, le=1.0, description="Minimum accuracy required")
    min_reviews: Optional[int] = Field(None, ge=1, description="Minimum number of reviews")
    min_cards: Optional[int] = Field(None, ge=1, description="Minimum number of cards to study")
    min_time: Optional[int] = Field(None, ge=1, description="Minimum study time in seconds")
    target_mastery: Optional[float] = Field(None, ge=0.0, le=1.0, description="Target mastery percentage")

class DeckAssignmentModel(BaseModel):
    """Deck assignment model with 3-level assignment support"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True
    )
    
    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")
    deck_id: PyObjectId = Field(..., description="Reference to decks._id")
    assigned_by: PyObjectId = Field(..., description="Reference to users._id (teacher/admin)")
    
    # 3-level Assignment Support
    class_id: Optional[PyObjectId] = Field(None, description="Reference to classes._id")
    course_id: Optional[PyObjectId] = Field(None, description="Reference to courses._id")
    lesson_id: Optional[PyObjectId] = Field(None, description="Reference to lessons._id")
    student_id: Optional[PyObjectId] = Field(None, description="For individual assignments")
    
    assignment_type: AssignmentType = Field(..., description="Type of assignment")
    
    # Assignment Details
    title: str = Field(..., min_length=1, max_length=200, description="Assignment title")
    description: Optional[str] = Field(None, max_length=1000, description="Assignment description")
    instructions: Optional[str] = Field(None, max_length=2000, description="Special instructions")
    
    assignment_date: datetime = Field(default_factory=datetime.utcnow, description="When assignment was created")
    due_date: Optional[datetime] = Field(None, description="Assignment due date")
    is_required: bool = Field(default=True, description="Whether assignment is mandatory")
    status: AssignmentStatus = Field(default=AssignmentStatus.ASSIGNED, description="Assignment status")
    
    # Assignment Settings
    study_mode_restriction: StudyModeRestriction = Field(default=StudyModeRestriction.ANY, description="Restricted study mode")
    completion_criteria: Optional[CompletionCriteria] = Field(None, description="Completion requirements")
    
    # Grading and Feedback
    max_points: Optional[int] = Field(None, ge=0, description="Maximum points for assignment")
    auto_grade: bool = Field(default=True, description="Whether to auto-grade based on completion criteria")
    allow_multiple_attempts: bool = Field(default=True, description="Allow multiple attempts")
    max_attempts: Optional[int] = Field(None, ge=1, description="Maximum number of attempts")
    
    # Notifications
    send_reminders: bool = Field(default=True, description="Send reminder notifications")
    reminder_days: Optional[int] = Field(None, ge=1, le=30, description="Days before due date to send reminders")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class DeckAssignmentCreate(BaseModel):
    """Schema for creating deck assignments"""
    deck_id: PyObjectId
    assigned_by: PyObjectId
    assignment_type: AssignmentType
    class_id: Optional[PyObjectId] = None
    course_id: Optional[PyObjectId] = None
    lesson_id: Optional[PyObjectId] = None
    student_id: Optional[PyObjectId] = None
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    instructions: Optional[str] = Field(None, max_length=2000)
    due_date: Optional[datetime] = None
    is_required: bool = True
    study_mode_restriction: StudyModeRestriction = StudyModeRestriction.ANY
    completion_criteria: Optional[CompletionCriteria] = None
    max_points: Optional[int] = Field(None, ge=0)
    auto_grade: bool = True
    allow_multiple_attempts: bool = True
    max_attempts: Optional[int] = Field(None, ge=1)
    send_reminders: bool = True
    reminder_days: Optional[int] = Field(None, ge=1, le=30)

class DeckAssignmentUpdate(BaseModel):
    """Schema for updating deck assignments"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    instructions: Optional[str] = Field(None, max_length=2000)
    due_date: Optional[datetime] = None
    is_required: Optional[bool] = None
    status: Optional[AssignmentStatus] = None
    study_mode_restriction: Optional[StudyModeRestriction] = None
    completion_criteria: Optional[CompletionCriteria] = None
    max_points: Optional[int] = Field(None, ge=0)
    auto_grade: Optional[bool] = None
    allow_multiple_attempts: Optional[bool] = None
    max_attempts: Optional[int] = Field(None, ge=1)
    send_reminders: Optional[bool] = None
    reminder_days: Optional[int] = Field(None, ge=1, le=30)

class DeckAssignmentResponse(BaseModel):
    """Schema for deck assignment responses"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )
    
    id: PyObjectId = Field(alias="_id")
    deck_id: PyObjectId
    assigned_by: PyObjectId
    class_id: Optional[PyObjectId] = None
    course_id: Optional[PyObjectId] = None
    lesson_id: Optional[PyObjectId] = None
    student_id: Optional[PyObjectId] = None
    assignment_type: AssignmentType
    title: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    assignment_date: datetime
    due_date: Optional[datetime] = None
    is_required: bool
    status: AssignmentStatus
    study_mode_restriction: StudyModeRestriction
    completion_criteria: Optional[CompletionCriteria] = None
    max_points: Optional[int] = None
    auto_grade: bool
    allow_multiple_attempts: bool
    max_attempts: Optional[int] = None
    send_reminders: bool
    reminder_days: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_orm(cls, assignment: DeckAssignmentModel):
        """Create DeckAssignmentResponse from DeckAssignmentModel"""
        return cls(
            _id=assignment.id,
            deck_id=assignment.deck_id,
            assigned_by=assignment.assigned_by,
            class_id=assignment.class_id,
            course_id=assignment.course_id,
            lesson_id=assignment.lesson_id,
            student_id=assignment.student_id,
            assignment_type=assignment.assignment_type,
            title=assignment.title,
            description=assignment.description,
            instructions=assignment.instructions,
            assignment_date=assignment.assignment_date,
            due_date=assignment.due_date,
            is_required=assignment.is_required,
            status=assignment.status,
            study_mode_restriction=assignment.study_mode_restriction,
            completion_criteria=assignment.completion_criteria,
            max_points=assignment.max_points,
            auto_grade=assignment.auto_grade,
            allow_multiple_attempts=assignment.allow_multiple_attempts,
            max_attempts=assignment.max_attempts,
            send_reminders=assignment.send_reminders,
            reminder_days=assignment.reminder_days,
            created_at=assignment.created_at,
            updated_at=assignment.updated_at
        )

class AssignmentProgress(BaseModel):
    """Student progress on an assignment"""
    assignment_id: PyObjectId
    student_id: PyObjectId
    attempt_number: int = Field(default=1, ge=1)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Progress Metrics
    cards_studied: int = Field(default=0, ge=0)
    total_cards: int = Field(default=0, ge=0)
    accuracy_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    time_spent: int = Field(default=0, ge=0, description="Time in seconds")
    
    # Completion Status
    meets_criteria: bool = Field(default=False)
    is_completed: bool = Field(default=False)
    grade: Optional[float] = Field(None, ge=0.0, le=100.0)
    feedback: Optional[str] = Field(None, max_length=1000)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
