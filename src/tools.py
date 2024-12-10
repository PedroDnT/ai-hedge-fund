import os

import pandas as pd
import requests
from typing import Dict, Union
from tavily import TavilyClient
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, TypedDict

import requests

# Define response schemas
class PriceData(TypedDict):
    time: str
    open: float
    high: float
    low: float
    close: float
    volume: int

class PriceResponse(TypedDict):
    prices: List[PriceData]
    ticker: str
    interval: str

class FinancialMetric(TypedDict):
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

@dataclass
class NewsArticle:
    title: str
    url: str
    published_date: datetime
    content: str
    source: str

def get_prices(ticker: str, start_date: str, end_date: str) -> PriceResponse:
    """Fetch price data from the API.
    
    Args:
        ticker: Stock ticker symbol
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        PriceResponse containing list of PriceData
        
    Raises:
        ValueError: If no price data is returned
        RequestException: If API request fails
    """
    headers = {"X-API-KEY": os.environ.get("FINANCIAL_DATASETS_API_KEY")}
    url = (
        f"https://api.financialdatasets.ai/prices/"
        f"?ticker={ticker}"
        f"&interval=day"
        f"&interval_multiplier=1"
        f"&start_date={start_date}"
        f"&end_date={end_date}"
    )
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    if not data.get("prices"):
        raise ValueError("No price data returned")
        
    return PriceResponse(
        prices=[PriceData(**price) for price in data["prices"]],
        ticker=data["ticker"],
        interval=data["interval"]
    )

def prices_to_df(prices):
    """Convert prices to a DataFrame."""
    df = pd.DataFrame(prices)
    df["Date"] = pd.to_datetime(df["time"])
    df.set_index("Date", inplace=True)
    numeric_cols = ["open", "close", "high", "low", "volume"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df.sort_index(inplace=True)
    return df

# Update the get_price_data function to use the new functions
def get_price_data(ticker, start_date, end_date):
    prices = get_prices(ticker, start_date, end_date)
    return prices_to_df(prices)

def get_financial_metrics(ticker, report_period, period='ttm', limit=1):
    """Fetch financial metrics from the API."""
    headers = {"X-API-KEY": os.environ.get("FINANCIAL_DATASETS_API_KEY")}
    url = (
        f"https://api.financialdatasets.ai/financial-metrics/"
        f"?ticker={ticker}"
        f"&report_period_lte={report_period}"
        f"&limit={limit}"
        f"&period={period}"
    )
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(
            f"Error fetching data: {response.status_code} - {response.text}"
        )
    data = response.json()
    financial_metrics = data.get("financial_metrics")
    if not financial_metrics:
        raise ValueError("No financial metrics returned")
    return financial_metrics

def get_news(
    query: str,
    end_date: str,
    max_results: int = 5,
) -> Union[Dict, str]:
    """
    Perform a web search using the Tavily API.

    This tool accesses real-time web data, news, articles and should be used when up-to-date information from the internet is required.
    """
    client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))
    response = client.search(query, topic="news", max_results=max_results)
    
    # Convert end_date string to datetime object
    end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Filter results
    if 'results' in response:
        filtered_results = []
        for result in response['results']:
            if 'published_date' in result:
                # Parse the published_date
                pub_date = datetime.strptime(result['published_date'], '%a, %d %b %Y %H:%M:%S %Z')
                if pub_date.date() <= end_date_dt.date():
                    filtered_results.append(result)
        
        response['results'] = filtered_results
    
    return response

def calculate_confidence_level(signals):
    """Calculate confidence level based on the difference between SMAs."""
    sma_diff_prev = abs(signals['sma_5_prev'] - signals['sma_20_prev'])
    sma_diff_curr = abs(signals['sma_5_curr'] - signals['sma_20_curr'])
    diff_change = sma_diff_curr - sma_diff_prev
    # Normalize confidence between 0 and 1
    confidence = min(max(diff_change / signals['current_price'], 0), 1)
    return confidence

def calculate_macd(prices_df: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """Calculate MACD (Moving Average Convergence Divergence).
    
    Args:
        prices_df: DataFrame with 'close' price column
        
    Returns:
        tuple containing:
        - macd_line: 12-day EMA - 26-day EMA
        - signal_line: 9-day EMA of MACD line
    """
    ema_12 = prices_df['close'].ewm(span=12, adjust=False).mean()
    ema_26 = prices_df['close'].ewm(span=26, adjust=False).mean()
    macd_line = ema_12 - ema_26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    return macd_line, signal_line

def calculate_rsi(prices_df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Calculate RSI (Relative Strength Index).
    
    Args:
        prices_df: DataFrame with 'close' price column
        period: Number of periods for calculation (default: 14)
        
    Returns:
        Series containing RSI values (0-100)
        - RSI > 70: Overbought
        - RSI < 30: Oversold
    """
    delta = prices_df['close'].diff()
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_bollinger_bands(
    prices_df: pd.DataFrame, 
    window: int = 20
) -> tuple[pd.Series, pd.Series]:
    """Calculate Bollinger Bands.
    
    Args:
        prices_df: DataFrame with 'close' price column
        window: Window size for moving average (default: 20)
        
    Returns:
        tuple containing:
        - upper_band: SMA + (2 * std_dev)
        - lower_band: SMA - (2 * std_dev)
    """
    sma = prices_df['close'].rolling(window).mean()
    std_dev = prices_df['close'].rolling(window).std()
    upper_band = sma + (std_dev * 2)
    lower_band = sma - (std_dev * 2)
    return upper_band, lower_band

def calculate_obv(prices_df: pd.DataFrame) -> pd.Series:
    """Calculate OBV (On-Balance Volume).
    
    Args:
        prices_df: DataFrame with 'close' and 'volume' columns
        
    Returns:
        Series containing cumulative OBV values
        - Rising OBV suggests positive volume pressure
        - Falling OBV suggests negative volume pressure
    """
    obv = [0]
    for i in range(1, len(prices_df)):
        if prices_df['close'].iloc[i] > prices_df['close'].iloc[i - 1]:
            obv.append(obv[-1] + prices_df['volume'].iloc[i])
        elif prices_df['close'].iloc[i] < prices_df['close'].iloc[i - 1]:
            obv.append(obv[-1] - prices_df['volume'].iloc[i])
        else:
            obv.append(obv[-1])
    prices_df['OBV'] = obv
    return prices_df['OBV']