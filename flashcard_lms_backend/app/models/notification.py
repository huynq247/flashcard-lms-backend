from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId
from enum import Enum
from app.utils.objectid import PyObjectId

class NotificationType(str, Enum):
    ASSIGNMENT = "assignment"
    MILESTONE = "milestone"
    ANNOUNCEMENT = "announcement"
    REMINDER = "reminder"
    ACHIEVEMENT = "achievement"
    DEADLINE = "deadline"
    INVITATION = "invitation"

class NotificationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class RelatedType(str, Enum):
    DECK = "deck"
    CLASS = "class"
    COURSE = "course"
    LESSON = "lesson"
    ACHIEVEMENT = "achievement"
    USER = "user"

class NotificationModel(BaseModel):
    """Notification model for in-app notifications (Decision #18: In-app only)"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True
    )
    
    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")
    user_id: PyObjectId = Field(..., description="Reference to users._id")
    
    # Notification Content
    notification_type: NotificationType = Field(..., description="Type of notification")
    title: str = Field(..., min_length=1, max_length=200, description="Notification title")
    message: str = Field(..., min_length=1, max_length=1000, description="Notification message")
    priority: NotificationPriority = Field(default=NotificationPriority.MEDIUM, description="Notification priority")
    
    # In-app Notification Data
    is_read: bool = Field(default=False, description="Whether notification has been read")
    read_at: Optional[datetime] = Field(None, description="When notification was read")
    action_url: Optional[str] = Field(None, description="Deep link for action")
    
    # Related Objects (generic reference system)
    related_id: Optional[PyObjectId] = Field(None, description="Related object ID")
    related_type: Optional[RelatedType] = Field(None, description="Type of related object")
    
    # Notification Metadata
    sender_id: Optional[PyObjectId] = Field(None, description="User who triggered notification")
    icon: Optional[str] = Field(None, description="Notification icon identifier")
    
    # Lifecycle
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(None, description="When notification expires")
    is_dismissed: bool = Field(default=False, description="Whether user dismissed notification")

class NotificationCreate(BaseModel):
    """Schema for creating notifications"""
    user_id: PyObjectId
    notification_type: NotificationType
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=1000)
    priority: NotificationPriority = NotificationPriority.MEDIUM
    action_url: Optional[str] = None
    related_id: Optional[PyObjectId] = None
    related_type: Optional[RelatedType] = None
    sender_id: Optional[PyObjectId] = None
    icon: Optional[str] = None
    expires_at: Optional[datetime] = None

class NotificationUpdate(BaseModel):
    """Schema for updating notifications"""
    is_read: Optional[bool] = None
    is_dismissed: Optional[bool] = None
    read_at: Optional[datetime] = None

class NotificationResponse(BaseModel):
    """Schema for notification responses"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )
    
    id: PyObjectId = Field(alias="_id")
    user_id: PyObjectId
    notification_type: NotificationType
    title: str
    message: str
    priority: NotificationPriority
    is_read: bool
    read_at: Optional[datetime] = None
    action_url: Optional[str] = None
    related_id: Optional[PyObjectId] = None
    related_type: Optional[RelatedType] = None
    sender_id: Optional[PyObjectId] = None
    icon: Optional[str] = None
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_dismissed: bool
    
    @classmethod
    def from_orm(cls, notification: NotificationModel):
        """Create NotificationResponse from NotificationModel"""
        return cls(
            _id=notification.id,
            user_id=notification.user_id,
            notification_type=notification.notification_type,
            title=notification.title,
            message=notification.message,
            priority=notification.priority,
            is_read=notification.is_read,
            read_at=notification.read_at,
            action_url=notification.action_url,
            related_id=notification.related_id,
            related_type=notification.related_type,
            sender_id=notification.sender_id,
            icon=notification.icon,
            created_at=notification.created_at,
            expires_at=notification.expires_at,
            is_dismissed=notification.is_dismissed
        )

class NotificationBulkCreate(BaseModel):
    """Schema for creating bulk notifications"""
    user_ids: list[PyObjectId] = Field(..., min_items=1, max_items=1000)
    notification_type: NotificationType
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=1000)
    priority: NotificationPriority = NotificationPriority.MEDIUM
    action_url: Optional[str] = None
    related_id: Optional[PyObjectId] = None
    related_type: Optional[RelatedType] = None
    sender_id: Optional[PyObjectId] = None
    icon: Optional[str] = None
    expires_at: Optional[datetime] = None

# Predefined notification templates
class NotificationTemplates:
    """Predefined notification templates for common scenarios"""
    
    @staticmethod
    def assignment_due_reminder(deck_title: str, due_date: datetime) -> dict:
        """Template for assignment due reminders"""
        return {
            "notification_type": NotificationType.REMINDER,
            "title": "Assignment Due Soon",
            "message": f"Your assignment '{deck_title}' is due on {due_date.strftime('%B %d, %Y')}",
            "priority": NotificationPriority.HIGH,
            "icon": "assignment_due"
        }
    
    @staticmethod
    def achievement_earned(achievement_title: str) -> dict:
        """Template for achievement notifications"""
        return {
            "notification_type": NotificationType.ACHIEVEMENT,
            "title": "Achievement Unlocked!",
            "message": f"Congratulations! You've earned the '{achievement_title}' achievement.",
            "priority": NotificationPriority.MEDIUM,
            "icon": "trophy"
        }
    
    @staticmethod
    def course_enrollment(course_title: str, teacher_name: str) -> dict:
        """Template for course enrollment notifications"""
        return {
            "notification_type": NotificationType.INVITATION,
            "title": "Course Enrollment",
            "message": f"You've been enrolled in '{course_title}' by {teacher_name}",
            "priority": NotificationPriority.MEDIUM,
            "icon": "course_enrollment"
        }
    
    @staticmethod
    def study_streak_reminder() -> dict:
        """Template for study streak reminders"""
        return {
            "notification_type": NotificationType.REMINDER,
            "title": "Keep Your Streak!",
            "message": "Don't forget to study today to maintain your streak.",
            "priority": NotificationPriority.LOW,
            "icon": "streak_reminder",
            "expires_at": datetime.utcnow() + timedelta(days=1)
        }
    
    @staticmethod
    def class_announcement(class_name: str, announcement: str) -> dict:
        """Template for class announcements"""
        return {
            "notification_type": NotificationType.ANNOUNCEMENT,
            "title": f"Announcement: {class_name}",
            "message": announcement,
            "priority": NotificationPriority.MEDIUM,
            "icon": "announcement"
        }
