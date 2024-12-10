from pydantic import BaseModel, Field
from typing import Dict, List, Literal, Optional
from datetime import datetime

class Position(BaseModel):
    ticker: str
    quantity: int = Field(..., ge=0)
    average_cost: float = Field(..., ge=0)
    current_price: float = Field(..., ge=0)
    market_value: float = Field(..., ge=0)
    unrealized_pl: float
    weight: float = Field(..., ge=0, le=1)

class Portfolio(BaseModel):
    cash: float = Field(..., ge=0)
    positions: Dict[str, Position] = {}
    total_value: float = Field(..., ge=0)
    last_updated: datetime

class TradeDecision(BaseModel):
    action: Literal["buy", "sell", "hold"]
    ticker: str
    quantity: int = Field(..., ge=0)
    price_limit: Optional[float] = Field(None, ge=0)
    confidence: float = Field(..., ge=0, le=1)
    reasoning: str
    timestamp: datetime 