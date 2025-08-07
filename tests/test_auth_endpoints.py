"""
Tests for authentication API endpoints.
"""
import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient

from app.main import app


class TestRegistrationEndpoint:
    """Test user registration endpoint."""
    
    @pytest.mark.asyncio
    async def test_register_success(self, async_client: AsyncClient, sample_user_data):
        """Test successful user registration."""
        with patch('app.services.auth_service.auth_service.register_user') as mock_register:
            # Mock successful registration
            mock_register.return_value = {
                "user_id": "test-user-id",
                "email": sample_user_data["email"],
                "username": sample_user_data["username"],
                "full_name": sample_user_data["full_name"],
                "role": sample_user_data["role"],
                "email_verified": False,
                "created_at": "2025-08-07T18:31:00Z",
                "message": "Registration successful"
            }
            
            response = await async_client.post("/api/v1/auth/register", json=sample_user_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["email"] == sample_user_data["email"]
            assert data["username"] == sample_user_data["username"]
            assert data["message"] == "Registration successful"
    
    @pytest.mark.asyncio
    async def test_register_invalid_email(self, async_client: AsyncClient):
        """Test registration with invalid email."""
        invalid_data = {
            "email": "invalid-email",
            "username": "testuser",
            "password": "TestPassword123!",
            "full_name": "Test User",
            "role": "student"
        }
        
        response = await async_client.post("/api/v1/auth/register", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_register_weak_password(self, async_client: AsyncClient):
        """Test registration with weak password."""
        weak_password_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "weak",  # Too weak
            "full_name": "Test User",
            "role": "student"
        }
        
        response = await async_client.post("/api/v1/auth/register", json=weak_password_data)
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, async_client: AsyncClient, sample_user_data):
        """Test registration with duplicate email."""
        with patch('app.services.auth_service.auth_service.register_user') as mock_register:
            from fastapi import HTTPException
            
            # Mock duplicate email error
            mock_register.side_effect = HTTPException(
                status_code=400,
                detail="Email already registered"
            )
            
            response = await async_client.post("/api/v1/auth/register", json=sample_user_data)
            assert response.status_code == 400


class TestLoginEndpoint:
    """Test user login endpoint."""
    
    @pytest.mark.asyncio
    async def test_login_success(self, async_client: AsyncClient):
        """Test successful login."""
        with patch('app.services.auth_service.auth_service.login_user') as mock_login:
            # Mock successful login
            mock_login.return_value = {
                "access_token": "test.access.token",
                "refresh_token": "test.refresh.token",
                "token_type": "bearer",
                "expires_in": 1800,
                "user": {
                    "id": "test-user-id",
                    "email": "test@example.com",
                    "username": "testuser",
                    "full_name": "Test User",
                    "role": "student",
                    "email_verified": False,
                    "is_active": True,
                    "created_at": "2025-08-07T18:31:00Z"
                }
            }
            
            login_data = {
                "email": "test@example.com",
                "password": "TestPassword123!"
            }
            
            response = await async_client.post("/api/v1/auth/login", json=login_data)
            
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data
            assert data["token_type"] == "bearer"
            assert data["user"]["email"] == login_data["email"]
    
    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, async_client: AsyncClient):
        """Test login with invalid credentials."""
        with patch('app.services.auth_service.auth_service.login_user') as mock_login:
            from fastapi import HTTPException
            
            # Mock invalid credentials
            mock_login.side_effect = HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )
            
            login_data = {
                "email": "test@example.com",
                "password": "WrongPassword"
            }
            
            response = await async_client.post("/api/v1/auth/login", json=login_data)
            assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_login_form_data(self, async_client: AsyncClient):
        """Test OAuth2 compatible login with form data."""
        with patch('app.services.auth_service.auth_service.login_user') as mock_login:
            # Mock successful login
            mock_login.return_value = {
                "access_token": "test.access.token",
                "refresh_token": "test.refresh.token",
                "token_type": "bearer",
                "expires_in": 1800,
                "user": {
                    "id": "test-user-id",
                    "email": "test@example.com",
                    "username": "testuser",
                    "full_name": "Test User",
                    "role": "student",
                    "email_verified": False,
                    "is_active": True,
                    "created_at": "2025-08-07T18:31:00Z"
                }
            }
            
            form_data = {
                "username": "test@example.com",  # OAuth2 uses username field for email
                "password": "TestPassword123!"
            }
            
            response = await async_client.post(
                "/api/v1/auth/login/form",
                data=form_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data


class TestTokenRefreshEndpoint:
    """Test token refresh endpoint."""
    
    @pytest.mark.asyncio
    async def test_refresh_token_success(self, async_client: AsyncClient):
        """Test successful token refresh."""
        with patch('app.services.auth_service.auth_service.refresh_token') as mock_refresh:
            # Mock successful refresh
            mock_refresh.return_value = {
                "access_token": "new.access.token",
                "refresh_token": "new.refresh.token",
                "token_type": "bearer",
                "expires_in": 1800,
                "user": {
                    "id": "test-user-id",
                    "email": "test@example.com",
                    "username": "testuser",
                    "full_name": "Test User",
                    "role": "student",
                    "email_verified": False,
                    "is_active": True,
                    "created_at": "2025-08-07T18:31:00Z"
                }
            }
            
            refresh_data = {
                "refresh_token": "valid.refresh.token"
            }
            
            response = await async_client.post("/api/v1/auth/refresh", json=refresh_data)
            
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data
    
    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, async_client: AsyncClient):
        """Test token refresh with invalid token."""
        with patch('app.services.auth_service.auth_service.refresh_token') as mock_refresh:
            from fastapi import HTTPException
            
            # Mock invalid refresh token
            mock_refresh.side_effect = HTTPException(
                status_code=401,
                detail="Invalid refresh token"
            )
            
            refresh_data = {
                "refresh_token": "invalid.refresh.token"
            }
            
            response = await async_client.post("/api/v1/auth/refresh", json=refresh_data)
            assert response.status_code == 401


class TestLogoutEndpoint:
    """Test logout endpoint."""
    
    @pytest.mark.asyncio
    async def test_logout_success(self, async_client: AsyncClient, auth_headers):
        """Test successful logout."""
        with patch('app.services.auth_service.auth_service.logout_user') as mock_logout:
            # Mock successful logout
            mock_logout.return_value = {"message": "Successfully logged out"}
            
            logout_data = {
                "access_token": "test.access.token",
                "refresh_token": "test.refresh.token"
            }
            
            response = await async_client.post(
                "/api/v1/auth/logout",
                json=logout_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Successfully logged out"


class TestPasswordManagement:
    """Test password change and reset endpoints."""
    
    @pytest.mark.asyncio
    async def test_change_password_success(self, async_client: AsyncClient, auth_headers):
        """Test successful password change."""
        with patch('app.core.deps.get_current_active_user') as mock_user:
            with patch('app.core.security.SecurityUtils.verify_password') as mock_verify:
                with patch('app.services.database_service.database_service.update_user_password') as mock_update:
                    # Mock current user
                    mock_user.return_value = type('User', (), {
                        'id': 'test-user-id',
                        'hashed_password': 'old.hashed.password'
                    })()
                    
                    # Mock password verification
                    mock_verify.return_value = True
                    
                    # Mock password update
                    mock_update.return_value = None
                    
                    password_data = {
                        "current_password": "OldPassword123!",
                        "new_password": "NewPassword123!"
                    }
                    
                    response = await async_client.post(
                        "/api/v1/auth/change-password",
                        json=password_data,
                        headers=auth_headers
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert "Password changed successfully" in data["message"]
    
    @pytest.mark.asyncio
    async def test_admin_reset_password(self, async_client: AsyncClient, admin_auth_headers):
        """Test admin password reset."""
        with patch('app.services.auth_service.auth_service.reset_password_admin') as mock_reset:
            # Mock successful reset
            mock_reset.return_value = {
                "user_id": "target-user-id",
                "message": "Password reset successfully",
                "reset_by": "admin-user-id",
                "reset_at": "2025-08-07T18:31:00Z",
                "force_change_required": True
            }
            
            reset_data = {
                "new_password": "NewPassword123!",
                "reset_reason": "User forgot password",
                "force_change_on_login": True
            }
            
            response = await async_client.put(
                "/api/v1/auth/admin/users/target-user-id/reset-password",
                json=reset_data,
                headers=admin_auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Password reset successfully"


class TestUserInfoEndpoint:
    """Test user information endpoint."""
    
    @pytest.mark.asyncio
    async def test_get_current_user_info(self, async_client: AsyncClient, auth_headers):
        """Test getting current user information."""
        with patch('app.core.deps.get_current_active_user') as mock_user:
            # Mock current user
            mock_user.return_value = type('User', (), {
                'id': 'test-user-id',
                'email': 'test@example.com',
                'username': 'testuser',
                'full_name': 'Test User',
                'role': 'student',
                'email_verified': False,
                'created_at': '2025-08-07T18:31:00Z'
            })()
            
            response = await async_client.get(
                "/api/v1/auth/me",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["email"] == "test@example.com"
            assert data["username"] == "testuser"
    
    @pytest.mark.asyncio
    async def test_get_user_info_unauthorized(self, async_client: AsyncClient):
        """Test getting user info without authentication."""
        response = await async_client.get("/api/v1/auth/me")
        assert response.status_code == 401


class TestHealthCheckEndpoint:
    """Test authentication health check."""
    
    @pytest.mark.asyncio
    async def test_auth_health_check(self, async_client: AsyncClient):
        """Test authentication service health check."""
        response = await async_client.get("/api/v1/auth/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "authentication"


# Pytest markers
pytest.mark.integration
pytest.mark.auth
