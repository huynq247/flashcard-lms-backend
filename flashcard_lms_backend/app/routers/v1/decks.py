from fastapi import APIRouter, HTTPException, Depends, status, Query
from app.models.deck import DeckModel, DeckCreate, DeckUpdate, DeckResponse, PrivacyLevel, DeckCategory
from app.services.database_service import db_service
from app.utils.auth import get_current_user
from app.models.user import UserModel
from bson import ObjectId
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=DeckResponse, status_code=status.HTTP_201_CREATED)
async def create_deck(
    deck_data: DeckCreate,
    current_user: UserModel = Depends(get_current_user)
):
    """Create a new deck"""
    try:
        deck = await db_service.create_deck(deck_data, current_user.id)
        return DeckResponse.from_orm(deck)
    
    except Exception as e:
        logger.error(f"Error creating deck: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/", response_model=List[DeckResponse])
async def get_user_decks(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: UserModel = Depends(get_current_user)
):
    """Get current user's decks"""
    try:
        decks = await db_service.get_decks_by_owner(current_user.id, skip, limit)
        return [DeckResponse.from_orm(deck) for deck in decks]
    
    except Exception as e:
        logger.error(f"Error getting user decks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/{deck_id}", response_model=DeckResponse)
async def get_deck_by_id(
    deck_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """Get deck by ID"""
    try:
        if not ObjectId.is_valid(deck_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid deck ID format"
            )
        
        deck = await db_service.get_deck_by_id(ObjectId(deck_id))
        if not deck:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deck not found"
            )
        
        # Check permissions
        if deck.owner_id != current_user.id and deck.privacy_level == PrivacyLevel.PRIVATE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return DeckResponse.from_orm(deck)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting deck: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/{deck_id}", response_model=DeckResponse)
async def update_deck(
    deck_id: str,
    deck_data: DeckUpdate,
    current_user: UserModel = Depends(get_current_user)
):
    """Update deck"""
    try:
        if not ObjectId.is_valid(deck_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid deck ID format"
            )
        
        deck = await db_service.get_deck_by_id(ObjectId(deck_id))
        if not deck:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deck not found"
            )
        
        # Check ownership
        if deck.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only deck owner can update"
            )
        
        updated_deck = await db_service.update_deck(ObjectId(deck_id), deck_data)
        return DeckResponse.from_orm(updated_deck)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating deck: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
