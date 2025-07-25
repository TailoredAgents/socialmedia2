"""
API validation utilities and common validators
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, validator
from datetime import datetime, date
from fastapi import HTTPException, status

class ValidationError(Exception):
    """Custom validation error"""
    pass

class APIResponse(BaseModel):
    """Standard API response format"""
    status: str = "success"
    message: Optional[str] = None
    data: Optional[Any] = None
    errors: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class PaginationParams(BaseModel):
    """Standard pagination parameters"""
    page: int = 1
    limit: int = 50
    offset: Optional[int] = None
    
    @validator('page')
    def page_must_be_positive(cls, v):
        if v < 1:
            raise ValueError('Page must be positive')
        return v
    
    @validator('limit')
    def limit_must_be_reasonable(cls, v):
        if v < 1 or v > 100:
            raise ValueError('Limit must be between 1 and 100')
        return v
    
    def get_offset(self) -> int:
        """Calculate offset from page and limit"""
        if self.offset is not None:
            return self.offset
        return (self.page - 1) * self.limit

class DateRangeParams(BaseModel):
    """Standard date range parameters"""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    days: Optional[int] = None
    
    @validator('end_date')
    def end_date_after_start(cls, v, values):
        if v and values.get('start_date') and v < values['start_date']:
            raise ValueError('End date must be after start date')
        return v
    
    @validator('days')
    def days_must_be_positive(cls, v):
        if v is not None and v < 1:
            raise ValueError('Days must be positive')
        return v

def validate_platform(platform: str) -> str:
    """Validate social media platform"""
    valid_platforms = ['twitter', 'linkedin', 'instagram', 'facebook', 'tiktok', 'youtube']
    if platform.lower() not in valid_platforms:
        raise ValidationError(f"Invalid platform. Must be one of: {', '.join(valid_platforms)}")
    return platform.lower()

def validate_content_type(content_type: str) -> str:
    """Validate content type"""
    valid_types = ['text', 'image', 'video', 'carousel', 'story', 'reel']
    if content_type.lower() not in valid_types:
        raise ValidationError(f"Invalid content type. Must be one of: {', '.join(valid_types)}")
    return content_type.lower()

def validate_goal_type(goal_type: str) -> str:
    """Validate goal type"""
    valid_types = ['follower_growth', 'engagement_rate', 'reach_increase', 'content_volume', 'custom']
    if goal_type.lower() not in valid_types:
        raise ValidationError(f"Invalid goal type. Must be one of: {', '.join(valid_types)}")
    return goal_type.lower()

def validate_workflow_type(workflow_type: str) -> str:
    """Validate workflow type"""
    valid_types = ['daily', 'optimization', 'manual', 'research', 'content_generation']
    if workflow_type.lower() not in valid_types:
        raise ValidationError(f"Invalid workflow type. Must be one of: {', '.join(valid_types)}")
    return workflow_type.lower()

def sanitize_text(text: str, max_length: int = 10000) -> str:
    """Sanitize text input"""
    if not text:
        return ""
    
    # Remove excessive whitespace
    sanitized = ' '.join(text.split())
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized

def validate_tags(tags: List[str]) -> List[str]:
    """Validate and sanitize tags"""
    if not tags:
        return []
    
    validated_tags = []
    for tag in tags:
        # Remove whitespace and convert to lowercase
        clean_tag = tag.strip().lower()
        
        # Skip empty tags
        if not clean_tag:
            continue
        
        # Validate tag format (alphanumeric and underscores only)
        if not clean_tag.replace('_', '').replace('-', '').isalnum():
            continue
        
        # Limit tag length
        if len(clean_tag) > 50:
            clean_tag = clean_tag[:50]
        
        validated_tags.append(clean_tag)
    
    # Remove duplicates and limit total number
    return list(set(validated_tags))[:20]

def validate_engagement_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate engagement data structure"""
    if not data:
        return {}
    
    # Define expected fields and their types
    expected_fields = {
        'likes': int,
        'comments': int,
        'shares': int,
        'views': int,
        'clicks': int,
        'saves': int,
        'impressions': int,
        'reach': int
    }
    
    validated_data = {}
    for field, field_type in expected_fields.items():
        if field in data:
            try:
                value = field_type(data[field])
                if value >= 0:  # Ensure non-negative
                    validated_data[field] = value
            except (ValueError, TypeError):
                continue  # Skip invalid values
    
    return validated_data

def create_error_response(message: str, errors: List[str] = None) -> Dict[str, Any]:
    """Create standardized error response"""
    return {
        "status": "error",
        "message": message,
        "errors": errors or [],
        "data": None
    }

def create_success_response(data: Any = None, message: str = None, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """Create standardized success response"""
    return {
        "status": "success",
        "message": message,
        "data": data,
        "metadata": metadata
    }

def validate_json_field(data: Any, max_size_kb: int = 100) -> Dict[str, Any]:
    """Validate JSON field size and structure"""
    if not data:
        return {}
    
    if not isinstance(data, dict):
        raise ValidationError("JSON field must be a dictionary")
    
    # Check size
    import json
    json_str = json.dumps(data)
    size_kb = len(json_str.encode('utf-8')) / 1024
    
    if size_kb > max_size_kb:
        raise ValidationError(f"JSON field too large. Maximum size: {max_size_kb}KB")
    
    return data

# Common HTTP exception handlers
def validation_exception_handler(error: ValidationError) -> HTTPException:
    """Convert validation error to HTTP exception"""
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=str(error)
    )

def not_found_exception(resource: str, resource_id: Any = None) -> HTTPException:
    """Create not found exception"""
    message = f"{resource} not found"
    if resource_id:
        message += f" (ID: {resource_id})"
    
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=message
    )

def forbidden_exception(message: str = "Access forbidden") -> HTTPException:
    """Create forbidden exception"""
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=message
    )

def bad_request_exception(message: str) -> HTTPException:
    """Create bad request exception"""
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=message
    )