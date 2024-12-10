from src.data_providers.market_data_provider import MarketDataProvider
from src.schemas.market_data_schema import (
    MarketDataError,
    InvalidTickerError,
    Quote,
    CompanyInfo,
    FinancialRatios
)
from datetime import datetime, timedelta
import pandas as pd

def test_provider():
    """Test all market data provider functionality"""
    
    # Initialize provider
    provider = MarketDataProvider(cache_timeout=3600)
    print("\n1. Testing Market Data Provider")
    print("=" * 50)
    
    # Test company listing
    print("\nTesting company listing...")
    companies = provider.companies
    print(f"✓ Found {len(companies)} companies")
    print(f"Sample company: {companies[0].name} ({companies[0].cvm_code})")
    
    # Test quote retrieval
    print("\nTesting quote retrieval for PETR4...")
    try:
        quotes = provider.get_historical_quotes("PETR4")
        print(f"✓ Retrieved {len(quotes)} quotes")
        latest = quotes[-1]
        print(f"Latest quote: R${latest.close:.2f} on {latest.date.date()}")
        
        # Test invalid ticker
        try:
            provider.get_historical_quotes("INVALID")
            print("✗ Failed to catch invalid ticker")
        except InvalidTickerError:
            print("✓ Successfully caught invalid ticker")
    except Exception as e:
        print(f"✗ Quote retrieval failed: {str(e)}")
    
    # Test financial data
    print("\nTesting financial data retrieval...")
    try:
        cvm_code = companies[0].cvm_code
        financials = provider.get_company_financials(cvm_code)
        
        print("\nBalance Sheet:")
        balance = financials["balance_sheet"]
        print(f"✓ Total Assets: R${balance.total_assets:,.2f}")
        print(f"✓ Total Liabilities: R${balance.total_liabilities:,.2f}")
        print(f"✓ Total Equity: R${balance.total_equity:,.2f}")
        
        print("\nIncome Statement:")
        income = financials["income_statement"]
        print(f"✓ Revenue: R${float(income.revenue):,.2f}")
        print(f"✓ Net Income: R${float(income.net_income):,.2f}")
        print(f"✓ Net Margin: {income.net_margin*100:.1f}%")
        
        print("\nRatios:")
        ratios = financials["financial_ratios"]
        if ratios.roe is not None:
            print(f"✓ ROE: {ratios.roe*100:.1f}%")
        if ratios.roa is not None:
            print(f"✓ ROA: {ratios.roa*100:.1f}%")
    except Exception as e:
        print(f"✗ Financial data retrieval failed: {str(e)}")
    
    # Test returns calculation
    print("\nTesting returns calculation...")
    try:
        returns, vol = provider.get_price_returns("PETR4", lookback_days=252)
        print(f"✓ 1Y Return: {returns*100:.1f}%")
        print(f"✓ Volatility: {vol*100:.1f}%")
    except Exception as e:
        print(f"✗ Returns calculation failed: {str(e)}")
    
    # Test caching
    print("\nTesting cache functionality...")
    try:
        # First call
        t1 = datetime.now()
        _ = provider.get_historical_quotes("PETR4")
        t2 = datetime.now()
        first_call = (t2 - t1).total_seconds()
        
        # Second call (should be cached)
        t1 = datetime.now()
        _ = provider.get_historical_quotes("PETR4")
        t2 = datetime.now()
        second_call = (t2 - t1).total_seconds()
        
        print(f"✓ First call: {first_call:.3f}s")
        print(f"✓ Second call: {second_call:.3f}s")
        print(f"✓ Cache speedup: {first_call/second_call:.1f}x")
    except Exception as e:
        print(f"✗ Cache testing failed: {str(e)}")

if __name__ == "__main__":
    test_provider() 