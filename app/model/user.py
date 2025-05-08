from pydantic import BaseModel, EmailStr, Field, field_serializer
from typing import Optional, Annotated
from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException, status, Depends
from pydantic.json_schema import JsonSchemaMode

# Custom type for ObjectId handling in Pydantic v2
class PyObjectId(ObjectId):
    # For Pydantic v2, we use the correct schema pattern
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        from pydantic_core import core_schema
        return core_schema.union_schema([
            core_schema.is_instance_schema(ObjectId),
            core_schema.chain_schema([
                core_schema.str_schema(),  # Use str_schema instead of string_schema
                core_schema.no_info_plain_validator_function(cls.validate),
            ]),
        ])
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

# User registration request model
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

# User login request model
class UserLogin(BaseModel):
    email: str
    password: str

# User response model (for API responses)
class UserResponse(BaseModel):
    id: PyObjectId = Field(alias="_id")
    username: str
    email: EmailStr
    created_at: datetime

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }

    # Correct way to serialize ObjectId
    @field_serializer('id')
    def serialize_id(self, id: PyObjectId) -> str:
        return str(id)

# Token model
class Token(BaseModel):
    access_token: str
    token_type: str

# Combined response model for login
class LoginResponse(BaseModel):
    user: UserResponse
    token: Token
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }

# User in database model (for internal use)
class UserInDB(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    username: str
    email: EmailStr
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "example": {
                "username": "johndoe",
                "email": "john.doe@example.com",
            }
        }
    }
    
    # Serializer for ObjectId
    @field_serializer('id')
    def serialize_id(self, id: PyObjectId) -> str:
        return str(id)

# User update model
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None