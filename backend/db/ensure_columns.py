"""
Ensure critical database columns exist on startup
This bypasses Alembic migration issues in production
"""
import logging
from sqlalchemy import text
from backend.db.database import engine

logger = logging.getLogger(__name__)

def ensure_user_columns():
    """
    Ensure all required columns exist in the users table.
    This is a safety net for production where migrations might not run properly.
    """
    try:
        with engine.connect() as conn:
            # Check and add is_superuser column
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='is_superuser'
            """))
            
            if not result.fetchone():
                logger.info("Adding missing is_superuser column to users table")
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN is_superuser BOOLEAN DEFAULT FALSE
                """))
                conn.commit()
                logger.info("Successfully added is_superuser column")
            
            # Check and add is_verified column
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='is_verified'
            """))
            
            if not result.fetchone():
                logger.info("Adding missing is_verified column to users table")
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN is_verified BOOLEAN DEFAULT FALSE
                """))
                conn.commit()
                logger.info("Successfully added is_verified column")
            
            # Check and add email_verified column
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='email_verified'
            """))
            
            if not result.fetchone():
                logger.info("Adding missing email_verified column to users table")
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN email_verified BOOLEAN DEFAULT FALSE
                """))
                conn.commit()
                logger.info("Successfully added email_verified column")
                
            # Check and add tier column
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='tier'
            """))
            
            if not result.fetchone():
                logger.info("Adding missing tier column to users table")
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN tier VARCHAR(50) DEFAULT 'free'
                """))
                conn.commit()
                logger.info("Successfully added tier column")
                
            # Check and add subscription_status column  
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='subscription_status'
            """))
            
            if not result.fetchone():
                logger.info("Adding missing subscription_status column to users table")
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN subscription_status VARCHAR(50) DEFAULT 'free'
                """))
                conn.commit()
                logger.info("Successfully added subscription_status column")
            
            logger.info("Database column check complete")
            
    except Exception as e:
        logger.error(f"Error ensuring database columns: {e}")
        # Don't crash the app, just log the error
        pass