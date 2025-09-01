"""
Email service wrapper with error handling for background tasks
"""
import logging
from typing import Optional
from backend.services.email_service import email_methods

logger = logging.getLogger(__name__)


async def safe_send_verification_email(to_email: str, username: str, token: str) -> bool:
    """
    Send verification email with error handling and logging
    Returns True if successful, False if failed
    """
    try:
        await email_methods.send_verification_email(to_email, username, token)
        logger.info(f"Verification email sent successfully to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send verification email to {to_email}: {e}")
        # TODO: Could add user notification about email service issues
        return False


async def safe_send_password_reset_email(to_email: str, username: str, token: str) -> bool:
    """
    Send password reset email with error handling and logging
    Returns True if successful, False if failed
    """
    try:
        await email_methods.send_password_reset_email(to_email, username, token)
        logger.info(f"Password reset email sent successfully to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send password reset email to {to_email}: {e}")
        # TODO: Could add user notification about email service issues
        return False


async def safe_send_welcome_email(to_email: str, username: str) -> bool:
    """
    Send welcome email with error handling and logging
    Returns True if successful, False if failed
    """
    try:
        if hasattr(email_methods, 'send_welcome_email'):
            await email_methods.send_welcome_email(to_email, username)
        logger.info(f"Welcome email sent successfully to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send welcome email to {to_email}: {e}")
        return False