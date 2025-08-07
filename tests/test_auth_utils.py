"""
Tests for authentication utilities and JWT functionality.
"""
import pytest
from datetime import datetime, timedelta

from app.utils.auth import (
    verify_password,
    hash_password,
    validate_password_strength,
    create_access_token,
    create_refresh_token,
    decode_token,
    decode_token,
    is_token_expired,
    get_token_expiry,
    TokenBlacklist,
    logout_user,
    check_token_blacklist,
    generate_password_reset_token,
    verify_password_reset_token,
    generate_email_verification_token,
    verify_email_verification_token,
    create_api_key,
    verify_api_key
)


class TestPasswordFunctions:
    """Test password-related functions."""
    
    def test_password_hashing(self):
        """Test password hashing and verification."""
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        
        # Verify correct password
        assert verify_password(password, hashed) is True
        
        # Verify incorrect password
        assert verify_password("WrongPassword", hashed) is False
    
    def test_password_strength_validation(self):
        """Test password strength validation."""
        # Valid strong password
        valid_password = "StrongPass123!"
        is_valid, message = validate_password_strength(valid_password)
        assert is_valid is True
        assert message == "Password is strong"
        
        # Too short
        short_password = "Short1!"
        is_valid, message = validate_password_strength(short_password)
        assert is_valid is False
        assert "at least 8 characters" in message
        
        # No lowercase
        no_lower = "UPPERCASE123!"
        is_valid, message = validate_password_strength(no_lower)
        assert is_valid is False
        assert "lowercase letter" in message
        
        # No uppercase
        no_upper = "lowercase123!"
        is_valid, message = validate_password_strength(no_upper)
        assert is_valid is False
        assert "uppercase letter" in message
        
        # No digit
        no_digit = "NoDigitPass!"
        is_valid, message = validate_password_strength(no_digit)
        assert is_valid is False
        assert "digit" in message
        
        # No special character
        no_special = "NoSpecialChar123"
        is_valid, message = validate_password_strength(no_special)
        assert is_valid is False
        assert "special character" in message
    
    def test_generate_secure_password(self):
        """Test secure password generation."""
        password = generate_secure_password()
        
        # Check length
        assert len(password) == 12  # default length
        
        # Custom length
        custom_password = generate_secure_password(16)
        assert len(custom_password) == 16
        
        # Should be strong
        is_valid, _ = validate_password_strength(password)
        assert is_valid is True


class TestJWTTokens:
    """Test JWT token functions."""
    
    def test_create_access_token(self):
        """Test access token creation."""
        user_id = "test-user-123"
        token = create_access_token(subject=user_id)
        
        assert token is not None
        assert isinstance(token, str)
        
        # Should be able to decode
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == user_id
        assert payload["type"] == "access"
    
    def test_create_refresh_token(self):
        """Test refresh token creation."""
        user_id = "test-user-123"
        token = create_refresh_token(subject=user_id)
        
        assert token is not None
        assert isinstance(token, str)
        
        # Should be able to decode
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == user_id
        assert payload["type"] == "refresh"
    
    def test_verify_token_valid(self):
        """Test token verification with valid token."""
        user_id = "test-user-123"
        token = create_access_token(subject=user_id)
        
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == user_id
        assert payload["type"] == "access"
    
    def test_verify_token_invalid(self):
        """Test token verification with invalid token."""
        invalid_token = "invalid.token.here"
        payload = verify_token(invalid_token)
        assert payload is None
    
    def test_verify_token_wrong_type(self):
        """Test token verification with wrong token type."""
        user_id = "test-user-123"
        access_token = create_access_token(subject=user_id)
        
        # Try to verify as refresh token
        payload = verify_token(access_token, token_type="refresh")
        assert payload is None
    
    def test_get_subject_from_token(self):
        """Test extracting subject from token."""
        user_id = "test-user-123"
        token = create_access_token(subject=user_id)
        
        extracted_user_id = get_subject_from_token(token)
        assert extracted_user_id == user_id
    
    def test_is_token_expired(self):
        """Test token expiration checking."""
        # Create token with short expiry
        user_id = "test-user-123"
        short_expiry = timedelta(seconds=-1)  # Already expired
        expired_token = create_access_token(
            subject=user_id, 
            expires_delta=short_expiry
        )
        
        assert is_token_expired(expired_token) is True
        
        # Valid token
        valid_token = create_access_token(subject=user_id)
        assert is_token_expired(valid_token) is False
    
    def test_get_token_expiry(self):
        """Test getting token expiry datetime."""
        user_id = "test-user-123"
        token = create_access_token(subject=user_id)
        
        expiry = get_token_expiry(token)
        assert expiry is not None
        assert isinstance(expiry, datetime)
        assert expiry > datetime.utcnow()


class TestTokenBlacklist:
    """Test token blacklist functionality."""
    
    def test_token_blacklist_operations(self):
        """Test basic blacklist operations."""
        blacklist = TokenBlacklist()
        token = "test.token.123"
        
        # Initially not blacklisted
        assert blacklist.is_blacklisted(token) is False
        assert blacklist.size() == 0
        
        # Add to blacklist
        blacklist.add_token(token)
        assert blacklist.is_blacklisted(token) is True
        assert blacklist.size() == 1
        
        # Remove from blacklist
        blacklist.remove_token(token)
        assert blacklist.is_blacklisted(token) is False
        assert blacklist.size() == 0
    
    def test_logout_user(self):
        """Test user logout functionality."""
        access_token = "access.token.123"
        refresh_token = "refresh.token.123"
        
        result = logout_user(access_token, refresh_token)
        
        assert result["message"] == "Successfully logged out"
        assert check_token_blacklist(access_token) is True
        assert check_token_blacklist(refresh_token) is True
    
    def test_logout_user_access_only(self):
        """Test user logout with access token only."""
        access_token = "access.token.123"
        
        result = logout_user(access_token)
        
        assert result["message"] == "Successfully logged out"
        assert check_token_blacklist(access_token) is True


class TestSpecialTokens:
    """Test special token types (password reset, email verification, API keys)."""
    
    def test_password_reset_token(self):
        """Test password reset token generation and verification."""
        user_id = "test-user-123"
        
        # Generate token
        reset_token = generate_password_reset_token(user_id)
        assert reset_token is not None
        
        # Verify token
        verified_user_id = verify_password_reset_token(reset_token)
        assert verified_user_id == user_id
        
        # Invalid token
        invalid_verified = verify_password_reset_token("invalid.token")
        assert invalid_verified is None
    
    def test_email_verification_token(self):
        """Test email verification token generation and verification."""
        email = "test@example.com"
        
        # Generate token
        verification_token = generate_email_verification_token(email)
        assert verification_token is not None
        
        # Verify token
        verified_email = verify_email_verification_token(verification_token)
        assert verified_email == email
        
        # Invalid token
        invalid_verified = verify_email_verification_token("invalid.token")
        assert invalid_verified is None
    
    def test_api_key(self):
        """Test API key generation and verification."""
        user_id = "test-user-123"
        key_name = "Test API Key"
        
        # Create API key
        api_key = create_api_key(user_id, key_name)
        assert api_key is not None
        
        # Verify API key
        payload = verify_api_key(api_key)
        assert payload is not None
        assert payload["sub"] == user_id
        assert payload["name"] == key_name
        assert payload["type"] == "api_key"
        assert "key_id" in payload
        
        # Invalid API key
        invalid_payload = verify_api_key("invalid.api.key")
        assert invalid_payload is None


class TestTokenValidation:
    """Test comprehensive token validation scenarios."""
    
    def test_token_with_additional_claims(self):
        """Test token creation with additional claims."""
        user_id = "test-user-123"
        additional_claims = {
            "email": "test@example.com",
            "role": "student",
            "permissions": ["read", "write"]
        }
        
        token = create_access_token(
            subject=user_id,
            additional_claims=additional_claims
        )
        
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == user_id
        assert payload["email"] == additional_claims["email"]
        assert payload["role"] == additional_claims["role"]
        assert payload["permissions"] == additional_claims["permissions"]
    
    def test_custom_expiry(self):
        """Test token creation with custom expiry."""
        user_id = "test-user-123"
        custom_expiry = timedelta(minutes=10)
        
        token = create_access_token(
            subject=user_id,
            expires_delta=custom_expiry
        )
        
        payload = verify_token(token)
        assert payload is not None
        
        # Check that expiry is approximately 10 minutes from now
        exp_time = datetime.fromtimestamp(payload["exp"])
        expected_exp = datetime.utcnow() + custom_expiry
        
        # Allow 5 second tolerance
        time_diff = abs((exp_time - expected_exp).total_seconds())
        assert time_diff < 5


# Pytest markers for different test categories
pytest.mark.unit
pytest.mark.auth
