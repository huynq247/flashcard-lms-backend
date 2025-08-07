"""
Simple test to verify Phase 2 Database Schema Implementation
"""
from app.models.user import UserModel, UserCreate, UserResponse
from app.models.deck import DeckModel, DeckCreate, DeckResponse
from app.utils.objectid import PyObjectId
from bson import ObjectId
import json

def test_basic_models():
    """Test basic model creation and validation"""
    
    # Test User Model
    print("Testing User Model...")
    user_create = UserCreate(
        email="test@example.com",
        username="testuser",
        password_hash="hashed_password",
        full_name="Test User"
    )
    print(f"✅ UserCreate: {user_create.email}")
    
    # Test PyObjectId
    print("\nTesting PyObjectId...")
    test_id = ObjectId()
    validated_id = PyObjectId.__class_getitem__(ObjectId)(test_id)
    print(f"✅ PyObjectId validation: {validated_id}")
    
    print("\n🎉 Basic model tests passed!")

if __name__ == "__main__":
    test_basic_models()
