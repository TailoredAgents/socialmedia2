"""
Lightweight CrewAI setup - minimal memory footprint
Only loads essential components for social media automation
"""
import os
from typing import Optional, Dict, Any

# Lazy imports to reduce memory usage
def get_openai_client():
    """Lazy load OpenAI client only when needed"""
    from openai import OpenAI
    from backend.core.config import get_settings
    settings = get_settings()
    return OpenAI(api_key=settings.openai_api_key)

def get_search_tool():
    """Lazy load search tool only when needed"""
    try:
        from crewai_tools import SerperDevTool
        from backend.core.config import get_settings
        settings = get_settings()
        return SerperDevTool(api_key=settings.serper_api_key)
    except ImportError:
        return None

class LightweightAgent:
    """Minimal agent without heavy CrewAI dependencies"""
    
    def __init__(self, role: str, goal: str, backstory: str):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self._openai_client = None
        self._search_tool = None
    
    @property
    def openai_client(self):
        if self._openai_client is None:
            self._openai_client = get_openai_client()
        return self._openai_client
    
    @property
    def search_tool(self):
        if self._search_tool is None:
            self._search_tool = get_search_tool()
        return self._search_tool
    
    async def execute_task(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a task using minimal resources"""
        try:
            # Use direct OpenAI API instead of full CrewAI
            response = self.openai_client.chat.completions.create(
                model="gpt-5-mini",  # Updated to GPT-5 mini
                messages=[
                    {"role": "system", "content": f"You are a {self.role}. {self.backstory}"},
                    {"role": "user", "content": f"Goal: {self.goal}\n\nTask: {task_description}"}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return {
                "status": "success",
                "result": response.choices[0].message.content.strip(),
                "agent": self.role,
                "memory_efficient": True
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "agent": self.role
            }

# Pre-defined lightweight agents
research_agent = LightweightAgent(
    role="Research Specialist",
    goal="Find trending topics and insights",
    backstory="You efficiently research social media trends using minimal resources."
)

content_agent = LightweightAgent(
    role="Content Creator",
    goal="Create engaging social media content",
    backstory="You create compelling content optimized for different platforms."
)

async def lightweight_daily_workflow(topic: str = "social media trends") -> Dict[str, Any]:
    """Lightweight version of daily content workflow"""
    
    # Step 1: Research (minimal)
    research_result = await research_agent.execute_task(
        f"Research current trends about {topic}. Provide 3 key insights in bullet points."
    )
    
    if research_result["status"] != "success":
        return {"status": "error", "step": "research", "error": research_result.get("error")}
    
    # Step 2: Content generation
    research_insights = research_result["result"]
    content_result = await content_agent.execute_task(
        f"Based on these insights: {research_insights}\n\nCreate 2 social media posts - one for Twitter and one for Instagram. Include relevant hashtags."
    )
    
    return {
        "status": "success",
        "workflow": "lightweight_daily",
        "research": research_insights,
        "content": content_result.get("result", ""),
        "memory_optimized": True
    }