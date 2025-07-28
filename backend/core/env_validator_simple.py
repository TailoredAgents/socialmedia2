"""
Simple Environment Variable Validator
"""
import os
import logging

logger = logging.getLogger(__name__)

def validate_environment():
    """Simple environment validation"""
    required_vars = ["SECRET_KEY"]
    missing = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    return {
        "validation_passed": len(missing) == 0,
        "errors": ["Missing required variable: " + var for var in missing],
        "warnings": [],
        "configuration_completeness": 100 if len(missing) == 0 else 0
    }

def validate_on_startup():
    """Validate environment on startup"""
    result = validate_environment()
    
    if not result["validation_passed"]:
        logger.error("Environment validation failed!")
        for error in result["errors"]:
            logger.error("  - " + error)
        
        # Only warn, don't fail startup for now
        logger.warning("Continuing with missing environment variables")
    else:
        logger.info("Environment validation passed")