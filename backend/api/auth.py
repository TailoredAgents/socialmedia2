"""
Authentication API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Dict, Any

from backend.db.database import get_db
from backend.db.models import User, UserSetting
from backend.auth.dependencies import get_current_user, get_current_active_user, AuthUser
from backend.auth.jwt_handler import jwt_handler
from backend.auth.auth0 import auth0_user_manager
from backend.auth.config_validator import auth_config_validator

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Pydantic models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str = ""

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    username: str

class UserProfile(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    is_active: bool
    tier: str
    created_at: str

@router.post("/register", response_model=TokenResponse)
async def register_user(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register new user with local authentication"""
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == request.email) | (User.username == request.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    # Create new user
    hashed_password = jwt_handler.hash_password(request.password)
    
    new_user = User(
        email=request.email,
        username=request.username,
        full_name=request.full_name or request.username,
        hashed_password=hashed_password,
        is_active=True,
        tier="base",
        auth_provider="local"
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create default user settings
    user_settings = UserSetting(
        user_id=new_user.id,
        brand_name=request.full_name or request.username,
        brand_voice="professional",
        content_frequency=3,
        preferred_platforms=["twitter", "linkedin"],
        posting_times={"twitter": "09:00", "linkedin": "10:00"},
        creativity_level=0.7,
        enable_images=True,
        enable_repurposing=True
    )
    
    db.add(user_settings)
    db.commit()
    
    # Create access token
    access_token = jwt_handler.create_user_token(
        user_id=str(new_user.id),
        email=new_user.email,
        username=new_user.username
    )
    
    return TokenResponse(
        access_token=access_token,
        user_id=str(new_user.id),
        email=new_user.email,
        username=new_user.username
    )

@router.post("/login", response_model=TokenResponse)
async def login_user(request: LoginRequest, db: Session = Depends(get_db)):
    """Login user with local authentication"""
    
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Verify password for local auth users
    if user.auth_provider == "local" and user.hashed_password:
        if not jwt_handler.verify_password(request.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
    elif user.auth_provider == "local" and not user.hashed_password:
        # User exists but has no password (created via Auth0)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please use Auth0 login for this account"
        )
    
    # Create access token
    access_token = jwt_handler.create_user_token(
        user_id=str(user.id),
        email=user.email,
        username=user.username
    )
    
    return TokenResponse(
        access_token=access_token,
        user_id=str(user.id),
        email=user.email,
        username=user.username
    )

@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user profile"""
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name or "",
        is_active=current_user.is_active,
        tier=current_user.tier,
        created_at=current_user.created_at.isoformat() if current_user.created_at else ""
    )

@router.post("/refresh")
async def refresh_token(current_user: AuthUser = Depends(get_current_user)):
    """Refresh access token"""
    
    # Create new access token
    access_token = jwt_handler.create_user_token(
        user_id=current_user.user_id,
        email=current_user.email,
        username=current_user.username
    )
    
    return TokenResponse(
        access_token=access_token,
        user_id=current_user.user_id,
        email=current_user.email,
        username=current_user.username
    )

@router.post("/logout")
async def logout_user(current_user: AuthUser = Depends(get_current_user)):
    """Logout user (client should remove token)"""
    return {"message": "Successfully logged out"}

@router.get("/auth0/callback")
async def auth0_callback(code: str, db: Session = Depends(get_db)):
    """Handle Auth0 callback (for future implementation)"""
    # This would handle the Auth0 authorization code flow
    # For now, return a placeholder response
    return {"message": "Auth0 callback received", "code": code}

@router.get("/verify")
async def verify_token(current_user: AuthUser = Depends(get_current_user)):
    """Verify if current token is valid"""
    return {
        "valid": True,
        "user_id": current_user.user_id,
        "email": current_user.email,
        "username": current_user.username,
        "auth_method": current_user.auth_method
    }

@router.get("/config")
async def get_auth_config():
    """Get authentication configuration status"""
    return auth_config_validator.get_auth_status()