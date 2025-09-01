#!/usr/bin/env python3
"""
Production Security Validation Script
Validates all critical security configurations before deployment
"""
import os
import sys
import logging
from typing import List, Dict, Any
from pathlib import Path
import secrets
import hashlib

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.core.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductionSecurityValidator:
    """Validates production security configuration"""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.checks_passed: List[str] = []
    
    def validate_environment_variables(self) -> bool:
        """Validate all critical environment variables"""
        logger.info("🔍 Validating environment variables...")
        
        required_vars = {
            "SECRET_KEY": {"min_length": 32, "description": "JWT signing key"},
            "ENCRYPTION_KEY": {"min_length": 32, "description": "Data encryption key"},
            "DATABASE_URL": {"must_contain": "postgresql://", "description": "Database connection"},
            "REDIS_URL": {"must_contain": "redis://", "description": "Redis connection"},
            "OPENAI_API_KEY": {"must_start": "sk-", "description": "OpenAI API key"},
        }
        
        for var_name, requirements in required_vars.items():
            value = os.getenv(var_name, "")
            
            if not value:
                self.errors.append(f"❌ {var_name} is not set - {requirements['description']}")
                continue
            
            # Check minimum length
            if "min_length" in requirements and len(value) < requirements["min_length"]:
                self.errors.append(f"❌ {var_name} must be at least {requirements['min_length']} characters")
                continue
            
            # Check must contain
            if "must_contain" in requirements and requirements["must_contain"] not in value:
                self.errors.append(f"❌ {var_name} must contain '{requirements['must_contain']}'")
                continue
            
            # Check must start with
            if "must_start" in requirements and not value.startswith(requirements["must_start"]):
                self.errors.append(f"❌ {var_name} must start with '{requirements['must_start']}'")
                continue
            
            self.checks_passed.append(f"✅ {var_name} is properly configured")
        
        return len([e for e in self.errors if var_name in e]) == 0
    
    def validate_secret_quality(self) -> bool:
        """Validate quality of secrets"""
        logger.info("🔍 Validating secret quality...")
        
        secret_key = os.getenv("SECRET_KEY", "")
        encryption_key = os.getenv("ENCRYPTION_KEY", "")
        
        # Check for default/weak values
        weak_patterns = [
            "your-secret-key",
            "change-this",
            "password",
            "secret",
            "default",
            "123456",
            "admin"
        ]
        
        for key_name, key_value in [("SECRET_KEY", secret_key), ("ENCRYPTION_KEY", encryption_key)]:
            if not key_value:
                continue
                
            # Check for weak patterns
            if any(pattern in key_value.lower() for pattern in weak_patterns):
                self.errors.append(f"❌ {key_name} contains weak/default patterns")
                continue
            
            # Check entropy (simplified)
            unique_chars = len(set(key_value))
            if unique_chars < 16:
                self.warnings.append(f"⚠️ {key_name} has low entropy ({unique_chars} unique characters)")
            else:
                self.checks_passed.append(f"✅ {key_name} has good entropy")
        
        return len([e for e in self.errors if "SECRET_KEY" in e or "ENCRYPTION_KEY" in e]) == 0
    
    def validate_database_security(self) -> bool:
        """Validate database connection security"""
        logger.info("🔍 Validating database security...")
        
        db_url = os.getenv("DATABASE_URL", "")
        
        if not db_url:
            self.errors.append("❌ DATABASE_URL is not set")
            return False
        
        # Check for SSL mode
        if "sslmode=require" not in db_url and "sslmode=prefer" not in db_url:
            self.warnings.append("⚠️ Database connection should use SSL (add ?sslmode=require)")
        else:
            self.checks_passed.append("✅ Database SSL is configured")
        
        # Check for hardcoded credentials (basic check)
        if "socialmedia:BbsIYQ" in db_url:
            self.errors.append("❌ Database URL contains exposed/hardcoded credentials")
            return False
        
        self.checks_passed.append("✅ Database URL appears secure")
        return True
    
    def validate_cors_configuration(self) -> bool:
        """Validate CORS configuration for production"""
        logger.info("🔍 Validating CORS configuration...")
        
        allowed_origins = os.getenv("ALLOWED_ORIGINS", os.getenv("CORS_ORIGINS", ""))
        
        if not allowed_origins:
            self.warnings.append("⚠️ No CORS origins configured - will use hardcoded defaults")
        else:
            origins = [origin.strip() for origin in allowed_origins.split(",")]
            
            # Check for localhost in production
            if any("localhost" in origin for origin in origins):
                self.errors.append("❌ CORS includes localhost in production - security risk")
                return False
            
            # Check all origins use HTTPS
            for origin in origins:
                if origin.startswith("http://") and not origin.startswith("http://localhost"):
                    self.errors.append(f"❌ CORS origin uses HTTP instead of HTTPS: {origin}")
                    return False
            
            self.checks_passed.append("✅ CORS origins are secure")
        
        return True
    
    def validate_application_config(self) -> bool:
        """Validate application configuration"""
        logger.info("🔍 Validating application configuration...")
        
        try:
            settings = get_settings()
            
            # Environment detection
            if settings.environment != "production":
                self.warnings.append(f"⚠️ Environment detected as '{settings.environment}', expected 'production'")
            else:
                self.checks_passed.append("✅ Environment correctly detected as production")
            
            # Debug mode
            if settings.debug:
                self.errors.append("❌ Debug mode is enabled in production")
                return False
            else:
                self.checks_passed.append("✅ Debug mode is disabled")
            
            return True
            
        except Exception as e:
            self.errors.append(f"❌ Failed to load application settings: {e}")
            return False
    
    def generate_secure_secrets(self) -> Dict[str, str]:
        """Generate secure secrets for missing configuration"""
        logger.info("🔧 Generating secure secrets...")
        
        return {
            "SECRET_KEY": secrets.token_urlsafe(64),
            "ENCRYPTION_KEY": secrets.token_urlsafe(32),
            "JWT_SECRET": secrets.token_urlsafe(64)
        }
    
    def run_all_validations(self) -> bool:
        """Run all security validations"""
        logger.info("🚀 Starting production security validation...")
        
        validations = [
            self.validate_environment_variables,
            self.validate_secret_quality,
            self.validate_database_security,
            self.validate_cors_configuration,
            self.validate_application_config
        ]
        
        all_passed = True
        for validation in validations:
            try:
                if not validation():
                    all_passed = False
            except Exception as e:
                self.errors.append(f"❌ Validation failed: {e}")
                all_passed = False
        
        return all_passed
    
    def print_report(self):
        """Print validation report"""
        logger.info("📋 PRODUCTION SECURITY VALIDATION REPORT")
        logger.info("=" * 60)
        
        if self.checks_passed:
            logger.info("✅ PASSED CHECKS:")
            for check in self.checks_passed:
                logger.info(f"  {check}")
            logger.info("")
        
        if self.warnings:
            logger.warning("⚠️ WARNINGS:")
            for warning in self.warnings:
                logger.warning(f"  {warning}")
            logger.info("")
        
        if self.errors:
            logger.error("❌ CRITICAL ERRORS:")
            for error in self.errors:
                logger.error(f"  {error}")
            logger.info("")
            
            logger.error("🚫 PRODUCTION DEPLOYMENT BLOCKED")
            logger.error("Fix all critical errors before deploying to production")
            return False
        else:
            logger.info("🎉 ALL SECURITY CHECKS PASSED")
            logger.info("✅ Application is ready for production deployment")
            return True


def main():
    """Main validation function"""
    validator = ProductionSecurityValidator()
    
    # Run validations
    success = validator.run_all_validations()
    
    # Print report
    validation_passed = validator.print_report()
    
    # Generate secrets if needed
    if not success and any("is not set" in error for error in validator.errors):
        logger.info("🔧 Generating secure secrets for missing configuration:")
        secrets_dict = validator.generate_secure_secrets()
        
        logger.info("\n" + "="*60)
        logger.info("GENERATED SECURE SECRETS (save these securely):")
        logger.info("="*60)
        
        for key, value in secrets_dict.items():
            logger.info(f"export {key}='{value}'")
    
    # Exit with appropriate code
    sys.exit(0 if validation_passed else 1)


if __name__ == "__main__":
    main()