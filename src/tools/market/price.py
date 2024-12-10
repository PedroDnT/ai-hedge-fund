from typing import Optional
import pandas as pd
from datetime import datetime, timedelta
from ...schemas.market_data import PriceResponse
from ..api.endpoints import get_prices

class PriceAnalyzer:
    def __init__(self, ticker: str):
        self.ticker = ticker
        self._cache = {}
        
    def get_price_history(
        self,
        start_date: datetime,
        end_date: Optional[datetime] = None,
        interval: str = "day"
    ) -> pd.DataFrame:
        """Get price history with caching"""
        end_date = end_date or datetime.now()
        cache_key = (self.ticker, start_date, end_date, interval)
        
        if cache_key not in self._cache:
            response = get_prices(
                ticker=self.ticker,
                start_date=start_date,
                end_date=end_date,
                interval=interval
            )
            self._cache[cache_key] = self._process_price_data(response)
            
        return self._cache[cache_key]
    
    def _process_price_data(self, response: PriceResponse) -> pd.DataFrame:
        """Convert API response to DataFrame"""
        df = pd.DataFrame([p.dict() for p in response.prices])
        df['time'] = pd.to_datetime(df['time'])
        df.set_index('time', inplace=True)
        return df
    
    def calculate_returns(self, df: pd.DataFrame) -> pd.Series:
        """Calculate daily returns"""
        return df['close'].pct_change()
    
    def calculate_volatility(self, df: pd.DataFrame, window: int = 20) -> pd.Series:
        """Calculate rolling volatility"""
        returns = self.calculate_returns(df)
        return returns.rolling(window=window).std() * (252 ** 0.5)  # Annualized 