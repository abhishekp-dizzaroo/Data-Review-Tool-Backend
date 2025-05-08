from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from bson import ObjectId
from datetime import datetime
from typing import List

from app.db.mongo_db_connection import get_database
from app.model.user import UserCreate, UserResponse, UserInDB, Token, UserUpdate, UserLogin, LoginResponse
from app.auth.auth import (
    get_password_hash, 
    verify_password, 
    create_access_token,
    get_current_user
)

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate):
    """Register a new user"""
    # Get database
    db = get_database()
    
    # Check if username already exists
    if await db.users.find_one({"username": user.username}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    if await db.users.find_one({"email": user.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user document
    now = datetime.utcnow()
    user_dict = UserInDB(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        created_at=now,
        updated_at=now
    )
    
    # Insert user into database
    result = await db.users.insert_one(user_dict.dict(by_alias=True))
    
    # Get created user
    created_user = await db.users.find_one({"_id": result.inserted_id})
    return UserResponse(**created_user)


@router.post("/login", response_model=LoginResponse)
async def login_user(user_data: UserLogin):
    """Login user and return both user data and access token"""
    # Get database
    db = get_database()
    
    # Find user by email
    user = await db.users.find_one({"email": user_data.email})
    
    # Check if user exists and password is correct
    if not user or not verify_password(user_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate access token
    access_token = create_access_token(data={"sub": str(user["_id"])})
    
    # Create token object
    token = Token(access_token=access_token, token_type="bearer")
    
    # Create user response without the hashed password
    user_response = UserResponse(
        _id=user["_id"],
        username=user["username"],
        email=user["email"],
        created_at=user["created_at"]
    )
    
    # Return combined response
    return LoginResponse(user=user_response, token=token)

# @router.post("/login", response_model=Token)
# async def login_user(user_data: UserLogin):
#     """Login user and return access token"""
#     # Get database
#     db = get_database()
    
#     print("Login Data", user_data)
#     # Find user by email
#     user = await db.users.find_one({"email": user_data.email})
    
#     # Check if user exists and password is correct
#     if not user or not verify_password(user_data.password, user["hashed_password"]):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect email or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     # Generate access token
#     access_token = create_access_token(data={"sub": str(user["_id"])})
#     return Token(access_token=access_token, token_type="bearer")




# Option 2: Keep OAuth2 but fix the form field handling
# @router.post("/login", response_model=Token)
# async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
#     """Login user and return access token"""
#     # Get database
#     db = get_database()
    
#     print("Login Data", form_data)
#     # Find user by email (OAuth2PasswordRequestForm uses username field)
#     user = await db.users.find_one({"email": form_data.username})  # Username field contains email
    
#     # Check if user exists and password is correct
#     if not user or not verify_password(form_data.password, user["hashed_password"]):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect email or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     # Generate access token
#     access_token = create_access_token(data={"sub": str(user["_id"])})
#     return Token(access_token=access_token, token_type="bearer")



@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_user_info(
    user_update: UserUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update current user information"""
    # Get database
    db = get_database()
    
    # Filter out None values
    update_data = {k: v for k, v in user_update.dict().items() if v is not None}
    
    if not update_data:
        # No updates provided
        return current_user
    
    # Handle password update
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    # Add updated_at timestamp
    update_data["updated_at"] = datetime.utcnow()
    
    # Update user in database
    await db.users.update_one(
        {"_id": ObjectId(current_user.id)},
        {"$set": update_data}
    )
    
    # Get updated user
    updated_user = await db.users.find_one({"_id": ObjectId(current_user.id)})
    
    return UserResponse(**updated_user)

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0, 
    limit: int = 10,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get list of users (requires authentication)"""
    # Get database
    db = get_database()
    
    # Get users from database
    users = await db.users.find().skip(skip).limit(limit).to_list(length=limit)
    
    return [UserResponse(**user) for user in users]

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get user by ID (requires authentication)"""
    # Get database
    db = get_database()
    
    # Check if valid ObjectId
    try:
        user_obj_id = ObjectId(user_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    # Get user from database
    user = await db.users.find_one({"_id": user_obj_id})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(**user)