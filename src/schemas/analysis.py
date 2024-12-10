from pydantic import BaseModel, Field
from typing import Dict, List, Literal, Optional
from datetime import datetime

class TechnicalSignal(BaseModel):
    indicator: str
    signal: Literal["bullish", "bearish", "neutral"]
    confidence: float = Field(..., ge=0, le=1)
    details: str

class TechnicalAnalysis(BaseModel):
    signals: List[TechnicalSignal]
    overall_signal: Literal["bullish", "bearish", "neutral"]
    overall_confidence: float = Field(..., ge=0, le=1)
    timestamp: datetime

class FundamentalAnalysis(BaseModel):
    profitability_score: float = Field(..., ge=0, le=1)
    growth_score: float = Field(..., ge=0, le=1)
    health_score: float = Field(..., ge=0, le=1)
    valuation_score: float = Field(..., ge=0, le=1)
    overall_score: float = Field(..., ge=0, le=1)
    signal: Literal["bullish", "bearish", "neutral"]
    reasoning: Dict[str, str]

class SentimentAnalysis(BaseModel):
    sentiment_score: float = Field(..., ge=-1, le=1)
    confidence: float = Field(..., ge=0, le=1)
    source_count: int
    key_topics: List[str]
    signal: Literal["bullish", "bearish", "neutral"]