"""
Test configuration and shared fixtures.
"""
import os
import asyncio
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Set testing environment
os.environ["TESTING"] = "true"

from app.main import app
from app.core.config import settings
from app.utils.auth import token_blacklist


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Async HTTP client for testing."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(autouse=True)
def clear_token_blacklist():
    """Clear token blacklist before each test."""
    token_blacklist.clear()
    yield
    token_blacklist.clear()


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    test_settings = {
        "SECRET_KEY": "test-secret-key-for-testing-only",
        "ALGORITHM": "HS256",
        "ACCESS_TOKEN_EXPIRE_MINUTES": 30,
        "REFRESH_TOKEN_EXPIRE_DAYS": 7,
    }
    return test_settings


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPassword123!",
        "full_name": "Test User",
        "role": "student"
    }


@pytest.fixture
def sample_admin_data():
    """Sample admin user data for testing."""
    return {
        "email": "admin@example.com",
        "username": "admin",
        "password": "AdminPassword123!",
        "full_name": "Admin User",
        "role": "admin"
    }


@pytest.fixture
def sample_teacher_data():
    """Sample teacher user data for testing."""
    return {
        "email": "teacher@example.com",
        "username": "teacher",
        "password": "TeacherPassword123!",
        "full_name": "Teacher User",
        "role": "teacher"
    }


@pytest.fixture
def valid_token_payload():
    """Valid JWT token payload for testing."""
    from datetime import datetime, timedelta
    
    return {
        "sub": "test-user-id",
        "email": "test@example.com",
        "username": "testuser",
        "role": "student",
        "exp": datetime.utcnow() + timedelta(minutes=30),
        "iat": datetime.utcnow(),
        "type": "access"
    }


@pytest.fixture
def expired_token_payload():
    """Expired JWT token payload for testing."""
    from datetime import datetime, timedelta
    
    return {
        "sub": "test-user-id",
        "email": "test@example.com",
        "username": "testuser",
        "role": "student",
        "exp": datetime.utcnow() - timedelta(minutes=30),  # Expired
        "iat": datetime.utcnow() - timedelta(hours=1),
        "type": "access"
    }


@pytest.fixture
def mock_user():
    """Mock user object for testing."""
    from app.models.enums import UserRole
    from datetime import datetime
    
    class MockUser:
        def __init__(self):
            self.id = "test-user-id"
            self.email = "test@example.com"
            self.username = "testuser"
            self.full_name = "Test User"
            self.role = UserRole.STUDENT
            self.email_verified = False
            self.is_active = True
            self.created_at = datetime.utcnow()
            self.hashed_password = "$2b$12$test.hashed.password"
    
    return MockUser()


@pytest.fixture
def mock_admin_user():
    """Mock admin user object for testing."""
    from app.models.enums import UserRole
    from datetime import datetime
    
    class MockAdminUser:
        def __init__(self):
            self.id = "admin-user-id"
            self.email = "admin@example.com"
            self.username = "admin"
            self.full_name = "Admin User"
            self.role = UserRole.ADMIN
            self.email_verified = True
            self.is_active = True
            self.created_at = datetime.utcnow()
            self.hashed_password = "$2b$12$admin.hashed.password"
    
    return MockAdminUser()


@pytest.fixture
def auth_headers():
    """Generate authentication headers with valid token."""
    from app.utils.auth import create_access_token
    
    token = create_access_token(
        subject="test-user-id",
        additional_claims={
            "email": "test@example.com",
            "username": "testuser",
            "role": "student"
        }
    )
    
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers():
    """Generate admin authentication headers with valid token."""
    from app.utils.auth import create_access_token
    
    token = create_access_token(
        subject="admin-user-id",
        additional_claims={
            "email": "admin@example.com",
            "username": "admin",
            "role": "admin"
        }
    )
    
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def teacher_auth_headers():
    """Generate teacher authentication headers with valid token."""
    from app.utils.auth import create_access_token
    
    token = create_access_token(
        subject="teacher-user-id",
        additional_claims={
            "email": "teacher@example.com",
            "username": "teacher",
            "role": "teacher"
        }
    )
    
    return {"Authorization": f"Bearer {token}"}


# Test database fixtures (when database is implemented)
@pytest.fixture
async def clean_database():
    """Clean database before and after tests."""
    # TODO: Implement database cleanup when database service is ready
    yield
    # Cleanup after test


# Mock database service for testing
@pytest.fixture
def mock_database_service():
    """Mock database service for testing."""
    class MockDatabaseService:
        async def get_user_by_email(self, email: str):
            return None
        
        async def get_user_by_username(self, username: str):
            return None
        
        async def create_user(self, user_data):
            # Return mock created user
            return type('User', (), {
                'id': 'test-user-id',
                'email': user_data.email,
                'username': user_data.username,
                'full_name': user_data.full_name,
                'role': user_data.role,
                'email_verified': False,
                'created_at': user_data.created_at
            })()
        
        async def get_user_by_id(self, user_id: str):
            if user_id == "test-user-id":
                return type('User', (), {
                    'id': 'test-user-id',
                    'email': 'test@example.com',
                    'username': 'testuser',
                    'role': 'student',
                    'is_active': True,
                    'hashed_password': '$2b$12$test.hash'
                })()
            return None
    
    return MockDatabaseService()
