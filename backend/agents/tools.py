import requests
from bs4 import BeautifulSoup
import tweepy
from openai import OpenAI
import json
import logging
from typing import Dict, List, Any
from backend.core.config import get_settings
from backend.core.openai_utils import get_openai_completion_params

settings = get_settings()
logger = logging.getLogger(__name__)

class WebScrapingTool:
    """Custom web scraping tool for research agent"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_url(self, url: str) -> Dict[str, Any]:
        """Scrape content from a URL"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.find('title')
            title_text = title.text.strip() if title else "No title found"
            
            # Extract main content
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
                
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return {
                'url': url,
                'title': title_text,
                'content': text[:2000],  # Limit content length
                'status': 'success'
            }
        except Exception as e:
            return {
                'url': url,
                'error': str(e),
                'status': 'error'
            }

class TwitterTool:
    """Twitter API integration for research and posting"""
    
    def __init__(self):
        if settings.twitter_api_key and settings.twitter_api_secret:
            try:
                auth = tweepy.OAuthHandler(
                    settings.twitter_api_key, 
                    settings.twitter_api_secret
                )
                
                if settings.twitter_access_token and settings.twitter_access_token_secret:
                    auth.set_access_token(
                        settings.twitter_access_token,
                        settings.twitter_access_token_secret
                    )
                
                self.api = tweepy.API(auth, wait_on_rate_limit=True)
                self.client = tweepy.Client(
                    bearer_token=settings.twitter_api_key,
                    consumer_key=settings.twitter_api_key,
                    consumer_secret=settings.twitter_api_secret,
                    access_token=settings.twitter_access_token,
                    access_token_secret=settings.twitter_access_token_secret,
                    wait_on_rate_limit=True
                )
            except Exception as e:
                logger.error(f"Twitter API initialization failed: {e}")
                self.api = None
                self.client = None
        else:
            self.api = None
            self.client = None
    
    def search_tweets(self, query: str, count: int = 10) -> List[Dict]:
        """Search for tweets based on query"""
        if not self.client:
            return [{"error": "Twitter API not configured"}]
        
        try:
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=count,
                tweet_fields=['created_at', 'author_id', 'public_metrics']
            )
            
            if not tweets.data:
                return []
            
            results = []
            for tweet in tweets.data:
                results.append({
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': str(tweet.created_at),
                    'author_id': tweet.author_id,
                    'metrics': tweet.public_metrics
                })
            
            return results
        except Exception as e:
            return [{"error": f"Twitter search failed: {str(e)}"}]
    
    def post_tweet(self, content: str) -> Dict[str, Any]:
        """Post a tweet"""
        if not self.client:
            return {"error": "Twitter API not configured", "status": "failed"}
        
        try:
            response = self.client.create_tweet(text=content)
            return {
                "status": "success",
                "tweet_id": response.data['id'],
                "content": content
            }
        except Exception as e:
            return {
                "error": f"Failed to post tweet: {str(e)}",
                "status": "failed"
            }

class OpenAITool:
    """OpenAI integration for content generation and analysis"""
    
    def __init__(self):
        if not settings.openai_api_key:
            logger.warning("OpenAI API key not configured. Content generation will be unavailable.")
            self.client = None
        else:
            self.client = OpenAI(api_key=settings.openai_api_key)
    
    def generate_text(self, prompt: str, model: str = "gpt-5-mini", max_tokens: int = 500, use_web_search: bool = False) -> str:
        """Generate text using OpenAI with fallback models and better error handling"""
        if not self.client:
            return "AI text generation is currently unavailable. Please check your OpenAI API configuration."
        
        # Define fallback models if the specified model fails
        fallback_models = ["gpt-5-mini", "gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
        models_to_try = [model] + [m for m in fallback_models if m != model]
        
        for current_model in models_to_try:
            try:
                logger.info(f"Attempting text generation with model: {current_model}")
                
                if use_web_search and current_model.startswith("gpt-5"):
                    # Use Responses API with web search for GPT-5 models
                    try:
                        response = self.client.responses.create(
                            model=current_model,
                            input=f"Use web search for current information: {prompt}",
                            tools=[
                                {
                                    "type": "web_search"
                                }
                            ],
                            text={"verbosity": "medium"}
                        )
                        result = response.output_text if hasattr(response, 'output_text') else str(response)
                        logger.info(f"Text generation with web search successful using {current_model}")
                        return result
                    except Exception as web_error:
                        logger.warning(f"Web search failed with {current_model}, falling back to regular completion: {web_error}")
                        # Fall through to regular completion
                
                # Use Chat Completions for non-web search requests or web search fallback
                params = get_openai_completion_params(
                    model=current_model,
                    max_tokens=max_tokens,
                    temperature=0.7,
                    messages=[{"role": "user", "content": prompt}]
                )
                response = self.client.chat.completions.create(**params)
                result = response.choices[0].message.content
                logger.info(f"Text generation successful using {current_model}")
                return result
                
            except Exception as e:
                logger.warning(f"Text generation failed with {current_model}: {e}")
                
                # Check for specific error types
                error_str = str(e).lower()
                if "rate limit" in error_str or "429" in error_str:
                    continue  # Try next model
                elif "invalid_request_error" in error_str or "model" in error_str:
                    continue  # Try next model  
                elif "insufficient_quota" in error_str or "quota" in error_str:
                    return "AI service quota exceeded. Please try again later or contact support."
                elif "authentication" in error_str or "401" in error_str:
                    return "AI service authentication failed. Please contact support."
                else:
                    continue  # Try next model for unknown errors
        
        # If all models failed
        logger.error("All text generation models failed")
        return "AI text generation is temporarily unavailable due to service issues. Please try again in a few minutes."
    
    def generate_content(self, prompt: str, content_type: str = "text", platform: str = None, tone: str = "professional") -> Dict[str, Any]:
        """Generate social media content using OpenAI with fallback models"""
        if not self.client:
            return {
                "status": "error",
                "error": "AI content generation is currently unavailable. Please check your OpenAI API configuration."
            }
        
        # List of models to try in order of preference
        models_to_try = ["gpt-5-mini", "gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
        
        # Build context-aware prompt
        context_prompt = f"""Create engaging {content_type} content for social media with the following specifications:

Platform: {platform or 'general social media'}
Tone: {tone}
Content Type: {content_type}

User Request: {prompt}

Requirements:
- Keep it engaging and appropriate for {platform or 'social media'}
- Use a {tone} tone
- Include relevant hashtags if appropriate
- Make it actionable and valuable
- Ensure it follows best practices for {platform or 'social media'}

Please provide:
1. Main content (text)
2. A catchy title/headline
3. Suggested hashtags (if applicable)

Format your response as JSON with keys: content, title, hashtags"""

        for model in models_to_try:
            try:
                logger.info(f"Attempting content generation with model: {model}")
                
                params = get_openai_completion_params(
                    model=model,
                    max_tokens=800,
                    temperature=0.7,
                    messages=[{"role": "user", "content": context_prompt}]
                )
                response = self.client.chat.completions.create(**params)
                
                content_text = response.choices[0].message.content.strip()
                
                # Try to parse as JSON, fallback to text parsing
                try:
                    result = json.loads(content_text)
                    logger.info(f"Content generation successful with model: {model}")
                    return {
                        "status": "success",
                        "content": result.get("content", content_text),
                        "title": result.get("title", "Generated Content"),
                        "hashtags": result.get("hashtags", []),
                        "model_used": model
                    }
                except json.JSONDecodeError:
                    # Fallback: treat entire response as content
                    logger.info(f"Content generation successful (non-JSON) with model: {model}")
                    return {
                        "status": "success",
                        "content": content_text,
                        "title": f"Generated {content_type.title()} Content",
                        "hashtags": [],
                        "model_used": model
                    }
                    
            except Exception as e:
                logger.warning(f"Content generation failed with {model}: {e}")
                
                # Check for specific error types for better user messaging
                error_str = str(e).lower()
                if "rate limit" in error_str or "429" in error_str:
                    continue  # Try next model
                elif "invalid_request_error" in error_str or "model" in error_str:
                    continue  # Try next model
                elif "insufficient_quota" in error_str or "quota" in error_str:
                    return {
                        "status": "error",
                        "error": "AI service quota exceeded. Please try again later or contact support."
                    }
                elif "authentication" in error_str or "401" in error_str:
                    return {
                        "status": "error", 
                        "error": "AI service authentication failed. Please contact support."
                    }
                else:
                    # For unknown errors, continue trying other models
                    continue
        
        # If all models failed
        logger.error("All content generation models failed")
        return {
            "status": "error",
            "error": "AI content generation is temporarily unavailable due to service issues. Please try again in a few minutes."
        }

    def generate_image_prompt(self, content_description: str) -> str:
        """Generate an image prompt based on content description"""
        if not self.client:
            return "Error: OpenAI API key not configured. Please set the OPENAI_API_KEY environment variable."
        
        prompt = f"""Create a detailed image prompt for generating a social media visual based on this content: {content_description}
        
        The prompt should be:
        - Visually appealing and professional
        - Suitable for social media platforms
        - Brand-friendly and engaging
        - Specific enough to generate consistent results
        
        Return only the image prompt, nothing else."""
        
        return self.generate_text(prompt, max_tokens=150)
    
    def create_image(self, prompt: str, size: str = "1024x1024") -> Dict[str, Any]:
        """
        Generate image using OpenAI Responses API with image_generation tool
        
        Uses the enhanced Responses API for real-time streaming and multi-turn editing capabilities,
        providing superior social media content creation with iterative refinement.
        """
        if not self.client:
            return {
                "status": "error",
                "error": "OpenAI API key not configured. Please set the OPENAI_API_KEY environment variable to enable image generation."
            }
        
        try:
            response = self.client.responses.create(
                model="grok-2-image",  # Use Grok-2 image model exclusively
                messages=[
                    {
                        "role": "user", 
                        "content": f"Generate an image with this description: {prompt}"
                    }
                ],
                tools=[
                    {
                        "type": "image_generation",
                        "image_generation": {
                            "size": size,
                            "quality": "standard"
                        }
                    }
                ],
                stream=False
            )
            
            # Extract base64 image data from Responses API tool call result
            image_b64 = None
            if response.content and response.content.tool_calls:
                for tool_call in response.content.tool_calls:
                    if tool_call.type == "image_generation":
                        image_b64 = tool_call.image_generation.b64_json
                        break
            
            if not image_b64:
                raise Exception("No image data returned from OpenAI Responses API")
            image_data_url = f"data:image/png;base64,{image_b64}"
            
            return {
                "status": "success",
                "image_url": image_data_url,
                "prompt": prompt,
                "model": "grok-2-image"
            }
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return {
                "status": "error",
                "error": f"Failed to generate image with Grok-2: {str(e)}"
            }
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        if not self.client:
            return {
                "sentiment": "neutral", 
                "confidence": 0.0, 
                "key_emotions": [],
                "error": "OpenAI API key not configured"
            }
        
        prompt = f"""Analyze the sentiment of this text and return a JSON response with:
        - sentiment: (positive/negative/neutral)
        - confidence: (0-1 scale)
        - key_emotions: (list of emotions detected)
        
        Text: {text}
        
        Return only valid JSON, nothing else."""
        
        try:
            response = self.generate_text(prompt, max_tokens=200)
            return json.loads(response)
        except:
            return {"sentiment": "neutral", "confidence": 0.5, "key_emotions": []}

class FAISSMemoryTool:
    """FAISS vector memory for storing and retrieving content insights"""
    
    def __init__(self):
        if not settings.openai_api_key:
            logger.warning("OpenAI API key not configured. Memory embeddings will be unavailable.")
            self.openai_client = None
        else:
            self.openai_client = OpenAI(api_key=settings.openai_api_key)
        # Initialize FAISS index (placeholder for now)
        self.index = None
        self.stored_content = []
    
    def embed_text(self, text: str) -> List[float]:
        """Create embedding for text"""
        if not self.openai_client:
            logger.warning("Cannot create embedding: OpenAI API key not configured")
            return []
            
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-large",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Embedding failed: {e}")
            return []
    
    def store_content(self, content: str, metadata: Dict[str, Any]):
        """Store content with embeddings (simplified version)"""
        embedding = self.embed_text(content)
        if embedding:
            self.stored_content.append({
                'content': content,
                'metadata': metadata,
                'embedding': embedding
            })
            return True
        return False
    
    def search_similar(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for similar content (simplified version)"""
        query_embedding = self.embed_text(query)
        if not query_embedding:
            return []
        
        # Simplified similarity search (in production, use FAISS)
        results = []
        for item in self.stored_content[-10:]:  # Return recent items
            results.append({
                'content': item['content'],
                'metadata': item['metadata'],
                'similarity': 0.8  # Placeholder similarity score
            })
        
        return results[:top_k]

# Initialize tools
web_scraper = WebScrapingTool()
twitter_tool = TwitterTool()
openai_tool = OpenAITool()
memory_tool = FAISSMemoryTool()