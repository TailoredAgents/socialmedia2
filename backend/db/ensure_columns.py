"""
Ensure critical database columns exist on startup
This bypasses Alembic migration issues in production
"""
import logging
from sqlalchemy import text
from backend.db.database import engine

logger = logging.getLogger(__name__)

def ensure_notifications_table():
    """
    Ensure notifications table exists with all required columns
    """
    try:
        with engine.connect() as conn:
            # Check if notifications table exists
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'notifications'
            """)).fetchall()
            
            if not result:
                logger.info("Creating missing notifications table...")
                
                # Create notifications table
                conn.execute(text("""
                    CREATE TABLE notifications (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        title VARCHAR(255) NOT NULL,
                        message TEXT,
                        notification_type VARCHAR(50) DEFAULT 'info',
                        priority VARCHAR(20) DEFAULT 'medium',
                        goal_id INTEGER,
                        content_id INTEGER, 
                        workflow_id INTEGER,
                        is_read BOOLEAN DEFAULT FALSE,
                        is_dismissed BOOLEAN DEFAULT FALSE,
                        read_at TIMESTAMP,
                        action_url VARCHAR(500),
                        action_label VARCHAR(100),
                        notification_metadata JSON,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP
                    )
                """))
                
                # Create indexes
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_notifications_user_id ON notifications (user_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_notifications_is_read ON notifications (is_read)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_notifications_created_at ON notifications (created_at)"))
                
                conn.commit()
                logger.info("✅ Successfully created notifications table")
            else:
                logger.info("✅ Notifications table already exists")
                
    except Exception as e:
        logger.error(f"❌ Error ensuring notifications table: {e}")
        pass

def ensure_user_columns():
    """
    Ensure all required columns exist in the users table.
    Based on migration 016_convert_to_open_saas_auth.py
    This is a safety net for production where migrations might not run properly.
    """
    required_columns = [
        # Core auth columns
        ('is_superuser', 'BOOLEAN DEFAULT FALSE'),
        ('is_verified', 'BOOLEAN DEFAULT FALSE'), 
        ('is_active', 'BOOLEAN DEFAULT TRUE'),
        ('auth_provider', 'VARCHAR(50) DEFAULT \'local\''),
        
        # Email verification columns (CRITICAL - missing these causes 500 errors)
        ('email_verified', 'BOOLEAN DEFAULT FALSE'),
        ('email_verification_token', 'VARCHAR(255)'),
        ('email_verification_sent_at', 'TIMESTAMP'),
        
        # Password reset columns
        ('password_reset_token', 'VARCHAR(255)'),
        ('password_reset_sent_at', 'TIMESTAMP'),
        
        # Two-factor authentication columns
        ('two_factor_enabled', 'BOOLEAN DEFAULT FALSE'),
        ('two_factor_secret', 'VARCHAR(255)'),
        ('two_factor_backup_codes', 'JSON'),
        
        # Multi-tenancy columns (CRITICAL - missing causes registration failures)
        ('default_organization_id', 'VARCHAR(255)'),
        
        # Subscription columns
        ('tier', 'VARCHAR(50) DEFAULT \'free\''),
        ('subscription_status', 'VARCHAR(50) DEFAULT \'free\''),
        ('subscription_end_date', 'TIMESTAMP'),
        ('stripe_customer_id', 'VARCHAR(255)'),
        ('stripe_subscription_id', 'VARCHAR(255)'),
        
        # Timestamps (commonly missing)
        ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
        ('updated_at', 'TIMESTAMP'),
    ]
    
    try:
        with engine.connect() as conn:
            logger.info("Checking for missing columns in users table...")
            
            # Get all existing columns
            existing_columns = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users'
            """)).fetchall()
            
            existing_column_names = {row[0] for row in existing_columns}
            logger.info(f"Found {len(existing_column_names)} existing columns in users table")
            
            columns_added = 0
            for column_name, column_type in required_columns:
                if column_name not in existing_column_names:
                    logger.info(f"Adding missing {column_name} column to users table")
                    
                    try:
                        conn.execute(text(f"""
                            ALTER TABLE users 
                            ADD COLUMN {column_name} {column_type}
                        """))
                        conn.commit()
                        columns_added += 1
                        logger.info(f"✅ Successfully added {column_name} column")
                    except Exception as col_error:
                        logger.error(f"❌ Failed to add {column_name} column: {col_error}")
                        conn.rollback()
            
            if columns_added > 0:
                logger.info(f"✅ Added {columns_added} missing columns to users table")
            else:
                logger.info("✅ All required columns already exist in users table")
                
            # Create indexes for new columns if they don't exist
            indexes_to_create = [
                ('ix_users_email_verification_token', 'email_verification_token'),
                ('ix_users_password_reset_token', 'password_reset_token'), 
                ('ix_users_stripe_customer_id', 'stripe_customer_id'),
            ]
            
            for index_name, column_name in indexes_to_create:
                try:
                    conn.execute(text(f"""
                        CREATE INDEX IF NOT EXISTS {index_name} ON users ({column_name})
                    """))
                    conn.commit()
                except Exception as idx_error:
                    logger.warning(f"Could not create index {index_name}: {idx_error}")
                    conn.rollback()
            
            logger.info("✅ Database column and index check complete")
            
    except Exception as e:
        logger.error(f"❌ Error ensuring database columns: {e}")
        # Don't crash the app, just log the error
        pass