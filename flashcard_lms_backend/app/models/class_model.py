from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId
from .user import PyObjectId

class ClassModel(BaseModel):
    """Class model for 3-level hierarchy"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    teacher_id: PyObjectId = Field(..., description="Reference to users._id (role: teacher)")
    
    # Students and courses
    student_ids: List[PyObjectId] = Field(default_factory=list, description="Reference to users._id (role: student)")
    course_ids: List[PyObjectId] = Field(default_factory=list, description="Reference to courses._id")
    
    # Classroom Management
    max_students: Optional[int] = Field(None, gt=0, le=1000)
    current_enrollment: int = Field(default=0, ge=0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: bool = Field(default=True)
    
    # Meta
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Additional settings
    allow_self_enrollment: bool = Field(default=False)
    requires_approval: bool = Field(default=True)
    class_code: Optional[str] = Field(None, description="Unique class code for joining")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Advanced Spanish - Fall 2025",
                "description": "Advanced Spanish language course for fall semester",
                "max_students": 30,
                "start_date": "2025-09-01T00:00:00Z",
                "end_date": "2025-12-15T23:59:59Z"
            }
        }

class ClassCreate(BaseModel):
    """Class creation model"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    max_students: Optional[int] = Field(None, gt=0, le=1000)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    allow_self_enrollment: bool = Field(default=False)
    requires_approval: bool = Field(default=True)

class ClassUpdate(BaseModel):
    """Class update model"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    max_students: Optional[int] = Field(None, gt=0, le=1000)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    allow_self_enrollment: Optional[bool] = None
    requires_approval: Optional[bool] = None

class ClassResponse(BaseModel):
    """Class response model"""
    id: PyObjectId = Field(alias="_id")
    name: str
    description: Optional[str]
    teacher_id: PyObjectId
    student_ids: List[PyObjectId]
    course_ids: List[PyObjectId]
    max_students: Optional[int]
    current_enrollment: int
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    allow_self_enrollment: bool
    requires_approval: bool
    class_code: Optional[str]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
