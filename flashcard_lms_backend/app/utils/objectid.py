from typing import Annotated
from pydantic import BeforeValidator
from bson import ObjectId

def validate_object_id(v):
    """Validate and convert ObjectId"""
    if isinstance(v, ObjectId):
        return v
    if isinstance(v, str) and ObjectId.is_valid(v):
        return ObjectId(v)
    raise ValueError("Invalid ObjectId")

# Type alias for use in models
PyObjectId = Annotated[ObjectId, BeforeValidator(validate_object_id)]
