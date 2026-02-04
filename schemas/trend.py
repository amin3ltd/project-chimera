"""
Trend Schemas - Data models for trend analysis.
"""

from pydantic import BaseModel, Field


# Relevance threshold constant
RELEVANCE_THRESHOLD = 0.75


class TrendData(BaseModel):
    """Individual trend data point matching API contract."""
    
    topic: str = Field(..., description="The trending topic or keyword")
    score: float = Field(..., ge=0.0, le=1.0, description="Relevance score (0.0-1.0)")
    velocity: str = Field(..., pattern="^(rising|stable|declining)$", 
                         description="Trend velocity indicator")


class TrendAnalysisRequest(BaseModel):
    """Request model for trend analysis."""
    
    content: str = Field(..., description="Content to analyze for trends")
    platform: str = Field(..., description="Source platform: twitter | instagram | tiktok")
    max_results: int = Field(default=10, ge=1, le=100, description="Max trends to return")
    min_relevance_score: float = Field(default=0.75, ge=0.0, le=1.0)


class TrendAnalysisResponse(BaseModel):
    """Response model for trend analysis."""
    
    status: str = Field(..., pattern="^(success|error)$")
    trends: list[TrendData] = Field(default_factory=list)
    error_message: str | None = None
    analysis_metadata: dict = Field(default_factory=dict)
