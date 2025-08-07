"""
Advanced privacy controls and deck access validation.
"""
from typing import Optional

from fastapi import HTTPException, status

from app.models.enums import UserRole, DeckPrivacyLevel
from app.models.user import UserModel
from app.services.database_service import database_service


class PrivacyService:
    """Service for privacy controls and access validation."""
    
    async def check_deck_access(self, user_id: str, deck_id: str) -> bool:
        """
        Check if user has access to a deck based on privacy level.
        
        Args:
            user_id: ID of user requesting access
            deck_id: ID of deck to access
            
        Returns:
            True if user has access, False otherwise
        """
        try:
            # Get deck and user
            deck = await database_service.get_deck_by_id(deck_id)
            if not deck:
                return False
            
            user = await database_service.get_user_by_id(user_id)
            if not user:
                return False
            
            # Admin can access everything
            if user.role == UserRole.ADMIN:
                return True
            
            # Owner can always access their own decks
            if str(deck.owner_id) == str(user_id):
                return True
            
            # Check privacy level
            if deck.privacy_level == DeckPrivacyLevel.PUBLIC:
                return True
            elif deck.privacy_level == DeckPrivacyLevel.PRIVATE:
                return False  # Only owner can access private decks
            elif deck.privacy_level == DeckPrivacyLevel.CLASS_ASSIGNED:
                return await self._check_class_assignment_access(user_id, deck_id)
            elif deck.privacy_level == DeckPrivacyLevel.COURSE_ASSIGNED:
                return await self._check_course_assignment_access(user_id, deck_id)
            elif deck.privacy_level == DeckPrivacyLevel.LESSON_ASSIGNED:
                return await self._check_lesson_assignment_access(user_id, deck_id)
            
            return False
            
        except Exception:
            return False
    
    async def _check_class_assignment_access(self, user_id: str, deck_id: str) -> bool:
        """Check if user has access to deck through class assignment."""
        try:
            # Get all class assignments for this deck
            assignments = await database_service.get_deck_assignments_by_deck_and_type(
                deck_id, "class"
            )
            
            if not assignments:
                return False
            
            # Check if user is enrolled in any of the assigned classes
            for assignment in assignments:
                enrollment = await database_service.get_enrollment_by_user_and_class(
                    user_id, str(assignment.class_id)
                )
                if enrollment and enrollment.status in ["enrolled", "in_progress", "completed"]:
                    return True
            
            return False
            
        except Exception:
            return False
    
    async def _check_course_assignment_access(self, user_id: str, deck_id: str) -> bool:
        """Check if user has access to deck through course assignment."""
        try:
            # Get all course assignments for this deck
            assignments = await database_service.get_deck_assignments_by_deck_and_type(
                deck_id, "course"
            )
            
            if not assignments:
                return False
            
            # Check if user is enrolled in any of the assigned courses
            for assignment in assignments:
                enrollment = await database_service.get_enrollment_by_user_and_course(
                    user_id, str(assignment.course_id)
                )
                if enrollment and enrollment.status in ["enrolled", "in_progress", "completed"]:
                    return True
            
            return False
            
        except Exception:
            return False
    
    async def _check_lesson_assignment_access(self, user_id: str, deck_id: str) -> bool:
        """Check if user has access to deck through lesson assignment."""
        try:
            # Get all lesson assignments for this deck
            assignments = await database_service.get_deck_assignments_by_deck_and_type(
                deck_id, "lesson"
            )
            
            if not assignments:
                return False
            
            # Check if user has access to any of the assigned lessons
            for assignment in assignments:
                # Check lesson access through course enrollment
                lesson = await database_service.get_lesson_by_id(str(assignment.lesson_id))
                if lesson:
                    enrollment = await database_service.get_enrollment_by_user_and_course(
                        user_id, str(lesson.course_id)
                    )
                    if enrollment and enrollment.status in ["enrolled", "in_progress", "completed"]:
                        return True
            
            return False
            
        except Exception:
            return False
    
    async def validate_deck_privacy_change(
        self, 
        deck_id: str, 
        new_privacy_level: DeckPrivacyLevel,
        user: UserModel
    ) -> bool:
        """
        Validate if user can change deck privacy level.
        
        Args:
            deck_id: ID of deck to change
            new_privacy_level: New privacy level
            user: User making the change
            
        Returns:
            True if change is allowed, False otherwise
        """
        try:
            deck = await database_service.get_deck_by_id(deck_id)
            if not deck:
                return False
            
            # Only owner or admin can change privacy
            if user.role != UserRole.ADMIN and str(deck.owner_id) != str(user.id):
                return False
            
            # Teachers can't make their decks completely private if they're assigned
            if (user.role == UserRole.TEACHER and 
                new_privacy_level == DeckPrivacyLevel.PRIVATE):
                
                # Check if deck has active assignments
                assignments = await database_service.get_active_assignments_by_deck(deck_id)
                if assignments:
                    return False
            
            return True
            
        except Exception:
            return False
    
    async def get_accessible_decks(
        self, 
        user_id: str, 
        privacy_level: Optional[DeckPrivacyLevel] = None
    ) -> list:
        """
        Get all decks accessible to a user.
        
        Args:
            user_id: ID of user
            privacy_level: Filter by specific privacy level (optional)
            
        Returns:
            List of accessible deck IDs
        """
        try:
            user = await database_service.get_user_by_id(user_id)
            if not user:
                return []
            
            accessible_decks = []
            
            # Get all decks (or filtered by privacy level)
            if privacy_level:
                decks = await database_service.get_decks_by_privacy_level(privacy_level)
            else:
                decks = await database_service.get_all_decks()
            
            # Check access for each deck
            for deck in decks:
                has_access = await self.check_deck_access(user_id, str(deck.id))
                if has_access:
                    accessible_decks.append(str(deck.id))
            
            return accessible_decks
            
        except Exception:
            return []
    
    async def get_user_owned_decks(self, user_id: str) -> list:
        """Get all decks owned by a user."""
        try:
            return await database_service.get_decks_by_owner(user_id)
        except Exception:
            return []
    
    async def check_assignment_access(self, user_id: str, deck_id: str) -> dict:
        """
        Check assignment-based access details for a deck.
        
        Returns:
            Dictionary with access details and assignment information
        """
        try:
            access_info = {
                "has_access": False,
                "access_type": None,
                "assignments": []
            }
            
            # Check class assignments
            class_assignments = await database_service.get_deck_assignments_by_deck_and_type(
                deck_id, "class"
            )
            for assignment in class_assignments:
                enrollment = await database_service.get_enrollment_by_user_and_class(
                    user_id, str(assignment.class_id)
                )
                if enrollment and enrollment.status in ["enrolled", "in_progress", "completed"]:
                    access_info["has_access"] = True
                    access_info["access_type"] = "class"
                    access_info["assignments"].append({
                        "type": "class",
                        "id": str(assignment.class_id),
                        "assignment_date": assignment.assignment_date,
                        "due_date": assignment.due_date
                    })
            
            # Check course assignments
            course_assignments = await database_service.get_deck_assignments_by_deck_and_type(
                deck_id, "course"
            )
            for assignment in course_assignments:
                enrollment = await database_service.get_enrollment_by_user_and_course(
                    user_id, str(assignment.course_id)
                )
                if enrollment and enrollment.status in ["enrolled", "in_progress", "completed"]:
                    access_info["has_access"] = True
                    access_info["access_type"] = "course"
                    access_info["assignments"].append({
                        "type": "course",
                        "id": str(assignment.course_id),
                        "assignment_date": assignment.assignment_date,
                        "due_date": assignment.due_date
                    })
            
            # Check lesson assignments
            lesson_assignments = await database_service.get_deck_assignments_by_deck_and_type(
                deck_id, "lesson"
            )
            for assignment in lesson_assignments:
                lesson = await database_service.get_lesson_by_id(str(assignment.lesson_id))
                if lesson:
                    enrollment = await database_service.get_enrollment_by_user_and_course(
                        user_id, str(lesson.course_id)
                    )
                    if enrollment and enrollment.status in ["enrolled", "in_progress", "completed"]:
                        access_info["has_access"] = True
                        access_info["access_type"] = "lesson"
                        access_info["assignments"].append({
                            "type": "lesson",
                            "id": str(assignment.lesson_id),
                            "assignment_date": assignment.assignment_date,
                            "due_date": assignment.due_date
                        })
            
            return access_info
            
        except Exception:
            return {"has_access": False, "access_type": None, "assignments": []}


# Global privacy service instance
privacy_service = PrivacyService()
