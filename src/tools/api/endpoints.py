from typing import Optional
from datetime import datetime
from ...schemas.market_data import PriceResponse, FinancialMetric, NewsArticle
from .client import client

def get_prices(
    ticker: str,
    start_date: datetime,
    end_date: datetime,
    interval: str = "day"
) -> PriceResponse:
    """Fetch price data from the API"""
    params = {
        "ticker": ticker,
        "interval": interval,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d")
    }
    
    response = client.get("prices", params=params)
    return PriceResponse(**response)

def get_financial_metrics(
    ticker: str,
    report_period: datetime,
    period: str = "ttm",
    limit: int = 1
) -> list[FinancialMetric]:
    """Fetch financial metrics from the API"""
    params = {
        "ticker": ticker,
        "report_period_lte": report_period.strftime("%Y-%m-%d"),
        "period": period,
        "limit": limit
    }
    
    response = client.get("financial-metrics", params=params)
    return [FinancialMetric(**metric) for metric in response["financial_metrics"]] 