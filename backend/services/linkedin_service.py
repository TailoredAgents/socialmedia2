"""
LinkedIn Service Layer
Integration Specialist Component - Service layer for LinkedIn operations with professional focus
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from dataclasses import asdict

from backend.integrations.linkedin_client import linkedin_client, LinkedInPost, LinkedInArticle, LinkedInAnalytics, LinkedInCompanyPage
from backend.auth.social_oauth import oauth_manager
from backend.db.models import User, ContentItem, ContentPerformanceSnapshot, UserSetting
from backend.services.similarity_service import similarity_service
from backend.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

class LinkedInService:
    """
    LinkedIn service layer with professional content optimization
    
    Features:
    - Professional content posting and optimization
    - Company page management
    - Article publishing
    - Professional network analytics
    - Industry-specific content recommendations
    - Career-focused engagement tracking
    """
    
    def __init__(self):
        """Initialize LinkedIn service"""
        self.platform = "linkedin"
        self.optimal_posting_hours = [8, 12, 17]  # Business hours
        self.optimal_posting_days = ["Tuesday", "Wednesday", "Thursday"]  # Best engagement days
        
        # Professional content categories
        self.professional_categories = [
            "leadership", "career_advice", "industry_insights", "business_strategy",
            "professional_development", "company_culture", "innovation", "networking"
        ]
        
        # LinkedIn-specific engagement thresholds
        self.engagement_thresholds = {
            "high": 5.0,    # High for LinkedIn
            "medium": 2.0,
            "low": 0.5
        }
        
        logger.info("LinkedInService initialized with professional focus")
    
    async def post_content(
        self,
        user_id: int,
        content: str,
        visibility: str = "PUBLIC",
        media_files: Optional[List[bytes]] = None,
        media_types: Optional[List[str]] = None,
        media_filenames: Optional[List[str]] = None,
        article_url: Optional[str] = None,
        company_page_id: Optional[str] = None,
        optimize_for_professional: bool = True,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Post content to LinkedIn with professional optimization
        
        Args:
            user_id: User ID
            content: Content to post
            visibility: Post visibility (PUBLIC, CONNECTIONS, LOGGED_IN)
            media_files: Optional media files
            media_types: Media MIME types
            media_filenames: Original filenames
            article_url: URL to share
            company_page_id: Company page ID for organization posts
            optimize_for_professional: Apply professional tone optimization
            db: Database session
            
        Returns:
            Posting result with professional insights
        """
        try:
            # Get valid access token
            access_token = await oauth_manager.get_valid_token(user_id, self.platform, db)
            if not access_token:
                raise Exception("No valid LinkedIn connection found")
            
            # Optimize content for LinkedIn's professional audience
            if optimize_for_professional:
                content = linkedin_client.optimize_for_linkedin(content)
            
            # Validate content
            is_valid, error_msg = linkedin_client.validate_post_content(content)
            if not is_valid:
                raise ValueError(error_msg)
            
            # Handle media uploads
            media_assets = []
            if media_files and media_types and media_filenames:
                for media_data, media_type, filename in zip(media_files, media_types, media_filenames):
                    asset_urn = await linkedin_client.upload_media(
                        access_token, media_data, media_type, filename
                    )
                    media_assets.append(asset_urn)
            
            # Determine author type and ID
            author_type = "organization" if company_page_id else "person"
            author_id = company_page_id if company_page_id else None
            
            # Create post
            post = await linkedin_client.create_post(
                access_token=access_token,
                text=content,
                visibility=visibility,
                media_assets=media_assets if media_assets else None,
                article_url=article_url,
                author_type=author_type,
                author_id=author_id
            )
            
            # Store in database
            content_item = await self._store_content_item(
                user_id=user_id,
                content=content,
                platform_post_id=post.id,
                post_data=post,
                company_page_id=company_page_id,
                db=db
            )
            
            # Schedule analytics collection
            await self._schedule_analytics_collection(post.id, user_id, db)
            
            # Generate professional insights
            professional_insights = await self._generate_professional_insights(content, post, db)
            
            return {
                "status": "success",
                "post_id": post.id,
                "content_item_id": content_item.id,
                "post_url": f"https://www.linkedin.com/feed/update/{post.id}",
                "posted_at": post.created_at.isoformat(),
                "visibility": post.visibility,
                "is_company_post": bool(company_page_id),
                "professional_insights": professional_insights,
                "optimization_applied": optimize_for_professional
            }
            
        except Exception as e:
            logger.error(f"Failed to post LinkedIn content: {e}")
            raise
    
    async def create_article(
        self,
        user_id: int,
        title: str,
        content: str,
        visibility: str = "PUBLIC",
        tags: Optional[List[str]] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Create a LinkedIn article
        
        Args:
            user_id: User ID
            title: Article title
            content: Article content (HTML supported)
            visibility: Article visibility
            tags: Article tags
            db: Database session
            
        Returns:
            Article creation result
        """
        try:
            # Get valid access token
            access_token = await oauth_manager.get_valid_token(user_id, self.platform, db)
            if not access_token:
                raise Exception("No valid LinkedIn connection found")
            
            # Create article
            article = await linkedin_client.create_article(
                access_token=access_token,
                title=title,
                content=content,
                visibility=visibility,
                tags=tags
            )
            
            # Store article as content item
            content_item = await self._store_content_item(
                user_id=user_id,
                content=f"{title}\n\n{content}",
                platform_post_id=article.id,
                content_type="article",
                article_data=article,
                db=db
            )
            
            return {
                "status": "success",
                "article_id": article.id,
                "content_item_id": content_item.id,
                "article_url": article.canonical_url,
                "title": article.title,
                "published_at": article.published_at.isoformat(),
                "visibility": visibility,
                "tags": tags or []
            }
            
        except Exception as e:
            logger.error(f"Failed to create LinkedIn article: {e}")
            raise
    
    async def _store_content_item(
        self,
        user_id: int,
        content: str,
        platform_post_id: str,
        post_data: Optional[LinkedInPost] = None,
        article_data: Optional[LinkedInArticle] = None,
        company_page_id: Optional[str] = None,
        content_type: str = "text",
        db: Session = None
    ) -> ContentItem:
        """Store LinkedIn content item in database"""
        try:
            # Extract professional elements
            hashtags = linkedin_client.extract_hashtags(content)
            mentions = linkedin_client.extract_mentions(content)
            
            # Determine content format
            content_format = "article" if article_data else "post"
            if company_page_id:
                content_format = f"company_{content_format}"
            
            # Create content item
            content_item = ContentItem(
                user_id=user_id,
                content=content,
                platform=self.platform,
                content_type=content_type,
                content_format=content_format,
                status="published",
                platform_post_id=platform_post_id,
                platform_url=f"https://www.linkedin.com/feed/update/{platform_post_id}",
                published_at=post_data.created_at if post_data else article_data.published_at,
                hashtags=hashtags,
                mentions=mentions,
                tone="professional",  # LinkedIn default
                reading_level="intermediate"  # Professional content assumption
            )
            
            # Add LinkedIn-specific metadata
            linkedin_metadata = {
                "visibility": post_data.visibility if post_data else "PUBLIC",
                "is_company_post": bool(company_page_id),
                "company_page_id": company_page_id,
                "professional_category": self._categorize_professional_content(content),
                "industry_relevance": self._assess_industry_relevance(content),
                "networking_potential": self._assess_networking_potential(content)
            }
            
            if article_data:
                linkedin_metadata.update({
                    "article_title": article_data.title,
                    "canonical_url": article_data.canonical_url,
                    "word_count": len(content.split())
                })
            
            content_item.content_metadata = linkedin_metadata
            
            if db:
                db.add(content_item)
                db.commit()
                db.refresh(content_item)
            
            logger.info(f"Stored LinkedIn content item {content_item.id}")
            return content_item
            
        except Exception as e:
            if db:
                db.rollback()
            logger.error(f"Failed to store LinkedIn content item: {e}")
            raise
    
    def _categorize_professional_content(self, content: str) -> str:
        """Categorize content by professional topic"""
        content_lower = content.lower()
        
        # Simple keyword-based categorization
        category_keywords = {
            "leadership": ["leadership", "manage", "team", "leader", "executive"],
            "career_advice": ["career", "job", "interview", "resume", "professional development"],
            "industry_insights": ["industry", "market", "trend", "analysis", "forecast"],
            "business_strategy": ["strategy", "business", "growth", "profit", "revenue"],
            "innovation": ["innovation", "technology", "digital", "ai", "automation"],
            "networking": ["network", "connection", "relationship", "collaboration"],
            "company_culture": ["culture", "values", "workplace", "employee", "team"]
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                return category
        
        return "general"
    
    def _assess_industry_relevance(self, content: str) -> float:
        """Assess how relevant content is to professional industries (0-1 score)"""
        # Simplified industry relevance scoring
        professional_indicators = [
            "business", "professional", "industry", "market", "strategy",
            "leadership", "career", "innovation", "technology", "finance",
            "consulting", "management", "sales", "marketing", "hr"
        ]
        
        content_lower = content.lower()
        matches = sum(1 for indicator in professional_indicators if indicator in content_lower)
        
        return min(1.0, matches / len(professional_indicators) * 3)  # Scale appropriately
    
    def _assess_networking_potential(self, content: str) -> float:
        """Assess content's potential for professional networking (0-1 score)"""
        # Look for networking-friendly elements
        networking_indicators = [
            "?",  # Questions encourage engagement
            "share", "thoughts", "experience", "opinion", "agree", "disagree",
            "comment", "connect", "network", "collaboration", "partnership"
        ]
        
        content_lower = content.lower()
        score = 0.0
        
        # Question marks increase networking potential
        question_count = content.count("?")
        score += min(0.3, question_count * 0.1)
        
        # Networking keywords
        keyword_matches = sum(1 for indicator in networking_indicators if indicator in content_lower)
        score += min(0.5, keyword_matches * 0.05)
        
        # Call-to-action phrases
        cta_phrases = ["what do you think", "share your", "tell me", "would love to hear"]
        if any(phrase in content_lower for phrase in cta_phrases):
            score += 0.2
        
        return min(1.0, score)
    
    async def _generate_professional_insights(
        self,
        content: str,
        post: LinkedInPost,
        db: Session
    ) -> Dict[str, Any]:
        """Generate insights about professional content performance"""
        try:
            insights = {
                "professional_category": self._categorize_professional_content(content),
                "industry_relevance": self._assess_industry_relevance(content),
                "networking_potential": self._assess_networking_potential(content),
                "content_analysis": {
                    "character_count": len(content),
                    "word_count": len(content.split()),
                    "hashtag_count": len(linkedin_client.extract_hashtags(content)),
                    "mention_count": len(linkedin_client.extract_mentions(content)),
                    "question_count": content.count("?")
                },
                "optimization_suggestions": []
            }
            
            # Generate optimization suggestions
            suggestions = []
            
            if insights["networking_potential"] < 0.5:
                suggestions.append("Consider adding a question to encourage engagement")
            
            if insights["content_analysis"]["hashtag_count"] == 0:
                suggestions.append("Add relevant industry hashtags to increase visibility")
            elif insights["content_analysis"]["hashtag_count"] > 5:
                suggestions.append("Consider reducing hashtags to 3-5 for better engagement")
            
            if len(content) < 100:
                suggestions.append("Expand content with more professional insights for better engagement")
            
            if insights["industry_relevance"] < 0.3:
                suggestions.append("Add more industry-specific terminology to increase professional relevance")
            
            insights["optimization_suggestions"] = suggestions
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate professional insights: {e}")
            return {}
    
    async def _schedule_analytics_collection(self, post_id: str, user_id: int, db: Session):
        """Schedule analytics collection for LinkedIn post"""
        try:
            # LinkedIn analytics are less immediate than Twitter
            await asyncio.sleep(10)  # Brief delay
            await self.collect_post_analytics(user_id, post_id, db)
        except Exception as e:
            logger.error(f"Failed to schedule LinkedIn analytics collection: {e}")
    
    async def collect_post_analytics(
        self,
        user_id: int,
        post_id: str,
        db: Session
    ) -> LinkedInAnalytics:
        """
        Collect and store analytics for a LinkedIn post
        
        Args:
            user_id: User ID
            post_id: Post ID
            db: Database session
            
        Returns:
            Analytics data
        """
        try:
            # Get valid access token
            access_token = await oauth_manager.get_valid_token(user_id, self.platform, db)
            if not access_token:
                raise Exception("No valid LinkedIn connection found")
            
            # Get analytics from LinkedIn
            analytics = await linkedin_client.get_post_analytics(access_token, post_id)
            
            # Update content item with latest metrics
            content_item = db.query(ContentItem).filter(
                ContentItem.platform_post_id == post_id,
                ContentItem.user_id == user_id
            ).first()
            
            if content_item:
                content_item.likes_count = analytics.reactions
                content_item.shares_count = analytics.shares
                content_item.comments_count = analytics.comments
                content_item.reach_count = analytics.impressions
                content_item.click_count = analytics.clicks
                content_item.engagement_rate = analytics.engagement_rate
                content_item.last_performance_update = datetime.utcnow()
                
                # Update performance tier based on LinkedIn engagement patterns
                content_item.performance_tier = self._calculate_performance_tier(analytics.engagement_rate)
                
                # Create performance snapshot
                snapshot = ContentPerformanceSnapshot(
                    content_item_id=content_item.id,
                    likes_count=analytics.reactions,
                    shares_count=analytics.shares,
                    comments_count=analytics.comments,
                    reach_count=analytics.impressions,
                    click_count=analytics.clicks,
                    engagement_rate=analytics.engagement_rate,
                    platform_metrics={
                        "unique_impressions": analytics.unique_impressions,
                        "click_through_rate": analytics.click_through_rate,
                        "professional_engagement": True
                    }
                )
                
                db.add(snapshot)
                db.commit()
            
            logger.info(f"Collected LinkedIn analytics for post {post_id}")
            return analytics
            
        except Exception as e:
            if db:
                db.rollback()
            logger.error(f"Failed to collect LinkedIn analytics: {e}")
            raise
    
    def _calculate_performance_tier(self, engagement_rate: float) -> str:
        """Calculate performance tier for LinkedIn content"""
        if engagement_rate >= self.engagement_thresholds["high"]:
            return "high"
        elif engagement_rate >= self.engagement_thresholds["medium"]:
            return "medium"
        elif engagement_rate >= self.engagement_thresholds["low"]:
            return "low"
        else:
            return "poor"
    
    async def get_company_pages(
        self,
        user_id: int,
        db: Session
    ) -> List[Dict[str, Any]]:
        """
        Get company pages the user can manage
        
        Args:
            user_id: User ID
            db: Database session
            
        Returns:
            List of company pages with management capabilities
        """
        try:
            # Get valid access token
            access_token = await oauth_manager.get_valid_token(user_id, self.platform, db)
            if not access_token:
                raise Exception("No valid LinkedIn connection found")
            
            # Get company pages
            company_pages = await linkedin_client.get_company_pages(access_token)
            
            # Format for response
            formatted_pages = []
            for page in company_pages:
                formatted_pages.append({
                    "id": page.id,
                    "name": page.name,
                    "description": page.description,
                    "follower_count": page.follower_count,
                    "logo_url": page.logo_url,
                    "industry": page.industry,
                    "company_size": page.company_size,
                    "website_url": page.website_url,
                    "can_post": True,  # User has admin access
                    "page_url": f"https://www.linkedin.com/company/{page.id}"
                })
            
            return formatted_pages
            
        except Exception as e:
            logger.error(f"Failed to get LinkedIn company pages: {e}")
            return []
    
    async def get_professional_content_suggestions(
        self,
        user_id: int,
        topic: str,
        industry: Optional[str] = None,
        content_type: str = "post",
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Get LinkedIn-specific professional content suggestions
        
        Args:
            user_id: User ID
            topic: Content topic
            industry: Target industry
            content_type: "post" or "article"
            db: Database session
            
        Returns:
            Professional content suggestions
        """
        try:
            # Get base recommendations from similarity service
            recommendations = await similarity_service.get_content_recommendations(
                topic=topic,
                target_platform=self.platform,
                db=db
            )
            
            # Enhance with LinkedIn professional focus
            professional_suggestions = []
            
            for rec in recommendations:
                # Add professional enhancements
                enhanced_suggestions = []
                for suggestion in rec.content_suggestions:
                    # Analyze professional elements
                    professional_score = self._assess_industry_relevance(suggestion.content)
                    networking_score = self._assess_networking_potential(suggestion.content)
                    
                    enhanced_suggestions.append({
                        **suggestion.__dict__,
                        "professional_score": professional_score,
                        "networking_potential": networking_score,
                        "industry_relevance": industry if industry else "general",
                        "recommended_format": self._recommend_content_format(suggestion.content),
                        "professional_enhancements": self._suggest_professional_enhancements(suggestion.content)
                    })
                
                professional_suggestions.append({
                    **rec.__dict__,
                    "content_suggestions": enhanced_suggestions,
                    "linkedin_specific": {
                        "optimal_posting_times": self.optimal_posting_hours,
                        "optimal_posting_days": self.optimal_posting_days,
                        "professional_categories": self.professional_categories,
                        "industry_hashtags": self._get_industry_hashtags(industry),
                        "engagement_strategies": self._get_engagement_strategies(content_type)
                    }
                })
            
            return {
                "status": "success",
                "topic": topic,
                "industry": industry,
                "content_type": content_type,
                "platform": self.platform,
                "suggestions": professional_suggestions
            }
            
        except Exception as e:
            logger.error(f"Failed to get LinkedIn content suggestions: {e}")
            raise
    
    def _recommend_content_format(self, content: str) -> str:
        """Recommend best format for LinkedIn content"""
        word_count = len(content.split())
        
        if word_count > 500:
            return "article"
        elif word_count > 100:
            return "long_form_post"
        else:
            return "standard_post"
    
    def _suggest_professional_enhancements(self, content: str) -> List[str]:
        """Suggest ways to make content more professional"""
        enhancements = []
        
        # Check for professional tone
        if not any(word in content.lower() for word in ["professional", "business", "industry", "experience"]):
            enhancements.append("Add professional context or industry insights")
        
        # Check for networking elements
        if "?" not in content:
            enhancements.append("Consider adding a thought-provoking question")
        
        # Check for value proposition
        if not any(word in content.lower() for word in ["tip", "insight", "lesson", "advice", "strategy"]):
            enhancements.append("Include actionable insights or professional tips")
        
        # Check for credibility indicators
        if not any(word in content.lower() for word in ["experience", "learned", "project", "team", "client"]):
            enhancements.append("Add personal or professional experience to build credibility")
        
        return enhancements
    
    def _get_industry_hashtags(self, industry: Optional[str]) -> List[str]:
        """Get relevant hashtags for industry"""
        industry_hashtags = {
            "technology": ["#Tech", "#Innovation", "#AI", "#DigitalTransformation", "#SaaS"],
            "finance": ["#Finance", "#FinTech", "#Banking", "#Investment", "#Economics"],
            "healthcare": ["#Healthcare", "#MedTech", "#Wellness", "#HealthInnovation", "#PatientCare"],
            "consulting": ["#Consulting", "#Strategy", "#BusinessTransformation", "#Leadership", "#Growth"],
            "marketing": ["#Marketing", "#DigitalMarketing", "#ContentMarketing", "#Advertising", "#Branding"],
            "sales": ["#Sales", "#SalesStrategy", "#B2B", "#CustomerSuccess", "#Revenue"],
            "hr": ["#HR", "#PeopleManagement", "#Recruitment", "#TalentAcquisition", "#WorkplaceCulture"]
        }
        
        if industry and industry.lower() in industry_hashtags:
            return industry_hashtags[industry.lower()]
        
        # Default professional hashtags
        return ["#Professional", "#Business", "#Career", "#Leadership", "#Growth"]
    
    def _get_engagement_strategies(self, content_type: str) -> List[str]:
        """Get engagement strategies based on content type"""
        strategies = {
            "post": [
                "Ask open-ended questions to encourage comments",
                "Share personal professional experiences",
                "Use industry-specific terminology",
                "Tag relevant connections when appropriate",
                "Post during business hours for maximum visibility"
            ],
            "article": [
                "Create compelling headlines that promise value",
                "Use subheadings to improve readability",
                "Include actionable takeaways",
                "Add a strong call-to-action at the end",
                "Share the article as a post to increase reach"
            ]
        }
        
        return strategies.get(content_type, strategies["post"])
    
    async def delete_content(
        self,
        user_id: int,
        content_item_id: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Delete LinkedIn content
        
        Args:
            user_id: User ID
            content_item_id: Content item ID
            db: Database session
            
        Returns:
            Deletion result
        """
        try:
            # Get content item
            content_item = db.query(ContentItem).filter(
                ContentItem.id == content_item_id,
                ContentItem.user_id == user_id,
                ContentItem.platform == self.platform
            ).first()
            
            if not content_item:
                raise Exception("Content item not found")
            
            # Get valid access token
            access_token = await oauth_manager.get_valid_token(user_id, self.platform, db)
            if not access_token:
                raise Exception("No valid LinkedIn connection found")
            
            # Delete from LinkedIn
            success = await linkedin_client.delete_post(access_token, content_item.platform_post_id)
            
            if success:
                # Update database
                content_item.status = "deleted"
                db.commit()
                
                logger.info(f"Deleted LinkedIn content {content_item_id}")
                
                return {
                    "status": "success",
                    "content_item_id": content_item_id,
                    "post_id": content_item.platform_post_id,
                    "deleted_at": datetime.utcnow().isoformat()
                }
            else:
                raise Exception("Failed to delete post from LinkedIn")
            
        except Exception as e:
            if db:
                db.rollback()
            logger.error(f"Failed to delete LinkedIn content: {e}")
            raise

# Global LinkedIn service instance
linkedin_service = LinkedInService()