"""
Deck model definitions for the application.
"""
from typing import Optional, List, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field

from app.models.enums import DeckPrivacyLevel


class DeckModel(BaseModel):
    """Deck model for database operations."""
    id: str = Field(..., description="Unique deck identifier")
    title: str = Field(..., min_length=1, max_length=200, description="Deck title")
    description: Optional[str] = Field(None, max_length=1000, description="Deck description")
    owner_id: str = Field(..., description="Owner user ID")
    privacy_level: DeckPrivacyLevel = Field(default=DeckPrivacyLevel.PRIVATE, description="Privacy level")
    is_active: bool = Field(default=True, description="Deck active status")
    card_count: int = Field(default=0, description="Number of cards in deck")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    last_studied: Optional[datetime] = Field(default=None, description="Last study session timestamp")
    tags: List[str] = Field(default_factory=list, description="Deck tags")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DeckCreateRequest(BaseModel):
    """Request model for deck creation."""
    title: str = Field(..., min_length=1, max_length=200, description="Deck title")
    description: Optional[str] = Field(None, max_length=1000, description="Deck description")
    privacy_level: DeckPrivacyLevel = Field(default=DeckPrivacyLevel.PRIVATE, description="Privacy level")
    tags: List[str] = Field(default_factory=list, description="Deck tags")


class DeckUpdateRequest(BaseModel):
    """Request model for deck updates."""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Deck title")
    description: Optional[str] = Field(None, max_length=1000, description="Deck description")
    privacy_level: Optional[DeckPrivacyLevel] = Field(None, description="Privacy level")
    tags: Optional[List[str]] = Field(None, description="Deck tags")
    
    class Config:
        extra = "forbid"


class DeckResponse(BaseModel):
    """Response model for deck data."""
    id: str = Field(..., description="Unique deck identifier")
    title: str = Field(..., description="Deck title")
    description: Optional[str] = Field(None, description="Deck description")
    owner_id: str = Field(..., description="Owner user ID")
    privacy_level: DeckPrivacyLevel = Field(..., description="Privacy level")
    is_active: bool = Field(..., description="Deck active status")
    card_count: int = Field(..., description="Number of cards in deck")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    last_studied: Optional[datetime] = Field(None, description="Last study session timestamp")
    tags: List[str] = Field(..., description="Deck tags")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DeckListResponse(BaseModel):
    """Response model for deck list."""
    decks: List[DeckResponse] = Field(..., description="List of decks")
    total: int = Field(..., description="Total number of decks")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")


class CardModel(BaseModel):
    """Card model for database operations."""
    id: str = Field(..., description="Unique card identifier")
    deck_id: str = Field(..., description="Parent deck ID")
    front_content: str = Field(..., min_length=1, description="Front side content")
    back_content: str = Field(..., min_length=1, description="Back side content")
    card_type: str = Field(default="basic", description="Card type")
    difficulty: int = Field(default=0, ge=0, le=10, description="Card difficulty rating")
    is_active: bool = Field(default=True, description="Card active status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional card metadata")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CardCreateRequest(BaseModel):
    """Request model for card creation."""
    front_content: str = Field(..., min_length=1, description="Front side content")
    back_content: str = Field(..., min_length=1, description="Back side content")
    card_type: str = Field(default="basic", description="Card type")
    difficulty: int = Field(default=0, ge=0, le=10, description="Card difficulty rating")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional card metadata")


class CardUpdateRequest(BaseModel):
    """Request model for card updates."""
    front_content: Optional[str] = Field(None, min_length=1, description="Front side content")
    back_content: Optional[str] = Field(None, min_length=1, description="Back side content")
    card_type: Optional[str] = Field(None, description="Card type")
    difficulty: Optional[int] = Field(None, ge=0, le=10, description="Card difficulty rating")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional card metadata")
    
    class Config:
        extra = "forbid"


class CardResponse(BaseModel):
    """Response model for card data."""
    id: str = Field(..., description="Unique card identifier")
    deck_id: str = Field(..., description="Parent deck ID")
    front_content: str = Field(..., description="Front side content")
    back_content: str = Field(..., description="Back side content")
    card_type: str = Field(..., description="Card type")
    difficulty: int = Field(..., description="Card difficulty rating")
    is_active: bool = Field(..., description="Card active status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    metadata: Dict[str, Any] = Field(..., description="Additional card metadata")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CardListResponse(BaseModel):
    """Response model for card list."""
    cards: List[CardResponse] = Field(..., description="List of cards")
    total: int = Field(..., description="Total number of cards")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
