"""
FastAPI Users configuration with SQLAlchemy
Production-ready authentication without OAuth
"""
import os
from typing import Optional, AsyncGenerator
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, IntegerIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.db.database import Base, get_db
from backend.core.config import settings

# User database model for FastAPI Users
class UserTable(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    tier = Column(String, default="base")
    auth_provider = Column(String, default="local")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Create async engine for FastAPI Users
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
elif DATABASE_URL.startswith("sqlite:///"):
    DATABASE_URL = DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, UserTable)

# User manager configuration
class UserManager(IntegerIDMixin, BaseUserManager[UserTable, int]):
    reset_password_token_secret = settings.SECRET_KEY
    verification_token_secret = settings.SECRET_KEY
    
    async def on_after_register(self, user: UserTable, request: Optional[Request] = None):
        """Called after a user registers"""
        print(f"User {user.id} has registered with email {user.email}")
    
    async def on_after_forgot_password(
        self, user: UserTable, token: str, request: Optional[Request] = None
    ):
        """Called after forgot password request"""
        print(f"User {user.id} has forgot their password. Reset token: {token}")
        # TODO: Send email with reset token
    
    async def on_after_request_verify(
        self, user: UserTable, token: str, request: Optional[Request] = None
    ):
        """Called after verification request"""
        print(f"Verification requested for user {user.id}. Verification token: {token}")
        # TODO: Send verification email
    
    async def on_after_update(
        self, user: UserTable, update_dict: dict, request: Optional[Request] = None
    ):
        """Called after a user updates their profile"""
        print(f"User {user.id} has been updated with {update_dict}")
    
    async def on_after_login(
        self, user: UserTable, request: Optional[Request] = None
    ):
        """Called after successful login"""
        print(f"User {user.id} logged in successfully")

async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

# JWT Strategy
def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.SECRET_KEY,
        lifetime_seconds=3600,  # 1 hour access token
    )

# Authentication backend
bearer_transport = BearerTransport(tokenUrl="/api/auth/jwt/login")

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

# FastAPIUsers instance
fastapi_users = FastAPIUsers[UserTable, int](
    get_user_manager,
    [auth_backend],
)

# Dependency shortcuts
current_active_user = fastapi_users.current_user(active=True)
current_active_verified_user = fastapi_users.current_user(active=True, verified=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)