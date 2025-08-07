"""
Simplified tests for authentication utilities.
"""
import pytest
from datetime import datetime, timedelta, UTC

from app.utils.auth import (
    hash_password,
    verify_password,
    validate_password_strength,
    create_access_token,
    create_refresh_token,
    decode_token,
    add_token_to_blacklist,
    is_token_blacklisted,
    clear_token_blacklist
)


class TestPasswordFunctions:
    """Test password hashing and verification."""
    
    def test_hash_password(self):
        """Test password hashing."""
        password = "TestPassword123!"
        hashed = hash_password(password)
        
        assert hashed != password
        assert hashed is not None
        assert len(hashed) > 20  # bcrypt hashes are typically longer
    
    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "TestPassword123!"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "TestPassword123!"
        wrong_password = "WrongPassword123!"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_validate_password_strength_valid(self):
        """Test password strength validation with valid password."""
        valid_passwords = [
            "TestPass123!",
            "MySecure2024@",
            "Complex#Pass1"
        ]
        
        for password in valid_passwords:
            assert validate_password_strength(password) is True
    
    def test_validate_password_strength_invalid(self):
        """Test password strength validation with invalid passwords."""
        invalid_passwords = [
            "short",  # Too short
            "nouppercase123!",  # No uppercase
            "NOLOWERCASE123!",  # No lowercase
            "NoDigits!",  # No digits
            "NoSpecialChars123"  # No special characters
        ]
        
        for password in invalid_passwords:
            assert validate_password_strength(password) is False


class TestJWTTokens:
    """Test JWT token creation and validation."""
    
    def test_create_access_token(self):
        """Test access token creation."""
        data = {"user_id": "test123", "role": "student"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token.split('.')) == 3  # JWT has 3 parts
    
    def test_create_refresh_token(self):
        """Test refresh token creation."""
        data = {"user_id": "test123"}
        token = create_refresh_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token.split('.')) == 3
    
    def test_decode_token_valid(self):
        """Test token decoding with valid token."""
        data = {"user_id": "test123", "role": "student"}
        token = create_access_token(data)
        
        payload = decode_token(token)
        
        assert payload["user_id"] == "test123"
        assert payload["role"] == "student"
        assert "exp" in payload
        assert "iat" in payload
    
    def test_decode_token_with_custom_expiry(self):
        """Test token with custom expiry time."""
        data = {"user_id": "test123"}
        custom_expiry = timedelta(minutes=60)
        token = create_access_token(data, expires_delta=custom_expiry)
        
        payload = decode_token(token)
        
        assert payload["user_id"] == "test123"
        # Check that expiry exists and is in the future
        exp_time = datetime.fromtimestamp(payload["exp"])
        now = datetime.now(UTC).replace(tzinfo=None)  # Remove timezone for comparison
        assert exp_time > now  # Token should not be expired


class TestTokenBlacklist:
    """Test token blacklist functionality."""
    
    def setup_method(self):
        """Clear blacklist before each test."""
        clear_token_blacklist()
    
    def test_add_token_to_blacklist(self):
        """Test adding token to blacklist."""
        token = "sample.jwt.token"
        
        # Initially not blacklisted
        assert is_token_blacklisted(token) is False
        
        # Add to blacklist
        add_token_to_blacklist(token)
        
        # Now should be blacklisted
        assert is_token_blacklisted(token) is True
    
    def test_different_tokens_independent(self):
        """Test that different tokens are handled independently."""
        token1 = "first.jwt.token"
        token2 = "second.jwt.token"
        
        add_token_to_blacklist(token1)
        
        assert is_token_blacklisted(token1) is True
        assert is_token_blacklisted(token2) is False
    
    def test_clear_token_blacklist(self):
        """Test clearing the token blacklist."""
        token = "sample.jwt.token"
        
        add_token_to_blacklist(token)
        assert is_token_blacklisted(token) is True
        
        clear_token_blacklist()
        assert is_token_blacklisted(token) is False


class TestTokenIntegration:
    """Test integrated token workflows."""
    
    def setup_method(self):
        """Clear blacklist before each test."""
        clear_token_blacklist()
    
    def test_full_token_lifecycle(self):
        """Test complete token lifecycle: create -> use -> blacklist."""
        # Create tokens
        user_data = {"user_id": "user123", "email": "test@example.com"}
        access_token = create_access_token(user_data)
        refresh_token = create_refresh_token({"user_id": "user123"})
        
        # Verify tokens work
        access_payload = decode_token(access_token)
        refresh_payload = decode_token(refresh_token)
        
        assert access_payload["user_id"] == "user123"
        assert refresh_payload["user_id"] == "user123"
        
        # Blacklist access token
        add_token_to_blacklist(access_token)
        
        # Access token should be blacklisted, refresh token should not
        assert is_token_blacklisted(access_token) is True
        assert is_token_blacklisted(refresh_token) is False
    
    def test_token_expiry_vs_blacklist(self):
        """Test that blacklist works independently of token expiry."""
        # Create short-lived token
        user_data = {"user_id": "user123"}
        short_expiry = timedelta(seconds=1)
        token = create_access_token(user_data, expires_delta=short_expiry)
        
        # Immediately blacklist
        add_token_to_blacklist(token)
        
        # Should be blacklisted regardless of expiry
        assert is_token_blacklisted(token) is True
        
        # Wait for token to expire
        import time
        time.sleep(2)
        
        # Should still be blacklisted even after expiry
        assert is_token_blacklisted(token) is True


# Test markers
pytest.mark.unit
