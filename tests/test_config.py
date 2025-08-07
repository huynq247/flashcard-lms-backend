"""
Testing configuration to override production settings.
"""
import os
import pytest
from unittest.mock import patch

# Set testing environment
os.environ["TESTING"] = "true"

# Mock database imports for testing
class MockDatabaseConnection:
    """Mock database connection for testing."""
    
    async def connect_to_mongo(self):
        """Mock MongoDB connection."""
        print("🧪 Using mock database for testing")
        return True
    
    async def close_mongo_connection(self):
        """Mock MongoDB disconnection."""
        print("🧪 Mock database disconnected")
        return True
    
    async def ping_database(self):
        """Mock database ping."""
        return {"status": "ok", "mock": True}

# Create mock instance
mock_db = MockDatabaseConnection()

# Patch database functions during testing
@pytest.fixture(autouse=True)
def mock_database_functions():
    """Automatically mock database functions for all tests."""
    with patch('app.utils.database.connect_to_mongo', side_effect=mock_db.connect_to_mongo):
        with patch('app.utils.database.close_mongo_connection', side_effect=mock_db.close_mongo_connection):
            with patch('app.utils.database.ping_database', side_effect=mock_db.ping_database):
                yield
