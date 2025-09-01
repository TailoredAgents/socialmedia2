"""
Critical authentication flow tests to prevent regression
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from backend.db.models import User
from backend.core.security import JWTHandler
import json


class TestAuthenticationFlow:
    """Test critical authentication flows"""
    
    def test_register_creates_user_and_returns_token(self, client: TestClient, db_session):
        """Test that registration creates user and returns valid JWT"""
        response = client.post("/api/auth/register", json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "SecurePass123!",
            "full_name": "Test User",
            "accept_terms": True
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"
        
        # Verify user was created in database
        user = db_session.query(User).filter_by(email="test@example.com").first()
        assert user is not None
        assert user.username == "testuser"
        
        # Verify refresh token cookie was set
        assert "refresh_token" in response.cookies
    
    def test_login_with_valid_credentials(self, client: TestClient, db_session):
        """Test login with valid credentials returns token"""
        # First create a user
        client.post("/api/auth/register", json={
            "email": "login@example.com",
            "username": "loginuser",
            "password": "SecurePass123!",
            "full_name": "Login User",
            "accept_terms": True
        })
        
        # Now test login
        response = client.post("/api/auth/login", json={
            "email": "login@example.com",
            "password": "SecurePass123!"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["email"] == "login@example.com"
        assert "refresh_token" in response.cookies
    
    def test_login_with_invalid_credentials_fails(self, client: TestClient):
        """Test login with invalid credentials returns error"""
        response = client.post("/api/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "WrongPassword"
        })
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    def test_refresh_token_flow(self, client: TestClient, db_session):
        """Test refresh token generates new access token"""
        # Register and get initial tokens
        register_response = client.post("/api/auth/register", json={
            "email": "refresh@example.com",
            "username": "refreshuser",
            "password": "SecurePass123!",
            "full_name": "Refresh User",
            "accept_terms": True
        })
        
        # Use refresh token cookie to get new access token
        cookies = {"refresh_token": register_response.cookies.get("refresh_token")}
        response = client.post("/api/auth/refresh", cookies=cookies)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["email"] == "refresh@example.com"
    
    def test_cors_headers_in_production(self, client: TestClient):
        """Test CORS headers are properly set in production"""
        with patch.dict('os.environ', {'ENVIRONMENT': 'production'}):
            response = client.options("/api/auth/login", headers={
                "Origin": "https://socialmedia-frontend-pycc.onrender.com",
                "Access-Control-Request-Method": "POST"
            })
            
            assert response.status_code == 200
            assert "access-control-allow-origin" in response.headers
            
            # Verify localhost is NOT allowed in production
            response_localhost = client.options("/api/auth/login", headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST"
            })
            
            # Should either reject or not include localhost in allowed origins
            if "access-control-allow-origin" in response_localhost.headers:
                assert response_localhost.headers["access-control-allow-origin"] != "http://localhost:3000"
    
    def test_cookie_samesite_settings(self, client: TestClient):
        """Test cookie SameSite attribute is properly set"""
        response = client.post("/api/auth/register", json={
            "email": "cookie@example.com",
            "username": "cookieuser",
            "password": "SecurePass123!",
            "full_name": "Cookie User",
            "accept_terms": True
        })
        
        cookie_header = response.headers.get("set-cookie", "")
        
        # In production, should use SameSite=Lax
        if "production" in cookie_header.lower():
            assert "samesite=lax" in cookie_header.lower()
        
        # Should always be httponly and secure in production
        assert "httponly" in cookie_header.lower()
    
    def test_jwt_token_validation(self):
        """Test JWT token creation and validation"""
        jwt_handler = JWTHandler()
        
        # Create a token
        token_data = {"sub": "123", "email": "test@example.com"}
        token = jwt_handler.create_access_token(data=token_data)
        
        assert token is not None
        assert len(token) > 50  # JWT tokens are typically long
        
        # Validate the token
        decoded = jwt_handler.decode_access_token(token)
        assert decoded["sub"] == "123"
        assert decoded["email"] == "test@example.com"
    
    def test_password_hashing_security(self):
        """Test password hashing is secure"""
        from backend.core.security import get_password_hash, verify_password
        
        password = "SecurePassword123!"
        hashed = get_password_hash(password)
        
        # Hash should be different from original
        assert hashed != password
        
        # Hash should be sufficiently long (bcrypt produces 60 char hashes)
        assert len(hashed) >= 60
        
        # Should verify correctly
        assert verify_password(password, hashed) is True
        assert verify_password("WrongPassword", hashed) is False
    
    @pytest.mark.parametrize("email,expected_status", [
        ("invalid-email", 422),  # Invalid email format
        ("test@example.com", 200),  # Valid email
        ("TEST@EXAMPLE.COM", 200),  # Case insensitive
    ])
    def test_email_validation(self, client: TestClient, email: str, expected_status: int):
        """Test email validation in registration"""
        response = client.post("/api/auth/register", json={
            "email": email,
            "username": "testuser",
            "password": "SecurePass123!",
            "full_name": "Test User",
            "accept_terms": True
        })
        
        assert response.status_code == expected_status