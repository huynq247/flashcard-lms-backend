"""
Database service factory - selects appropriate service based on environment.
"""
import os
from typing import Union

from app.services.database_service import database_service as real_database_service
from app.services.database_service_mock import MockDatabaseService


def get_database_service() -> Union[MockDatabaseService, 'RealDatabaseService']:
    """
    Get appropriate service based on environment.
    
    Returns:
        - MockDatabaseService for testing
        - RealDatabaseService for development/production
    """
    # Check if we're running tests
    if os.getenv("TESTING") == "true" or "pytest" in os.environ.get("_", ""):
        from app.services.database_service_mock import database_service as mock_service
        return mock_service
    
    # Use real database service for development/production
    return real_database_service


# Export the selected service
database_service = get_database_service()
