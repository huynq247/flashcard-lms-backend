from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId
from enum import Enum
from app.utils.objectid import PyObjectId

class EnrollmentType(str, Enum):
    CLASS = "class"
    COURSE = "course"
    LESSON = "lesson"

class EnrollmentStatus(str, Enum):
    ENROLLED = "enrolled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DROPPED = "dropped"
    SUSPENDED = "suspended"
    PENDING_APPROVAL = "pending_approval"

class EnrollmentMethod(str, Enum):
    MANUAL = "manual"           # Teacher/admin enrolled student
    SELF_ENROLL = "self_enroll" # Student enrolled themselves
    BULK_IMPORT = "bulk_import" # Bulk enrollment
    INVITATION = "invitation"   # Student accepted invitation

class EnrollmentModel(BaseModel):
    """Enrollment model with 3-level support"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True
    )
    
    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")
    user_id: PyObjectId = Field(..., description="Reference to users._id")
    
    # 3-level enrollment support
    class_id: Optional[PyObjectId] = Field(None, description="Reference to classes._id")
    course_id: Optional[PyObjectId] = Field(None, description="Reference to courses._id")
    lesson_id: Optional[PyObjectId] = Field(None, description="Reference to lessons._id")
    
    enrollment_type: EnrollmentType = Field(..., description="Type of enrollment")
    enrollment_method: EnrollmentMethod = Field(..., description="How student was enrolled")
    
    # Enrollment Details
    enrollment_date: datetime = Field(default_factory=datetime.utcnow, description="When student enrolled")
    start_date: Optional[datetime] = Field(None, description="When enrollment becomes active")
    end_date: Optional[datetime] = Field(None, description="When enrollment expires")
    completion_date: Optional[datetime] = Field(None, description="When student completed")
    
    status: EnrollmentStatus = Field(default=EnrollmentStatus.ENROLLED, description="Current enrollment status")
    
    # Progress Tracking
    progress_percentage: float = Field(default=0.0, ge=0.0, le=100.0, description="Overall completion percentage")
    last_activity: Optional[datetime] = Field(None, description="Last learning activity")
    
    # Performance Metrics
    total_time_spent: int = Field(default=0, ge=0, description="Total study time in seconds")
    assignments_completed: int = Field(default=0, ge=0)
    assignments_total: int = Field(default=0, ge=0)
    average_grade: Optional[float] = Field(None, ge=0.0, le=100.0)
    
    # Access Control
    is_active: bool = Field(default=True, description="Whether enrollment is active")
    enrolled_by: Optional[PyObjectId] = Field(None, description="Who enrolled the student")
    approval_required: bool = Field(default=False, description="Whether enrollment needs approval")
    approved_by: Optional[PyObjectId] = Field(None, description="Who approved enrollment")
    approved_at: Optional[datetime] = Field(None, description="When enrollment was approved")
    
    # Additional Data
    enrollment_notes: Optional[str] = Field(None, max_length=1000, description="Notes about enrollment")
    custom_data: Optional[Dict[str, Any]] = Field(None, description="Custom enrollment data")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class EnrollmentCreate(BaseModel):
    """Schema for creating enrollments"""
    user_id: PyObjectId
    enrollment_type: EnrollmentType
    enrollment_method: EnrollmentMethod = EnrollmentMethod.MANUAL
    class_id: Optional[PyObjectId] = None
    course_id: Optional[PyObjectId] = None
    lesson_id: Optional[PyObjectId] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    enrolled_by: Optional[PyObjectId] = None
    approval_required: bool = False
    enrollment_notes: Optional[str] = Field(None, max_length=1000)
    custom_data: Optional[Dict[str, Any]] = None

class EnrollmentUpdate(BaseModel):
    """Schema for updating enrollments"""
    status: Optional[EnrollmentStatus] = None
    progress_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    completion_date: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    total_time_spent: Optional[int] = Field(None, ge=0)
    assignments_completed: Optional[int] = Field(None, ge=0)
    assignments_total: Optional[int] = Field(None, ge=0)
    average_grade: Optional[float] = Field(None, ge=0.0, le=100.0)
    is_active: Optional[bool] = None
    approved_by: Optional[PyObjectId] = None
    approved_at: Optional[datetime] = None
    enrollment_notes: Optional[str] = Field(None, max_length=1000)
    custom_data: Optional[Dict[str, Any]] = None

class EnrollmentResponse(BaseModel):
    """Schema for enrollment responses"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )
    
    id: PyObjectId = Field(alias="_id")
    user_id: PyObjectId
    class_id: Optional[PyObjectId] = None
    course_id: Optional[PyObjectId] = None
    lesson_id: Optional[PyObjectId] = None
    enrollment_type: EnrollmentType
    enrollment_method: EnrollmentMethod
    enrollment_date: datetime
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    status: EnrollmentStatus
    progress_percentage: float
    last_activity: Optional[datetime] = None
    total_time_spent: int
    assignments_completed: int
    assignments_total: int
    average_grade: Optional[float] = None
    is_active: bool
    enrolled_by: Optional[PyObjectId] = None
    approval_required: bool
    approved_by: Optional[PyObjectId] = None
    approved_at: Optional[datetime] = None
    enrollment_notes: Optional[str] = None
    custom_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_orm(cls, enrollment: EnrollmentModel):
        """Create EnrollmentResponse from EnrollmentModel"""
        return cls(
            _id=enrollment.id,
            user_id=enrollment.user_id,
            class_id=enrollment.class_id,
            course_id=enrollment.course_id,
            lesson_id=enrollment.lesson_id,
            enrollment_type=enrollment.enrollment_type,
            enrollment_method=enrollment.enrollment_method,
            enrollment_date=enrollment.enrollment_date,
            start_date=enrollment.start_date,
            end_date=enrollment.end_date,
            completion_date=enrollment.completion_date,
            status=enrollment.status,
            progress_percentage=enrollment.progress_percentage,
            last_activity=enrollment.last_activity,
            total_time_spent=enrollment.total_time_spent,
            assignments_completed=enrollment.assignments_completed,
            assignments_total=enrollment.assignments_total,
            average_grade=enrollment.average_grade,
            is_active=enrollment.is_active,
            enrolled_by=enrollment.enrolled_by,
            approval_required=enrollment.approval_required,
            approved_by=enrollment.approved_by,
            approved_at=enrollment.approved_at,
            enrollment_notes=enrollment.enrollment_notes,
            custom_data=enrollment.custom_data,
            created_at=enrollment.created_at,
            updated_at=enrollment.updated_at
        )

class BulkEnrollmentCreate(BaseModel):
    """Schema for bulk enrollment creation"""
    user_ids: list[PyObjectId] = Field(..., min_items=1, max_items=1000)
    enrollment_type: EnrollmentType
    class_id: Optional[PyObjectId] = None
    course_id: Optional[PyObjectId] = None
    lesson_id: Optional[PyObjectId] = None
    enrollment_method: EnrollmentMethod = EnrollmentMethod.BULK_IMPORT
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    enrolled_by: Optional[PyObjectId] = None
    approval_required: bool = False
    enrollment_notes: Optional[str] = Field(None, max_length=1000)

class EnrollmentStats(BaseModel):
    """Enrollment statistics for classes/courses/lessons"""
    total_enrolled: int = Field(default=0, ge=0)
    active_students: int = Field(default=0, ge=0)
    completed: int = Field(default=0, ge=0)
    in_progress: int = Field(default=0, ge=0)
    dropped: int = Field(default=0, ge=0)
    pending_approval: int = Field(default=0, ge=0)
    average_progress: float = Field(default=0.0, ge=0.0, le=100.0)
    completion_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    average_time_to_complete: Optional[int] = Field(None, ge=0, description="Average completion time in days")
