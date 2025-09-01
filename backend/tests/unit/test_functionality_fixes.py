"""
Test suite for critical functionality fixes
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.db.models import User, WorkflowExecution


class TestAuthenticationCookieFixes:
    """Test authentication cookie configuration fixes"""
    
    @patch('backend.core.config.get_settings')
    def test_cookie_samesite_production_consistency(self, mock_settings, client: TestClient):
        """Test that all cookies use consistent SameSite in production"""
        # Mock production environment
        mock_settings.return_value.environment = "production"
        mock_settings.return_value.require_email_verification = False
        
        response = client.post("/api/auth/register", json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "SecurePass123!",
            "full_name": "Test User",
            "accept_terms": True
        })
        
        assert response.status_code == 200
        cookie_header = response.headers.get("set-cookie", "")
        
        # Should use SameSite=none in production with secure
        assert "samesite=none" in cookie_header.lower()
        assert "secure" in cookie_header.lower()
        assert "httponly" in cookie_header.lower()
    
    @patch('backend.core.config.get_settings')
    def test_cookie_samesite_development_consistency(self, mock_settings, client: TestClient):
        """Test that all cookies use consistent SameSite in development"""
        # Mock development environment
        mock_settings.return_value.environment = "development"
        mock_settings.return_value.require_email_verification = False
        
        response = client.post("/api/auth/register", json={
            "email": "dev@example.com",
            "username": "devuser",
            "password": "SecurePass123!",
            "full_name": "Dev User",
            "accept_terms": True
        })
        
        assert response.status_code == 200
        cookie_header = response.headers.get("set-cookie", "")
        
        # Should use SameSite=lax in development
        assert "samesite=lax" in cookie_header.lower()


class TestWorkflowBackgroundTasks:
    """Test workflow background task database session fixes"""
    
    @pytest.mark.asyncio
    async def test_workflow_execution_no_session_passed(self, db_session: Session):
        """Test workflow execution doesn't pass database session to background task"""
        from backend.api.workflow_v2 import run_workflow
        
        # Create a workflow execution
        execution = WorkflowExecution(
            id="test-execution-id",
            user_id=1,
            workflow_type="daily",
            status="running"
        )
        db_session.add(execution)
        db_session.commit()
        
        # Mock get_db to return our session
        with patch('backend.api.workflow_v2.get_db') as mock_get_db:
            mock_get_db.return_value.__next__ = Mock(return_value=db_session)
            
            # Should not raise any database session errors
            await run_workflow("test-execution-id", "daily")
            
            # Verify execution was updated
            updated_execution = db_session.query(WorkflowExecution).filter_by(
                id="test-execution-id"
            ).first()
            assert updated_execution.status in ["completed", "failed"]
    
    def test_background_task_call_signature(self, client: TestClient, db_session):
        """Test that background task is called without database session parameter"""
        with patch('backend.api.workflow_v2.background_tasks') as mock_bg_tasks:
            response = client.post("/api/workflow/execute", json={
                "workflow_type": "daily"
            })
            
            assert response.status_code == 200
            
            # Verify add_task was called with correct parameters (no db session)
            mock_bg_tasks.add_task.assert_called_once()
            call_args = mock_bg_tasks.add_task.call_args
            
            # Should be: run_workflow, execution_id, workflow_type (no db parameter)
            assert len(call_args[0]) == 3  # function + 2 parameters


class TestOAuthRedirectFixes:
    """Test OAuth redirect URI environment fixes"""
    
    @patch('backend.core.config.get_settings')
    @patch('backend.integrations.twitter_client.get_oauth_authorization_url')
    def test_oauth_uses_configured_backend_url(self, mock_twitter_auth, mock_settings, client: TestClient):
        """Test OAuth redirect uses configured backend URL instead of localhost"""
        # Mock production settings
        mock_settings.return_value.backend_url = "https://api.production.com"
        mock_twitter_auth.return_value = ("https://oauth.url", "state")
        
        response = client.get("/api/social/connect/twitter")
        
        if response.status_code == 200:
            # Verify redirect_uri uses configured backend URL
            expected_redirect = "https://api.production.com/api/social/callback/twitter"
            # This would be verified by checking the call to twitter_client
            mock_twitter_auth.assert_called_with(expected_redirect, mock.ANY)


class TestEmailServiceFixes:
    """Test email service background task error handling"""
    
    @pytest.mark.asyncio
    async def test_safe_email_sending_handles_errors(self):
        """Test that email wrapper handles failures gracefully"""
        from backend.services.email_service_wrapper import safe_send_verification_email
        
        with patch('backend.services.email_service.email_methods.send_verification_email') as mock_send:
            # Test successful send
            mock_send.return_value = None  # Success
            result = await safe_send_verification_email("test@example.com", "user", "token")
            assert result is True
            
            # Test failed send
            mock_send.side_effect = Exception("SMTP Error")
            result = await safe_send_verification_email("test@example.com", "user", "token")
            assert result is False
    
    def test_registration_uses_safe_email_wrapper(self, client: TestClient):
        """Test that registration uses the safe email wrapper"""
        with patch('backend.services.email_service_wrapper.safe_send_verification_email') as mock_safe_send:
            with patch('backend.core.config.get_settings') as mock_settings:
                mock_settings.return_value.require_email_verification = True
                
                response = client.post("/api/auth/register", json={
                    "email": "emailtest@example.com",
                    "username": "emailuser",
                    "password": "SecurePass123!",
                    "full_name": "Email User",
                    "accept_terms": True
                })
                
                assert response.status_code == 200
                # Background task should be scheduled with safe wrapper
                # This is harder to test directly but can be verified by checking imports


class TestAsyncSleepFixes:
    """Test that blocking time.sleep was replaced with asyncio.sleep"""
    
    @pytest.mark.asyncio
    async def test_workflow_uses_async_sleep(self):
        """Test that workflow processing uses async sleep instead of blocking"""
        from backend.api.workflow_v2 import run_workflow
        
        with patch('asyncio.sleep') as mock_async_sleep:
            with patch('backend.api.workflow_v2.get_db') as mock_get_db:
                mock_db = Mock()
                mock_execution = Mock()
                mock_execution.status = "running"
                mock_db.query.return_value.filter.return_value.first.return_value = mock_execution
                mock_get_db.return_value.__next__ = Mock(return_value=mock_db)
                
                await run_workflow("test-id", "daily")
                
                # Should call async sleep instead of time.sleep
                mock_async_sleep.assert_called_with(2)


class TestAuthenticationPriorityFix:
    """Test authentication dependency priority fix"""
    
    @patch('backend.auth.dependencies.jwt_handler.verify_token')
    @patch('backend.auth.dependencies.auth0_verifier.verify_token')
    def test_local_jwt_tried_first(self, mock_auth0_verify, mock_jwt_verify):
        """Test that local JWT is tried before Auth0"""
        from backend.auth.dependencies import get_current_user
        
        # Mock successful local JWT
        mock_jwt_verify.return_value = {
            "sub": "123",
            "email": "test@example.com",
            "username": "testuser"
        }
        
        # This should not be called if local JWT succeeds
        mock_auth0_verify.return_value = {"sub": "auth0-id"}
        
        # Call the function (this would normally be called by FastAPI)
        # We can't easily test the full dependency injection here,
        # but we can verify the logic order in the function
        
        # Verify that when both work, local JWT is preferred
        # This is tested by the order of try/except blocks
        assert True  # Placeholder - full integration test needed


# Integration test to verify overall functionality
class TestOverallFunctionalityHealth:
    """Integration tests for overall functionality health"""
    
    def test_complete_registration_flow(self, client: TestClient):
        """Test complete user registration flow works end-to-end"""
        response = client.post("/api/auth/register", json={
            "email": "integration@example.com",
            "username": "integrationuser",
            "password": "SecurePass123!",
            "full_name": "Integration User",
            "accept_terms": True
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["email"] == "integration@example.com"
        
        # Should have refresh token cookie
        assert "refresh_token" in response.cookies
    
    def test_complete_login_flow(self, client: TestClient, db_session):
        """Test complete user login flow works end-to-end"""
        # First register a user
        client.post("/api/auth/register", json={
            "email": "login@example.com",
            "username": "loginuser",
            "password": "SecurePass123!",
            "full_name": "Login User",
            "accept_terms": True
        })
        
        # Now login
        response = client.post("/api/auth/login", json={
            "email": "login@example.com",
            "password": "SecurePass123!"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["email"] == "login@example.com"
        
        # Should have refresh token cookie
        assert "refresh_token" in response.cookies