"""
Class model definitions for the application.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class ClassModel(BaseModel):
    """Class model for database operations."""
    id: str = Field(..., description="Unique class identifier")
    name: str = Field(..., min_length=1, max_length=200, description="Class name")
    description: Optional[str] = Field(None, max_length=1000, description="Class description")
    teacher_id: str = Field(..., description="Teacher user ID")
    class_code: str = Field(..., description="Unique class join code")
    is_active: bool = Field(default=True, description="Class active status")
    student_count: int = Field(default=0, description="Number of enrolled students")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ClassCreateRequest(BaseModel):
    """Request model for class creation."""
    name: str = Field(..., min_length=1, max_length=200, description="Class name")
    description: Optional[str] = Field(None, max_length=1000, description="Class description")


class ClassUpdateRequest(BaseModel):
    """Request model for class updates."""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Class name")
    description: Optional[str] = Field(None, max_length=1000, description="Class description")
    
    class Config:
        extra = "forbid"


class ClassResponse(BaseModel):
    """Response model for class data."""
    id: str = Field(..., description="Unique class identifier")
    name: str = Field(..., description="Class name")
    description: Optional[str] = Field(None, description="Class description")
    teacher_id: str = Field(..., description="Teacher user ID")
    class_code: str = Field(..., description="Unique class join code")
    is_active: bool = Field(..., description="Class active status")
    student_count: int = Field(..., description="Number of enrolled students")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ClassListResponse(BaseModel):
    """Response model for class list."""
    classes: List[ClassResponse] = Field(..., description="List of classes")
    total: int = Field(..., description="Total number of classes")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")


class ClassEnrollmentModel(BaseModel):
    """Class enrollment model for database operations."""
    id: str = Field(..., description="Unique enrollment identifier")
    class_id: str = Field(..., description="Class ID")
    student_id: str = Field(..., description="Student user ID")
    enrolled_at: datetime = Field(default_factory=datetime.utcnow, description="Enrollment timestamp")
    is_active: bool = Field(default=True, description="Enrollment active status")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ClassJoinRequest(BaseModel):
    """Request model for joining a class."""
    class_code: str = Field(..., description="Class join code")


class ClassJoinResponse(BaseModel):
    """Response model for class join."""
    class_id: str = Field(..., description="Joined class ID")
    class_name: str = Field(..., description="Class name")
    teacher_name: str = Field(..., description="Teacher name")
    enrolled_at: datetime = Field(..., description="Enrollment timestamp")
    message: str = Field(..., description="Join confirmation message")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
