"""
Integration tests for role-based access control and privacy features.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient

from app.models.enums import UserRole, DeckPrivacyLevel
from app.main import app


class TestRoleBasedAccessControl:
    """Test role-based access control across endpoints."""
    
    @pytest.mark.asyncio
    async def test_student_access_permissions(self, async_client: AsyncClient, student_auth_headers):
        """Test student role access permissions."""
        with patch('app.core.deps.get_current_active_user') as mock_user:
            # Mock student user
            mock_user.return_value = type('User', (), {
                'id': 'student-user-id',
                'role': UserRole.STUDENT,
                'email': 'student@example.com'
            })()
            
            # Test allowed endpoints
            response = await async_client.get(
                "/api/v1/decks/my-decks",
                headers=student_auth_headers
            )
            # Should not be 403 (forbidden)
            assert response.status_code != 403
            
            # Test restricted admin endpoints
            with patch('app.core.deps.require_admin') as mock_admin:
                from fastapi import HTTPException
                mock_admin.side_effect = HTTPException(status_code=403, detail="Admin access required")
                
                response = await async_client.get(
                    "/api/v1/admin/users",
                    headers=student_auth_headers
                )
                assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_teacher_access_permissions(self, async_client: AsyncClient, teacher_auth_headers):
        """Test teacher role access permissions."""
        with patch('app.core.deps.get_current_active_user') as mock_user:
            # Mock teacher user
            mock_user.return_value = type('User', (), {
                'id': 'teacher-user-id',
                'role': UserRole.TEACHER,
                'email': 'teacher@example.com'
            })()
            
            # Test class management access
            response = await async_client.get(
                "/api/v1/classes/my-classes",
                headers=teacher_auth_headers
            )
            assert response.status_code != 403
            
            # Test deck creation permissions
            deck_data = {
                "title": "Teacher's Deck",
                "description": "Created by teacher",
                "privacy_level": DeckPrivacyLevel.CLASS.value
            }
            
            response = await async_client.post(
                "/api/v1/decks",
                json=deck_data,
                headers=teacher_auth_headers
            )
            assert response.status_code != 403
    
    @pytest.mark.asyncio
    async def test_admin_full_access(self, async_client: AsyncClient, admin_auth_headers):
        """Test admin role has full access."""
        with patch('app.core.deps.get_current_active_user') as mock_user:
            # Mock admin user
            mock_user.return_value = type('User', (), {
                'id': 'admin-user-id',
                'role': UserRole.ADMIN,
                'email': 'admin@example.com'
            })()
            
            # Test admin-only endpoints
            response = await async_client.get(
                "/api/v1/admin/users",
                headers=admin_auth_headers
            )
            assert response.status_code != 403
            
            # Test system management
            response = await async_client.get(
                "/api/v1/admin/system/stats",
                headers=admin_auth_headers
            )
            assert response.status_code != 403


class TestDeckPrivacySystem:
    """Test deck privacy access control."""
    
    @pytest.mark.asyncio
    async def test_private_deck_access(self, async_client: AsyncClient, student_auth_headers):
        """Test private deck access control."""
        with patch('app.services.privacy_service.privacy_service.check_deck_access') as mock_access:
            with patch('app.services.database_service.database_service.get_deck') as mock_get_deck:
                # Mock private deck
                mock_deck = MagicMock()
                mock_deck.id = "private-deck-id"
                mock_deck.owner_id = "other-user-id"  # Different from current user
                mock_deck.privacy_level = DeckPrivacyLevel.PRIVATE
                mock_get_deck.return_value = mock_deck
                
                # Mock access denied
                mock_access.return_value = False
                
                response = await async_client.get(
                    "/api/v1/decks/private-deck-id",
                    headers=student_auth_headers
                )
                
                # Should be forbidden for non-owner
                assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_public_deck_access(self, async_client: AsyncClient, student_auth_headers):
        """Test public deck access."""
        with patch('app.services.privacy_service.privacy_service.check_deck_access') as mock_access:
            with patch('app.services.database_service.database_service.get_deck') as mock_get_deck:
                # Mock public deck
                mock_deck = MagicMock()
                mock_deck.id = "public-deck-id"
                mock_deck.owner_id = "other-user-id"
                mock_deck.privacy_level = DeckPrivacyLevel.PUBLIC
                mock_get_deck.return_value = mock_deck
                
                # Mock access allowed
                mock_access.return_value = True
                
                response = await async_client.get(
                    "/api/v1/decks/public-deck-id",
                    headers=student_auth_headers
                )
                
                # Should be accessible to anyone
                assert response.status_code != 403
    
    @pytest.mark.asyncio
    async def test_class_deck_access_with_assignment(self, async_client: AsyncClient, student_auth_headers):
        """Test class deck access with proper assignment."""
        with patch('app.services.privacy_service.privacy_service.check_deck_access') as mock_access:
            with patch('app.services.database_service.database_service.get_deck') as mock_get_deck:
                with patch('app.core.deps.get_current_active_user') as mock_user:
                    # Mock student user
                    mock_user.return_value = type('User', (), {
                        'id': 'student-user-id',
                        'role': UserRole.STUDENT
                    })()
                    
                    # Mock class deck
                    mock_deck = MagicMock()
                    mock_deck.id = "class-deck-id"
                    mock_deck.owner_id = "teacher-user-id"
                    mock_deck.privacy_level = DeckPrivacyLevel.CLASS
                    mock_get_deck.return_value = mock_deck
                    
                    # Mock access allowed (student is in class)
                    mock_access.return_value = True
                    
                    response = await async_client.get(
                        "/api/v1/decks/class-deck-id",
                        headers=student_auth_headers
                    )
                    
                    # Should be accessible to assigned students
                    assert response.status_code != 403
    
    @pytest.mark.asyncio
    async def test_class_deck_access_without_assignment(self, async_client: AsyncClient, student_auth_headers):
        """Test class deck access without proper assignment."""
        with patch('app.services.privacy_service.privacy_service.check_deck_access') as mock_access:
            with patch('app.services.database_service.database_service.get_deck') as mock_get_deck:
                # Mock class deck
                mock_deck = MagicMock()
                mock_deck.id = "class-deck-id"
                mock_deck.owner_id = "teacher-user-id"
                mock_deck.privacy_level = DeckPrivacyLevel.CLASS
                mock_get_deck.return_value = mock_deck
                
                # Mock access denied (student not in class)
                mock_access.return_value = False
                
                response = await async_client.get(
                    "/api/v1/decks/class-deck-id",
                    headers=student_auth_headers
                )
                
                # Should be forbidden for non-assigned students
                assert response.status_code == 403


class TestResourcePermissions:
    """Test resource-specific permissions."""
    
    @pytest.mark.asyncio
    async def test_deck_modification_by_owner(self, async_client: AsyncClient, auth_headers):
        """Test deck modification by owner."""
        with patch('app.core.deps.get_current_active_user') as mock_user:
            with patch('app.services.database_service.database_service.get_deck') as mock_get_deck:
                # Mock current user as deck owner
                mock_user.return_value = type('User', (), {
                    'id': 'owner-user-id',
                    'role': UserRole.STUDENT
                })()
                
                # Mock owned deck
                mock_deck = MagicMock()
                mock_deck.id = "owned-deck-id"
                mock_deck.owner_id = "owner-user-id"
                mock_get_deck.return_value = mock_deck
                
                update_data = {
                    "title": "Updated Deck Title",
                    "description": "Updated description"
                }
                
                response = await async_client.put(
                    "/api/v1/decks/owned-deck-id",
                    json=update_data,
                    headers=auth_headers
                )
                
                # Should be allowed for owner
                assert response.status_code != 403
    
    @pytest.mark.asyncio
    async def test_deck_modification_by_non_owner(self, async_client: AsyncClient, auth_headers):
        """Test deck modification by non-owner."""
        with patch('app.core.deps.get_current_active_user') as mock_user:
            with patch('app.services.database_service.database_service.get_deck') as mock_get_deck:
                # Mock current user as non-owner
                mock_user.return_value = type('User', (), {
                    'id': 'non-owner-user-id',
                    'role': UserRole.STUDENT
                })()
                
                # Mock deck owned by someone else
                mock_deck = MagicMock()
                mock_deck.id = "other-deck-id"
                mock_deck.owner_id = "other-user-id"
                mock_get_deck.return_value = mock_deck
                
                update_data = {
                    "title": "Attempted Update",
                    "description": "Should not work"
                }
                
                response = await async_client.put(
                    "/api/v1/decks/other-deck-id",
                    json=update_data,
                    headers=auth_headers
                )
                
                # Should be forbidden for non-owner
                assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_card_creation_in_owned_deck(self, async_client: AsyncClient, auth_headers):
        """Test card creation in owned deck."""
        with patch('app.core.deps.get_current_active_user') as mock_user:
            with patch('app.services.database_service.database_service.get_deck') as mock_get_deck:
                # Mock current user as deck owner
                mock_user.return_value = type('User', (), {
                    'id': 'owner-user-id',
                    'role': UserRole.STUDENT
                })()
                
                # Mock owned deck
                mock_deck = MagicMock()
                mock_deck.id = "owned-deck-id"
                mock_deck.owner_id = "owner-user-id"
                mock_get_deck.return_value = mock_deck
                
                card_data = {
                    "front_content": "Question",
                    "back_content": "Answer",
                    "card_type": "basic"
                }
                
                response = await async_client.post(
                    "/api/v1/decks/owned-deck-id/cards",
                    json=card_data,
                    headers=auth_headers
                )
                
                # Should be allowed for deck owner
                assert response.status_code != 403


class TestClassAssignmentAccess:
    """Test class assignment-based access control."""
    
    @pytest.mark.asyncio
    async def test_teacher_access_to_class(self, async_client: AsyncClient, teacher_auth_headers):
        """Test teacher access to their class."""
        with patch('app.core.deps.get_current_active_user') as mock_user:
            with patch('app.services.database_service.database_service.get_class') as mock_get_class:
                # Mock teacher user
                mock_user.return_value = type('User', (), {
                    'id': 'teacher-user-id',
                    'role': UserRole.TEACHER
                })()
                
                # Mock class owned by teacher
                mock_class = MagicMock()
                mock_class.id = "teacher-class-id"
                mock_class.teacher_id = "teacher-user-id"
                mock_get_class.return_value = mock_class
                
                response = await async_client.get(
                    "/api/v1/classes/teacher-class-id",
                    headers=teacher_auth_headers
                )
                
                # Should be accessible to class teacher
                assert response.status_code != 403
    
    @pytest.mark.asyncio
    async def test_student_access_to_enrolled_class(self, async_client: AsyncClient, student_auth_headers):
        """Test student access to enrolled class."""
        with patch('app.core.deps.get_current_active_user') as mock_user:
            with patch('app.services.database_service.database_service.is_student_in_class') as mock_enrollment:
                # Mock student user
                mock_user.return_value = type('User', (), {
                    'id': 'student-user-id',
                    'role': UserRole.STUDENT
                })()
                
                # Mock enrollment
                mock_enrollment.return_value = True
                
                response = await async_client.get(
                    "/api/v1/classes/enrolled-class-id/materials",
                    headers=student_auth_headers
                )
                
                # Should be accessible to enrolled student
                assert response.status_code != 403
    
    @pytest.mark.asyncio
    async def test_student_access_to_non_enrolled_class(self, async_client: AsyncClient, student_auth_headers):
        """Test student access to non-enrolled class."""
        with patch('app.core.deps.get_current_active_user') as mock_user:
            with patch('app.services.database_service.database_service.is_student_in_class') as mock_enrollment:
                # Mock student user
                mock_user.return_value = type('User', (), {
                    'id': 'student-user-id',
                    'role': UserRole.STUDENT
                })()
                
                # Mock no enrollment
                mock_enrollment.return_value = False
                
                response = await async_client.get(
                    "/api/v1/classes/other-class-id/materials",
                    headers=student_auth_headers
                )
                
                # Should be forbidden for non-enrolled student
                assert response.status_code == 403


class TestSecurityMiddleware:
    """Test security middleware integration."""
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, async_client: AsyncClient):
        """Test rate limiting middleware."""
        # Make multiple rapid requests
        responses = []
        for i in range(10):
            response = await async_client.post("/api/v1/auth/login", json={
                "email": "test@example.com",
                "password": "password"
            })
            responses.append(response.status_code)
        
        # Should eventually hit rate limit (429)
        assert 429 in responses
    
    @pytest.mark.asyncio
    async def test_cors_headers(self, async_client: AsyncClient):
        """Test CORS headers are present."""
        response = await async_client.options("/api/v1/auth/health")
        
        # Check for CORS headers
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
    
    @pytest.mark.asyncio
    async def test_security_headers(self, async_client: AsyncClient):
        """Test security headers are present."""
        response = await async_client.get("/api/v1/auth/health")
        
        # Check for security headers
        headers = response.headers
        assert "x-content-type-options" in headers
        assert "x-frame-options" in headers


# Pytest markers
pytest.mark.integration
pytest.mark.permissions
pytest.mark.privacy
