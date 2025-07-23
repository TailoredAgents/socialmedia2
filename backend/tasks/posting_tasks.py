from backend.tasks.celery_app import celery_app
from backend.agents.tools import twitter_tool
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@celery_app.task
def schedule_post(content, platform, scheduled_time=None):
    """Schedule a post for a specific platform"""
    try:
        if scheduled_time is None:
            scheduled_time = datetime.utcnow() + timedelta(hours=1)
        
        # For now, we'll simulate scheduling
        # In production, you'd integrate with platform APIs or scheduling services
        
        result = {
            'status': 'scheduled',
            'content': content,
            'platform': platform,
            'scheduled_for': scheduled_time.isoformat(),
            'post_id': f"{platform}_{int(datetime.utcnow().timestamp())}"
        }
        
        logger.info(f"Post scheduled for {platform} at {scheduled_time}")
        
        return result
        
    except Exception as exc:
        logger.error(f"Post scheduling failed: {str(exc)}")
        return {
            'status': 'error',
            'message': f'Post scheduling failed: {str(exc)}'
        }

@celery_app.task
def publish_post(content, platform, post_id=None):
    """Publish a post immediately to the specified platform"""
    try:
        if platform.lower() == 'twitter':
            result = twitter_tool.post_tweet(content)
            
            if result['status'] == 'success':
                return {
                    'status': 'published',
                    'platform': platform,
                    'content': content,
                    'platform_post_id': result['tweet_id'],
                    'published_at': datetime.utcnow().isoformat()
                }
            else:
                return {
                    'status': 'failed',
                    'platform': platform,
                    'error': result.get('error', 'Unknown error')
                }
        
        elif platform.lower() == 'linkedin':
            # LinkedIn API integration would go here
            # For now, simulate success
            return {
                'status': 'published',
                'platform': platform,
                'content': content,
                'platform_post_id': f"linkedin_{int(datetime.utcnow().timestamp())}",
                'published_at': datetime.utcnow().isoformat(),
                'note': 'LinkedIn integration not yet implemented'
            }
        
        elif platform.lower() == 'instagram':
            # Instagram API integration would go here
            return {
                'status': 'published',
                'platform': platform,
                'content': content,
                'platform_post_id': f"instagram_{int(datetime.utcnow().timestamp())}",
                'published_at': datetime.utcnow().isoformat(),
                'note': 'Instagram integration not yet implemented'
            }
        
        else:
            return {
                'status': 'error',
                'message': f'Platform {platform} not supported'
            }
            
    except Exception as exc:
        logger.error(f"Post publishing failed: {str(exc)}")
        return {
            'status': 'error',
            'message': f'Post publishing failed: {str(exc)}'
        }

@celery_app.task
def batch_publish_posts(posts):
    """Publish multiple posts across different platforms"""
    try:
        results = []
        
        for post in posts:
            result = publish_post.apply_async(
                args=[post['content'], post['platform']],
                kwargs={'post_id': post.get('id')}
            )
            
            results.append({
                'original_post': post,
                'task_id': result.id,
                'status': 'queued'
            })
        
        return {
            'status': 'success',
            'message': f'Batch publishing initiated for {len(posts)} posts',
            'results': results
        }
        
    except Exception as exc:
        logger.error(f"Batch publishing failed: {str(exc)}")
        return {
            'status': 'error',
            'message': f'Batch publishing failed: {str(exc)}'
        }

@celery_app.task
def validate_post_content(content, platform):
    """Validate post content against platform requirements"""
    try:
        issues = []
        
        # Platform-specific validation
        if platform.lower() == 'twitter':
            if len(content) > 280:
                issues.append(f"Content too long: {len(content)} characters (max: 280)")
        
        elif platform.lower() == 'linkedin':
            if len(content) > 3000:
                issues.append(f"Content too long: {len(content)} characters (max: 3000)")
        
        elif platform.lower() == 'instagram':
            if len(content) > 2200:
                issues.append(f"Content too long: {len(content)} characters (max: 2200)")
        
        # General validation
        if not content.strip():
            issues.append("Content is empty")
        
        # Check for excessive hashtags
        hashtag_count = content.count('#')
        if hashtag_count > 10:
            issues.append(f"Too many hashtags: {hashtag_count} (recommended: 5-10)")
        
        # Check for URLs (basic validation)
        if 'http://' in content or 'https://' in content:
            url_count = content.count('http://') + content.count('https://')
            if url_count > 2:
                issues.append(f"Too many URLs: {url_count} (recommended: 1-2)")
        
        return {
            'status': 'success',
            'valid': len(issues) == 0,
            'issues': issues,
            'content_length': len(content),
            'platform': platform
        }
        
    except Exception as exc:
        logger.error(f"Content validation failed: {str(exc)}")
        return {
            'status': 'error',
            'message': f'Content validation failed: {str(exc)}'
        }

@celery_app.task
def get_optimal_posting_time(platform, timezone='UTC'):
    """Get optimal posting time for a platform"""
    try:
        # Default optimal times (these would ideally come from analytics)
        optimal_times = {
            'twitter': {
                'weekdays': ['09:00', '12:00', '15:00', '17:00'],
                'weekends': ['10:00', '14:00', '16:00']
            },
            'linkedin': {
                'weekdays': ['08:00', '10:00', '12:00', '17:00'],
                'weekends': ['09:00', '11:00']
            },
            'instagram': {
                'weekdays': ['11:00', '13:00', '17:00', '19:00'],
                'weekends': ['10:00', '12:00', '15:00']
            }
        }
        
        current_time = datetime.utcnow()
        is_weekend = current_time.weekday() >= 5  # Saturday = 5, Sunday = 6
        
        platform_times = optimal_times.get(platform.lower(), optimal_times['twitter'])
        times = platform_times['weekends'] if is_weekend else platform_times['weekdays']
        
        # Find next optimal time
        next_optimal = None
        for time_str in times:
            hour, minute = map(int, time_str.split(':'))
            optimal_datetime = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            if optimal_datetime > current_time:
                next_optimal = optimal_datetime
                break
        
        # If no time today, use first time tomorrow
        if next_optimal is None:
            tomorrow = current_time + timedelta(days=1)
            hour, minute = map(int, times[0].split(':'))
            next_optimal = tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        return {
            'status': 'success',
            'platform': platform,
            'next_optimal_time': next_optimal.isoformat(),
            'all_optimal_times': times,
            'timezone': timezone,
            'is_weekend': is_weekend
        }
        
    except Exception as exc:
        logger.error(f"Optimal time calculation failed: {str(exc)}")
        return {
            'status': 'error',
            'message': f'Optimal time calculation failed: {str(exc)}'
        }