from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
from functools import lru_cache
from src.tools.new_tools import (
    get_quotes, 
    list_cia, 
    get_balance_sheet,
    get_income_statements,
    get_financial_ratios,
    get_market_ratios,
    match_company_data
)
from src.schemas.market_data_schema import (
    Quote,
    CompanyInfo,
    FinancialRatios,
    MarketRatios,
    BalanceSheet,
    IncomeStatement,
    MarketDataError,
    InvalidTickerError,
    InvalidCVMCodeError
)
from src.utils import get_default_period_init, get_default_period_end

class MarketDataProvider:
    """Provider for Brazilian market data using DadosDeMercado API"""
    
    def __init__(self, cache_timeout: int = 3600):
        self._companies = None
        self._company_data = None
        self._cache_timeout = cache_timeout
        self._last_cache_update = None
    
    def _should_refresh_cache(self) -> bool:
        """Check if cache should be refreshed"""
        if self._last_cache_update is None:
            return True
        return (datetime.now() - self._last_cache_update).total_seconds() > self._cache_timeout
    
    @property
    def companies(self) -> List[CompanyInfo]:
        """Get list of all companies with automatic cache refresh"""
        if self._companies is None or self._should_refresh_cache():
            try:
                self._companies = [CompanyInfo(**company) for company in list_cia()]
                self._last_cache_update = datetime.now()
            except Exception as e:
                raise MarketDataError(f"Failed to fetch companies: {str(e)}")
        return self._companies
    
    @property
    def company_data(self) -> pd.DataFrame:
        """Get combined company and ticker data with automatic cache refresh"""
        if self._company_data is None or self._should_refresh_cache():
            try:
                self._company_data = match_company_data()
                self._last_cache_update = datetime.now()
            except Exception as e:
                raise MarketDataError(f"Failed to match company data: {str(e)}")
        return self._company_data
    
    @lru_cache(maxsize=100)
    def get_historical_quotes(
        self, 
        ticker: str, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Quote]:
        """Get historical quotes for a ticker with caching"""
        if not start_date:
            start_date = get_default_period_init(get_default_period_end())
        if not end_date:
            end_date = get_default_period_end()
        
        try:
            quotes_df = get_quotes(
                ticker,
                period_init=start_date.strftime('%Y-%m-%d'),
                period_end=end_date.strftime('%Y-%m-%d')
            )
            return [Quote(**row.to_dict()) for _, row in quotes_df.iterrows()]
        except Exception as e:
            raise InvalidTickerError(f"Failed to get quotes for {ticker}: {str(e)}")
    
    @lru_cache(maxsize=50)
    def get_company_financials(
        self,
        cvm_code: str,
        statement_type: str = "con"
    ) -> Dict:
        """Get complete financial data for a company with caching"""
        try:
            balance = get_balance_sheet(cvm_code, statement_type)
            income = get_income_statements(cvm_code, statement_type)
            ratios = get_financial_ratios(cvm_code, statement_type)
            market = get_market_ratios(cvm_code, statement_type)
            
            return {
                "balance_sheet": BalanceSheet(**balance),
                "income_statement": IncomeStatement(**income),
                "financial_ratios": FinancialRatios(**ratios),
                "market_ratios": MarketRatios(**market)
            }
        except Exception as e:
            raise InvalidCVMCodeError(f"Failed to get financials for CVM code {cvm_code}: {str(e)}")
    
    def get_company_by_ticker(self, ticker: str) -> Optional[CompanyInfo]:
        """Get company info by ticker"""
        try:
            company_data = self.company_data
            company = company_data[company_data['ticker'] == ticker]
            if company.empty:
                raise InvalidTickerError(f"Ticker {ticker} not found")
            return CompanyInfo(**company.iloc[0].to_dict())
        except Exception as e:
            if isinstance(e, InvalidTickerError):
                raise
            raise MarketDataError(f"Failed to get company info for {ticker}: {str(e)}")
    
    def get_latest_quote(self, ticker: str) -> Quote:
        """Get latest quote for a ticker"""
        quotes = self.get_historical_quotes(ticker)
        if not quotes:
            raise InvalidTickerError(f"No quotes found for {ticker}")
        return quotes[-1]
    
    def get_price_returns(
        self,
        ticker: str,
        lookback_days: int = 252
    ) -> Tuple[float, float]:
        """Calculate price returns and volatility
        Returns:
            Tuple[float, float]: (return, volatility)
        """
        end_date = get_default_period_end()
        start_date = end_date - timedelta(days=lookback_days)
        
        quotes = self.get_historical_quotes(ticker, start_date, end_date)
        if not quotes:
            raise InvalidTickerError(f"No quotes found for {ticker}")
        
        prices = pd.Series([q.adj_close for q in quotes])
        returns = prices.pct_change().dropna()
        
        total_return = (prices.iloc[-1] / prices.iloc[0]) - 1
        volatility = returns.std() * (252 ** 0.5)  # Annualized
        
        return total_return, volatility