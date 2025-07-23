from celery import current_task
from backend.tasks.celery_app import celery_app
from backend.agents.crew_config import research_agent, create_research_task
from backend.agents.tools import web_scraper, twitter_tool, memory_tool, openai_tool
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def run_daily_research(self, topics=None):
    """Run daily research across multiple topics"""
    if topics is None:
        topics = [
            "social media trends",
            "AI marketing",
            "content marketing",
            "digital transformation",
            "social media best practices"
        ]
    
    try:
        results = []
        total_topics = len(topics)
        
        current_task.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': total_topics, 'status': 'Starting research...'}
        )
        
        for i, topic in enumerate(topics):
            current_task.update_state(
                state='PROGRESS',
                meta={'current': i+1, 'total': total_topics, 'status': f'Researching: {topic}'}
            )
            
            # Create research task
            research_task = create_research_task(topic)
            
            # Execute research
            research_result = research_agent.execute_task(research_task)
            
            # Store in memory
            memory_tool.store_content(
                content=str(research_result),
                metadata={
                    'type': 'research',
                    'topic': topic,
                    'research_date': current_task.request.utc
                }
            )
            
            results.append({
                'topic': topic,
                'result': str(research_result),
                'status': 'completed'
            })
        
        current_task.update_state(
            state='PROGRESS',
            meta={'current': total_topics, 'total': total_topics, 'status': 'Research completed!'}
        )
        
        return {
            'status': 'success',
            'message': f'Research completed for {len(results)} topics',
            'topics_researched': len(results),
            'results': results
        }
        
    except Exception as exc:
        logger.error(f"Daily research failed: {str(exc)}")
        return {
            'status': 'error',
            'message': f'Daily research failed: {str(exc)}'
        }

@celery_app.task
def research_trending_topics():
    """Research what's trending on social media"""
    try:
        # Search for trending topics on Twitter
        trending_searches = [
            "trending AI",
            "social media 2025",
            "marketing trends",
            "digital marketing",
            "content strategy"
        ]
        
        results = []
        
        for search in trending_searches:
            # Twitter search
            tweets = twitter_tool.search_tweets(search, count=10)
            
            if tweets and not any("error" in tweet for tweet in tweets):
                # Analyze trending content
                tweet_texts = [tweet['text'] for tweet in tweets if 'text' in tweet]
                
                analysis_prompt = f"""Analyze these tweets about '{search}' and identify:
                1. Key trending themes
                2. Common hashtags
                3. Engagement patterns
                4. Content opportunities
                
                Tweets: {tweet_texts[:5]}  # Limit to first 5 tweets
                
                Provide a concise analysis with actionable insights."""
                
                analysis = openai_tool.generate_text(analysis_prompt, max_tokens=300)
                
                result = {
                    'search_term': search,
                    'tweet_count': len(tweets),
                    'analysis': analysis,
                    'sample_tweets': tweet_texts[:3]
                }
                
                results.append(result)
                
                # Store in memory
                memory_tool.store_content(
                    content=analysis,
                    metadata={
                        'type': 'trending_analysis',
                        'search_term': search,
                        'tweet_count': len(tweets)
                    }
                )
        
        return {
            'status': 'success',
            'message': f'Trending research completed for {len(results)} topics',
            'results': results
        }
        
    except Exception as exc:
        logger.error(f"Trending research failed: {str(exc)}")
        return {
            'status': 'error',
            'message': f'Trending research failed: {str(exc)}'
        }

@celery_app.task
def research_competitor_content(competitors=None):
    """Research competitor content and strategies"""
    if competitors is None:
        competitors = [
            "@buffer",
            "@hootsuite", 
            "@sproutsocial",
            "@hubspot"
        ]
    
    try:
        results = []
        
        for competitor in competitors:
            # Search for competitor content
            competitor_tweets = twitter_tool.search_tweets(f"from:{competitor}", count=5)
            
            if competitor_tweets and not any("error" in tweet for tweet in competitor_tweets):
                tweet_texts = [tweet['text'] for tweet in competitor_tweets if 'text' in tweet]
                
                analysis_prompt = f"""Analyze {competitor}'s recent content strategy:
                
                Recent posts: {tweet_texts}
                
                Identify:
                1. Content themes and topics
                2. Posting style and tone
                3. Engagement tactics used
                4. Hashtag strategies
                5. Content opportunities we could explore
                
                Provide insights for our content strategy."""
                
                analysis = openai_tool.generate_text(analysis_prompt, max_tokens=400)
                
                result = {
                    'competitor': competitor,
                    'posts_analyzed': len(tweet_texts),
                    'analysis': analysis,
                    'sample_content': tweet_texts[:2]
                }
                
                results.append(result)
                
                # Store in memory
                memory_tool.store_content(
                    content=analysis,
                    metadata={
                        'type': 'competitor_analysis',
                        'competitor': competitor,
                        'posts_count': len(tweet_texts)
                    }
                )
        
        return {
            'status': 'success',
            'message': f'Competitor analysis completed for {len(results)} competitors',
            'results': results
        }
        
    except Exception as exc:
        logger.error(f"Competitor research failed: {str(exc)}")
        return {
            'status': 'error',
            'message': f'Competitor research failed: {str(exc)}'
        }

@celery_app.task
def research_web_content(urls=None):
    """Research content from specified URLs"""
    if urls is None:
        urls = [
            "https://blog.hubspot.com/marketing",
            "https://buffer.com/resources",
            "https://blog.hootsuite.com"
        ]
    
    try:
        results = []
        
        for url in urls:
            scraped_data = web_scraper.scrape_url(url)
            
            if scraped_data['status'] == 'success':
                # Analyze the content
                analysis_prompt = f"""Analyze this web content for social media opportunities:
                
                Title: {scraped_data['title']}
                Content: {scraped_data['content'][:1000]}...
                
                Identify:
                1. Key insights and takeaways
                2. Social media content opportunities
                3. Trending topics mentioned
                4. Actionable tips for our audience
                
                Provide a summary with content ideas."""
                
                analysis = openai_tool.generate_text(analysis_prompt, max_tokens=350)
                
                result = {
                    'url': url,
                    'title': scraped_data['title'],
                    'analysis': analysis,
                    'content_length': len(scraped_data['content'])
                }
                
                results.append(result)
                
                # Store in memory
                memory_tool.store_content(
                    content=analysis,
                    metadata={
                        'type': 'web_content_analysis',
                        'source_url': url,
                        'title': scraped_data['title']
                    }
                )
        
        return {
            'status': 'success',
            'message': f'Web content research completed for {len(results)} URLs',
            'results': results
        }
        
    except Exception as exc:
        logger.error(f"Web content research failed: {str(exc)}")
        return {
            'status': 'error',
            'message': f'Web content research failed: {str(exc)}'
        }