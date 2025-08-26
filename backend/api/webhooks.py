"""
Production Webhook Endpoints

Handles incoming webhooks from social media platforms:
- Facebook Graph API webhooks
- Instagram Graph API webhooks  
- X/Twitter Account Activity API webhooks

All endpoints include proper security validation and signature verification.
"""

import logging
import os
from typing import Dict, Any
from fastapi import APIRouter, Request, HTTPException, Query, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.db.models import User, SocialPlatformConnection
from backend.services.facebook_webhook_handler import FacebookWebhookHandler, InstagramWebhookHandler
from backend.services.twitter_webhook_handler import TwitterWebhookHandler, TwitterV2WebhookHandler
from backend.services.social_webhook_service import get_webhook_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhooks", tags=["webhooks"])

# Initialize webhook handlers
FACEBOOK_APP_SECRET = os.getenv('FACEBOOK_APP_SECRET')
INSTAGRAM_APP_SECRET = os.getenv('INSTAGRAM_APP_SECRET', FACEBOOK_APP_SECRET)  # Often same as Facebook
TWITTER_CONSUMER_SECRET = os.getenv('TWITTER_CONSUMER_SECRET')

facebook_handler = FacebookWebhookHandler(FACEBOOK_APP_SECRET) if FACEBOOK_APP_SECRET else None
instagram_handler = InstagramWebhookHandler(INSTAGRAM_APP_SECRET) if INSTAGRAM_APP_SECRET else None
twitter_handler = TwitterWebhookHandler(TWITTER_CONSUMER_SECRET) if TWITTER_CONSUMER_SECRET else None
twitter_v2_handler = TwitterV2WebhookHandler(TWITTER_CONSUMER_SECRET) if TWITTER_CONSUMER_SECRET else None

@router.get("/facebook")
async def facebook_webhook_verification(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_challenge: str = Query(..., alias="hub.challenge"),
    hub_verify_token: str = Query(..., alias="hub.verify_token")
):
    """Facebook webhook verification endpoint"""
    
    expected_token = os.getenv('FACEBOOK_WEBHOOK_VERIFY_TOKEN')
    if not expected_token:
        raise HTTPException(status_code=500, detail="Webhook verify token not configured")
    
    if hub_mode == "subscribe" and hub_verify_token == expected_token:
        logger.info("Facebook webhook verified successfully")
        return PlainTextResponse(hub_challenge)
    else:
        logger.warning(f"Facebook webhook verification failed: mode={hub_mode}, token_match={hub_verify_token == expected_token}")
        raise HTTPException(status_code=403, detail="Verification failed")

@router.post("/facebook/{user_id}")
async def facebook_webhook_handler(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Facebook webhook event handler"""
    
    if not facebook_handler:
        raise HTTPException(status_code=500, detail="Facebook webhook handler not configured")
    
    # Get signature from headers
    signature = request.headers.get('X-Hub-Signature-256')
    if not signature:
        raise HTTPException(status_code=400, detail="Missing signature header")
    
    # Read request body
    payload = await request.body()
    
    # Verify user exists and has Facebook connection
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    facebook_connection = db.query(SocialPlatformConnection).filter(
        SocialPlatformConnection.user_id == user_id,
        SocialPlatformConnection.platform == "facebook",
        SocialPlatformConnection.is_active == True
    ).first()
    
    if not facebook_connection:
        logger.warning(f"Facebook webhook received for user {user_id} without active connection")
        raise HTTPException(status_code=404, detail="No active Facebook connection")
    
    # Set webhook service for the handler
    facebook_handler.webhook_service = get_webhook_service()
    
    # Process webhook
    try:
        result = await facebook_handler.process_webhook(payload, signature, user_id)
        logger.info(f"Processed Facebook webhook for user {user_id}: {result['processed_events']} events")
        return result
    except Exception as e:
        logger.error(f"Error processing Facebook webhook: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

@router.get("/instagram")
async def instagram_webhook_verification(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_challenge: str = Query(..., alias="hub.challenge"),
    hub_verify_token: str = Query(..., alias="hub.verify_token")
):
    """Instagram webhook verification endpoint"""
    
    expected_token = os.getenv('INSTAGRAM_WEBHOOK_VERIFY_TOKEN', os.getenv('FACEBOOK_WEBHOOK_VERIFY_TOKEN'))
    if not expected_token:
        raise HTTPException(status_code=500, detail="Webhook verify token not configured")
    
    if hub_mode == "subscribe" and hub_verify_token == expected_token:
        logger.info("Instagram webhook verified successfully")
        return PlainTextResponse(hub_challenge)
    else:
        logger.warning(f"Instagram webhook verification failed")
        raise HTTPException(status_code=403, detail="Verification failed")

@router.post("/instagram/{user_id}")
async def instagram_webhook_handler(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Instagram webhook event handler"""
    
    if not instagram_handler:
        raise HTTPException(status_code=500, detail="Instagram webhook handler not configured")
    
    signature = request.headers.get('X-Hub-Signature-256')
    if not signature:
        raise HTTPException(status_code=400, detail="Missing signature header")
    
    payload = await request.body()
    
    # Verify user and Instagram connection
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    instagram_connection = db.query(SocialPlatformConnection).filter(
        SocialPlatformConnection.user_id == user_id,
        SocialPlatformConnection.platform == "instagram",
        SocialPlatformConnection.is_active == True
    ).first()
    
    if not instagram_connection:
        raise HTTPException(status_code=404, detail="No active Instagram connection")
    
    # Set webhook service for the handler
    instagram_handler.webhook_service = get_webhook_service()
    
    try:
        result = await instagram_handler.process_webhook(payload, signature, user_id)
        logger.info(f"Processed Instagram webhook for user {user_id}: {result['processed_events']} events")
        return result
    except Exception as e:
        logger.error(f"Error processing Instagram webhook: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

@router.get("/twitter/crc")
async def twitter_webhook_crc(
    crc_token: str = Query(...),
    user_id: int = Query(...)
):
    """Twitter webhook CRC (Challenge Response Check) endpoint"""
    
    if not twitter_handler:
        raise HTTPException(status_code=500, detail="Twitter webhook handler not configured")
    
    try:
        response_token = twitter_handler.create_crc_response(crc_token)
        logger.info(f"Twitter CRC check successful for user {user_id}")
        return {"response_token": f"sha256={response_token}"}
    except Exception as e:
        logger.error(f"Twitter CRC check failed: {e}")
        raise HTTPException(status_code=500, detail="CRC check failed")

@router.post("/twitter/{user_id}")
async def twitter_webhook_handler(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Twitter Account Activity API webhook handler"""
    
    if not twitter_handler:
        raise HTTPException(status_code=500, detail="Twitter webhook handler not configured")
    
    signature = request.headers.get('X-Twitter-Webhooks-Signature')
    if not signature:
        raise HTTPException(status_code=400, detail="Missing signature header")
    
    payload = await request.body()
    
    # Verify user and Twitter connection
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    twitter_connection = db.query(SocialPlatformConnection).filter(
        SocialPlatformConnection.user_id == user_id,
        SocialPlatformConnection.platform == "twitter",
        SocialPlatformConnection.is_active == True
    ).first()
    
    if not twitter_connection:
        raise HTTPException(status_code=404, detail="No active Twitter connection")
    
    # Set webhook service for the handler
    twitter_handler.webhook_service = get_webhook_service()
    
    try:
        result = await twitter_handler.process_webhook(payload, signature, user_id)
        logger.info(f"Processed Twitter webhook for user {user_id}: {result['processed_events']} events")
        return result
    except Exception as e:
        logger.error(f"Error processing Twitter webhook: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

@router.post("/twitter/v2/{user_id}")
async def twitter_v2_webhook_handler(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Twitter API v2 webhook handler"""
    
    if not twitter_v2_handler:
        raise HTTPException(status_code=500, detail="Twitter v2 webhook handler not configured")
    
    signature = request.headers.get('X-Twitter-Webhooks-Signature')
    if not signature:
        raise HTTPException(status_code=400, detail="Missing signature header")
    
    payload = await request.body()
    
    # Verify user and Twitter connection
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    twitter_connection = db.query(SocialPlatformConnection).filter(
        SocialPlatformConnection.user_id == user_id,
        SocialPlatformConnection.platform == "twitter",
        SocialPlatformConnection.is_active == True
    ).first()
    
    if not twitter_connection:
        raise HTTPException(status_code=404, detail="No active Twitter connection")
    
    # Set webhook service for the handler
    twitter_v2_handler.webhook_service = get_webhook_service()
    
    try:
        result = await twitter_v2_handler.process_webhook(payload, signature, user_id)
        logger.info(f"Processed Twitter v2 webhook for user {user_id}: {result['processed_events']} events")
        return result
    except Exception as e:
        logger.error(f"Error processing Twitter v2 webhook: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

@router.get("/status")
async def webhook_status():
    """Get webhook configuration status"""
    
    return {
        "facebook": {
            "configured": facebook_handler is not None,
            "app_secret_set": bool(FACEBOOK_APP_SECRET),
            "verify_token_set": bool(os.getenv('FACEBOOK_WEBHOOK_VERIFY_TOKEN'))
        },
        "instagram": {
            "configured": instagram_handler is not None,
            "app_secret_set": bool(INSTAGRAM_APP_SECRET),
            "verify_token_set": bool(os.getenv('INSTAGRAM_WEBHOOK_VERIFY_TOKEN', os.getenv('FACEBOOK_WEBHOOK_VERIFY_TOKEN')))
        },
        "twitter": {
            "configured": twitter_handler is not None,
            "consumer_secret_set": bool(TWITTER_CONSUMER_SECRET),
            "v2_handler": twitter_v2_handler is not None
        },
        "endpoints": {
            "facebook_verify": "/webhooks/facebook",
            "facebook_handler": "/webhooks/facebook/{user_id}",
            "instagram_verify": "/webhooks/instagram", 
            "instagram_handler": "/webhooks/instagram/{user_id}",
            "twitter_crc": "/webhooks/twitter/crc",
            "twitter_handler": "/webhooks/twitter/{user_id}",
            "twitter_v2_handler": "/webhooks/twitter/v2/{user_id}"
        }
    }