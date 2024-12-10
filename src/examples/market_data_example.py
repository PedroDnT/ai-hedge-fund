from src.data_providers.market_data_provider import MarketDataProvider
from src.schemas.market_data_schema import MarketDataError, InvalidTickerError
from datetime import datetime, timedelta

def main():
    # Initialize provider with 1-hour cache timeout
    provider = MarketDataProvider(cache_timeout=3600)
    
    try:
        # List companies
        print("\nListing first 5 companies:")
        for company in provider.companies[:5]:
            print(f"- {company.trade_name} (CVM: {company.cvm_code})")
        
        # Get historical quotes and calculate returns
        ticker = "PETR4"
        print(f"\nAnalyzing {ticker}:")
        
        # Get company info
        company = provider.get_company_by_ticker(ticker)
        print(f"Company: {company.name}")
        
        # Get latest quote
        quote = provider.get_latest_quote(ticker)
        print(f"Latest price: R${quote.close:.2f}")
        
        # Calculate returns
        returns, vol = provider.get_price_returns(ticker, lookback_days=252)
        print(f"1Y Return: {returns*100:.1f}%")
        print(f"Volatility: {vol*100:.1f}%")
        
        # Get financials
        print(f"\nFinancials for {company.name}:")
        financials = provider.get_company_financials(company.cvm_code)
        
        income = financials["income_statement"]
        print(f"Revenue: R${income.revenue:,.0f}")
        print(f"Net Income: R${income.net_income:,.0f}")
        print(f"Net Margin: {income.net_margin*100:.1f}%")
        
        ratios = financials["financial_ratios"]
        print(f"ROE: {ratios.roe*100:.1f}% (if available)")
        
        # Test error handling with invalid ticker
        print("\nTesting invalid ticker:")
        try:
            provider.get_latest_quote("INVALID")
        except InvalidTickerError as e:
            print(f"Caught expected error: {e}")
            
    except MarketDataError as e:
        print(f"Error accessing market data: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()