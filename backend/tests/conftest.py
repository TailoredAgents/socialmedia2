"""
Test configuration and fixtures for the AI Social Media Content Agent backend
"""
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import tempfile
import os

from backend.main import app
from backend.db.database import get_db, Base
from backend.db.models import User, ContentItem, Goal, MemoryContent
from backend.auth.dependencies import get_current_active_user

# Test database URL - using SQLite for fast testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def db_session():
    """Create a test database session"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Clean up
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    """Create a test client with database dependency override"""
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        is_active=True,
        tier="pro"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def authenticated_client(client, test_user, db_session):
    """Create an authenticated test client"""
    
    def override_get_current_user():
        return test_user
    
    app.dependency_overrides[get_current_active_user] = override_get_current_user
    
    yield client
    
    app.dependency_overrides.clear()

@pytest.fixture
def test_content_item(db_session, test_user):
    """Create a test content item"""
    content = ContentItem(
        user_id=test_user.id,
        content="Test content for social media",
        platform="twitter",
        content_type="post",
        status="published",
        engagement_rate=5.2,
        performance_tier="medium"
    )
    db_session.add(content)
    db_session.commit()
    db_session.refresh(content)
    return content

@pytest.fixture
def test_goal(db_session, test_user):
    """Create a test goal"""
    goal = Goal(
        id="test-goal-123",
        user_id=test_user.id,
        title="Increase Twitter Followers",
        description="Grow Twitter following by 1000 followers",
        goal_type="follower_growth",
        target_value=1000.0,
        current_value=250.0,
        target_date=datetime.utcnow() + timedelta(days=30),
        platform="twitter"
    )
    db_session.add(goal)
    db_session.commit()
    db_session.refresh(goal)
    return goal

@pytest.fixture
def test_memory_content(db_session, test_user):
    """Create test memory content"""
    memory = MemoryContent(
        id="test-memory-123",
        user_id=test_user.id,
        content="Test memory content about social media trends",
        content_type="research",
        platform="twitter",
        relevance_score=0.85,
        engagement_score=7.5,
        performance_tier="high"
    )
    db_session.add(memory)
    db_session.commit()
    db_session.refresh(memory)
    return memory

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    return {
        "choices": [{
            "message": {
                "content": "Generated social media content about trending topics"
            }
        }],
        "usage": {
            "total_tokens": 50
        }
    }

@pytest.fixture
def mock_faiss_embeddings():
    """Mock FAISS embeddings for testing"""
    import numpy as np
    return np.random.rand(1536).astype('float32')  # OpenAI embedding dimension

# Test data fixtures
@pytest.fixture
def sample_content_data():
    return {
        "content": "This is a test social media post about AI and technology trends",
        "platform": "twitter",
        "content_type": "post",
        "scheduled_for": None,
        "hashtags": ["#AI", "#Technology", "#Trends"]
    }

@pytest.fixture
def sample_goal_data():
    return {
        "title": "Increase LinkedIn Engagement",
        "description": "Boost LinkedIn post engagement by 50%",
        "goal_type": "engagement_rate",
        "target_value": 50.0,
        "target_date": "2025-08-24",
        "platform": "linkedin"
    }

@pytest.fixture
def sample_memory_data():
    return {
        "content": "Research insights about social media algorithm changes",
        "content_type": "research",
        "source": "industry_report",
        "platform": "web",
        "tags": ["algorithms", "social_media", "research"],
        "metadata": {"source_url": "https://example.com/report"}
    }

# Helper functions
def create_auth_headers(token: str = "test-token"):
    """Create authentication headers for testing"""
    return {"Authorization": f"Bearer {token}"}

def assert_response_structure(response_data: dict, expected_keys: list):
    """Assert that response contains expected keys"""
    for key in expected_keys:
        assert key in response_data, f"Expected key '{key}' not found in response"

# Mock external services
@pytest.fixture(autouse=True)
def mock_external_services(monkeypatch):
    """Mock external services for testing"""
    
    # Mock OpenAI API
    def mock_openai_create(*args, **kwargs):
        return type('Response', (), {
            'choices': [type('Choice', (), {
                'message': type('Message', (), {
                    'content': 'Mock AI generated content'
                })()
            })()],
            'usage': type('Usage', (), {'total_tokens': 50})()
        })()
    
    # Mock FAISS operations
    def mock_faiss_add(*args, **kwargs):
        return 1
    
    def mock_faiss_search(*args, **kwargs):
        return ([0.95], [0])
    
    # Apply mocks
    monkeypatch.setattr("openai.ChatCompletion.create", mock_openai_create)
    
    yield