"""
Skill: skill_analyze_trendstrends

Analyzes content for trending topics using MCP resources and semantic analysis.
Real MCP integration for trend fetching.
"""

import asyncio
import json
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

# Import MCP client
try:
    from services.mcp_client import create_news_mcp_client, MCPClient
except ImportError:
    MCPClient = None


# Relevance threshold constant (from SRS)
RELEVANCE_THRESHOLD = 0.75


# Input Schema
class AnalyzeTrendsInput(BaseModel):
    """Input contract for skill_analyze_trends"""
    content: str = Field(..., description="Content to analyze for trends")
    platform: str = Field(..., description="Platform: twitter | instagram | tiktok")
    max_results: int = Field(default=10, ge=1, le=100, description="Maximum number of trends to return")
    min_relevance_score: float = Field(default=0.75, ge=0.0, le=1.0, description="Minimum relevance threshold")
    topic: Optional[str] = Field(default=None, description="Specific topic to analyze")


# Trend Data Point
class TrendData(BaseModel):
    """Individual trend data point"""
    topic: str
    score: float = Field(..., ge=0.0, le=1.0)
    velocity: str = Field(..., pattern="^(rising|stable|declining)$")
    platform: str = Field(default="twitter")
    volume: Optional[int] = None
    engagement_rate: Optional[float] = None


# Output Schema
class AnalyzeTrendsOutput(BaseModel):
    """Output contract for skill_analyze_trends"""
    status: str = Field(..., pattern="^(success|error)$")
    trends: list[TrendData] = Field(default_factory=list)
    error_message: Optional[str] = None
    analysis_metadata: dict = Field(default_factory=dict)


class TrendAnalyzer:
    """
    Trend analysis engine using MCP resources.
    
    Provides:
    - MCP-based trend fetching
    - Relevance scoring
    - Velocity analysis
    """
    
    def __init__(self):
        """Initialize the analyzer."""
        self.name = "trend_analyzer"
        self.version = "1.0.0"
        self._mcp_client: Optional[MCPClient] = None
    
    def _get_mcp_client(self) -> MCPClient:
        """Get or create MCP client."""
        if self._mcp_client is None:
            if MCPClient:
                self._mcp_client = create_news_mcp_client()
        return self._mcp_client
    
    def _calculate_relevance(self, trend: dict, content: str) -> float:
        """
        Calculate relevance score between trend and content.
        
        Uses simple keyword matching for demo.
        In production, would use embedding similarity.
        """
        content_words = set(content.lower().split())
        trend_words = set(trend.get("topic", "").lower().split())
        
        if not content_words:
            return 0.5
        
        # Calculate Jaccard similarity
        overlap = len(content_words & trend_words)
        union = len(content_words | trend_words)
        
        if union == 0:
            return 0.5
        
        return overlap / union
    
    def _determine_velocity(self, volume: int, previous_volume: int = None) -> str:
        """
        Determine trend velocity based on volume changes.
        
        Returns: rising | stable | declining
        """
        if previous_volume is None:
            return "stable"
        
        if volume > previous_volume * 1.1:
            return "rising"
        elif volume < previous_volume * 0.9:
            return "declining"
        else:
            return "stable"
    
    def _fetch_trends_from_mcp(self, topic: str, limit: int) -> list[dict]:
        """
        Fetch trends from MCP news server.
        
        Returns list of trend dictionaries.
        """
        client = self._get_mcp_client()
        
        if client and client.is_connected():
            try:
                # Call MCP tool
                result = asyncio.run(
                    client.call_tool("fetch_trends", {
                        "topic": topic,
                        "limit": limit
                    })
                )
                return result.get("trends", [])
            except Exception as e:
                print(f"MCP fetch error: {e}")
                return []
        else:
            # Return mock trends for demo
            return self._get_mock_trends(topic, limit)
    
    def _get_mock_trends(self, topic: str, limit: int) -> list[dict]:
        """Generate mock trends for demo/testing."""
        base_trends = [
            {"topic": f"AI Agents in {topic}", "volume": 15000, "sentiment": 0.85},
            {"topic": f"Autonomous {topic} Systems", "volume": 12000, "sentiment": 0.78},
            {"topic": f"LLM Applications {topic}", "volume": 10000, "sentiment": 0.72},
            {"topic": f"Machine Learning {topic}", "volume": 8500, "sentiment": 0.68},
            {"topic": f"AI Ethics in {topic}", "volume": 7000, "sentiment": 0.55},
            {"topic": f"Transformer Models {topic}", "volume": 5500, "sentiment": 0.70},
            {"topic": f"Neural Networks {topic}", "volume": 4500, "sentiment": 0.65},
            {"topic": f"Deep Learning {topic}", "volume": 4000, "sentiment": 0.62},
            {"topic": f"AI Automation {topic}", "volume": 3500, "sentiment": 0.75},
            {"topic": f"Generative AI {topic}", "volume": 3000, "sentiment": 0.80},
        ]
        return base_trends[:limit]


class AnalyzeTrendsSkill:
    """Skill class for trend analysis."""
    
    def __init__(self):
        """Initialize the skill."""
        self.name = "skill_analyze_trends"
        self.version = "1.0.0"
        self.analyzer = TrendAnalyzer()
    
    def execute(self, content: str, platform: str, max_results: int = 10,
                min_relevance_score: float = 0.75,
                topic: str = None) -> AnalyzeTrendsOutput:
        """
        Analyze content for trending topics.
        
        Args:
            content: Content to analyze for trends
            platform: Source platform (twitter, instagram, tiktok)
            max_results: Maximum number of trends to return
            min_relevance_score: Minimum relevance threshold
            topic: Specific topic to analyze
            
        Returns:
            AnalyzeTrendsOutput with identified trends
        """
        try:
            # Extract topic from content if not provided
            if topic is None:
                topic = self._extract_topic(content)
            
            # Fetch trends from MCP
            raw_trends = self.analyzer._fetch_trends_from_mcp(topic, max_results * 2)
            
            # Calculate relevance and filter
            filtered_trends = []
            for trend in raw_trends:
                relevance = self.analyzer._calculate_relevance(trend, content)
                
                if relevance >= min_relevance_score:
                    velocity = self.analyzer._determine_velocity(
                        trend.get("volume", 0)
                    )
                    
                    filtered_trends.append(TrendData(
                        topic=trend.get("topic", "Unknown"),
                        score=relevance,
                        velocity=velocity,
                        platform=platform,
                        volume=trend.get("volume"),
                        engagement_rate=trend.get("sentiment")
                    ))
            
            # Sort by score and limit results
            filtered_trends.sort(key=lambda x: x.score, reverse=True)
            filtered_trends = filtered_trends[:max_results]
            
            return AnalyzeTrendsOutput(
                status="success",
                trends=filtered_trends,
                analysis_metadata={
                    "content_length": len(content),
                    "platform": platform,
                    "topic_analyzed": topic,
                    "min_relevance_threshold": min_relevance_score,
                    "total_trends_found": len(raw_trends),
                    "trends_returned": len(filtered_trends),
                    "processed_at": datetime.now().isoformat(),
                }
            )
            
        except Exception as e:
            return AnalyzeTrendsOutput(
                status="error",
                error_message=str(e)
            )
    
    def _extract_topic(self, content: str) -> str:
        """
        Extract main topic from content.
        
        Uses simple keyword extraction for demo.
        In production, would use NER or LLM.
        """
        # Common tech topics
        topics = [
            "AI", "artificial intelligence", "machine learning",
            "technology", "software", "cloud", "data",
            "robotics", "automation", "LLM", "GPT"
        ]
        
        content_lower = content.lower()
        
        for topic in topics:
            if topic.lower() in content_lower:
                return topic
        
        # Default to general
        return "technology"


async def async_execute_trend_analysis(
    content: str,
    platform: str = "twitter",
    max_results: int = 10
) -> AnalyzeTrendsOutput:
    """Async wrapper for trend analysis."""
    skill = AnalyzeTrendsSkill()
    return skill.execute(content, platform, max_results)


if __name__ == "__main__":
    # Test the skill
    skill = AnalyzeTrendsSkill()
    
    result = skill.execute(
        content="AI agents are transforming how we work with technology and automation",
        platform="twitter",
        max_results=5,
        min_relevance_score=0.6
    )
    
    print("=== Trend Analysis Result ===")
    print(f"Status: {result.status}")
    print(f"Trends Found: {len(result.trends)}")
    print(f"Metadata: {json.dumps(result.analysis_metadata, indent=2)}")
    print("\nTop Trends:")
    
    for i, trend in enumerate(result.trends, 1):
        print(f"{i}. {trend.topic}")
        print(f"   Score: {trend.score:.2f} | Velocity: {trend.velocity}")
        print(f"   Volume: {trend.volume} | Engagement: {trend.engagement_rate}")
