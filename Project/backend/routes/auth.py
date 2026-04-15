from fastapi import APIRouter, HTTPException, Response, Request, status, Depends
from pydantic import BaseModel, EmailStr
from core.database import users_collection, refresh_tokens_collection
from core.security import verify_password, get_password_hash, create_access_token, hash_token, REFRESH_TOKEN_EXPIRE_DAYS
import secrets
from datetime import datetime, timedelta

router = APIRouter()

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister):
    # Check if user exists
    existing_user = await users_collection.find_one({"$or": [{"username": user.username}, {"email": user.email}]})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or Email already registered")
        
    hashed_password = get_password_hash(user.password)
    user_dict = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password
    }
    
    await users_collection.insert_one(user_dict)
    return {"success": True, "message": "User created successfully"}

@router.post("/login", response_model=TokenResponse)
async def login(user_credentials: UserLogin, response: Response):
    user = await users_collection.find_one({"email": user_credentials.email})
    if not user or not verify_password(user_credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
        
    user_id_str = str(user["_id"])
    
    # Create tokens
    access_token = create_access_token(subject=user_id_str)
    
    # Generate secure random refresh token
    raw_refresh_token = secrets.token_urlsafe(64)
    hashed_refresh = hash_token(raw_refresh_token)
    
    expiry = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    # Store in DB
    await refresh_tokens_collection.insert_one({
        "user_id": user_id_str,
        "token_hash": hashed_refresh,
        "expiry": expiry,
        "created_at": datetime.utcnow()
    })
    
    # Set HttpOnly Cookie
    response.set_cookie(
        key="refresh_token",
        value=raw_refresh_token,
        httponly=True,
        secure=False, # Change to True in HTTPS environment
        samesite="lax",
        expires=int(expiry.timestamp())
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: Request, response: Response):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
        
    hashed_refresh = hash_token(token)
    
    # Find token in DB
    db_token = await refresh_tokens_collection.find_one({"token_hash": hashed_refresh})
    
    if not db_token:
        response.delete_cookie("refresh_token")
        raise HTTPException(status_code=401, detail="Invalid refresh token")
        
    if db_token["expiry"] < datetime.utcnow():
        await refresh_tokens_collection.delete_one({"_id": db_token["_id"]})
        response.delete_cookie("refresh_token")
        raise HTTPException(status_code=401, detail="Refresh token expired")
        
    # Valid -> Perform Rotation
    # Delete old token
    await refresh_tokens_collection.delete_one({"_id": db_token["_id"]})
    
    user_id_str = db_token["user_id"]
    
    # Issue new tokens
    new_access_token = create_access_token(subject=user_id_str)
    new_raw_refresh = secrets.token_urlsafe(64)
    new_hashed_refresh = hash_token(new_raw_refresh)
    new_expiry = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    await refresh_tokens_collection.insert_one({
        "user_id": user_id_str,
        "token_hash": new_hashed_refresh,
        "expiry": new_expiry,
        "created_at": datetime.utcnow()
    })
    
    response.set_cookie(
        key="refresh_token",
        value=new_raw_refresh,
        httponly=True,
        secure=False, 
        samesite="lax",
        expires=int(new_expiry.timestamp())
    )
    
    return {"access_token": new_access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout(request: Request, response: Response):
    token = request.cookies.get("refresh_token")
    if token:
        hashed_refresh = hash_token(token)
        await refresh_tokens_collection.delete_one({"token_hash": hashed_refresh})
        
    response.delete_cookie("refresh_token")
    return {"success": True, "message": "Successfully logged out"}
