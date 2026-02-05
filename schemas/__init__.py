"""
Schemas package.

Having `schemas` as a real Python package avoids mypy treating `schemas/trend.py`
as both a top-level module (`trend`) and a package module (`schemas.trend`).
"""

from __future__ import annotations

__all__ = ["Trend"]

from .trend import TrendAnalysisRequest, TrendAnalysisResponse, TrendData

__all__ = ["TrendData", "TrendAnalysisRequest", "TrendAnalysisResponse"]

