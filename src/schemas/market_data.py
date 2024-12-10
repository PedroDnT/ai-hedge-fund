from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class PriceData(BaseModel):
    time: datetime
    open: float = Field(..., description="Opening price")
    high: float = Field(..., description="Highest price")
    low: float = Field(..., description="Lowest price") 
    close: float = Field(..., description="Closing price")
    volume: int = Field(..., description="Trading volume")

class PriceResponse(BaseModel):
    prices: List[PriceData]
    ticker: str
    interval: str

class FinancialMetric(BaseModel):
    report_period: str
    ticker: str
    return_on_equity: float
    net_margin: float
    operating_margin: float
    revenue_growth: float
    earnings_growth: float
    book_value_growth: float
    current_ratio: float
    debt_to_equity: float
    free_cash_flow_per_share: float
    earnings_per_share: float
    price_to_earnings_ratio: float
    price_to_book_ratio: float
    price_to_sales_ratio: float

class NewsArticle(BaseModel):
    title: str
    url: str
    published_date: datetime
    content: str
    source: str 