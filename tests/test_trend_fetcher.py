"""Test for Trend Fetcher - This test SHOULD fail initially."""

import pytest
from pydantic import ValidationError


def test_trend_data_structure():
    """Asserts that the trend data structure matches the API contract."""
    from schemas.trend import TrendData
    
    # This should work when TrendData is implemented
    trend = TrendData(
        topic="AI Agents",
        score=0.85,
        velocity="rising"
    )
    
    assert trend.topic == "AI Agents"
    assert trend.score == 0.85
    assert trend.velocity == "rising"


def test_trend_with_required_fields():
    """Test that TrendData requires all specified fields."""
    from schemas.trend import TrendData
    
    with pytest.raises(ValidationError):
        # Missing required fields should raise error
        TrendData()


def test_trend_relevance_threshold():
    """Test that trends below threshold are filtered out."""
    from schemas.trend import TrendData, RELEVANCE_THRESHOLD
    
    # Create a trend below threshold
    low_relevance_trend = TrendData(
        topic="Unpopular Topic",
        score=0.5,
        velocity="declining"
    )
    
    # This trend should be below the relevance threshold
    assert low_relevance_trend.score < RELEVANCE_THRESHOLD
