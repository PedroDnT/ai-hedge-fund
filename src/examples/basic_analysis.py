from datetime import datetime, timedelta
from src.tools.market.price import PriceAnalyzer
from src.tools.market.indicators import calculate_technical_indicators
from src.tools.api.endpoints import get_financial_metrics

def run_basic_analysis(ticker: str):
    """Example of basic market analysis workflow"""
    
    # Initialize price analyzer
    analyzer = PriceAnalyzer(ticker)
    
    # Get last 3 months of price data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    price_df = analyzer.get_price_history(start_date, end_date)
    
    # Calculate technical analysis
    tech_analysis = calculate_technical_indicators(price_df)
    
    # Get fundamental metrics
    fundamentals = get_financial_metrics(ticker, end_date)
    
    # Calculate key metrics
    returns = analyzer.calculate_returns(price_df)
    volatility = analyzer.calculate_volatility(price_df)
    
    print(f"\n=== Analysis for {ticker} ===")
    print("\nTechnical Analysis:")
    print(f"Overall Signal: {tech_analysis.overall_signal}")
    print(f"Confidence: {tech_analysis.overall_confidence:.2%}")
    
    print("\nIndividual Signals:")
    for signal in tech_analysis.signals:
        print(f"- {signal.indicator}: {signal.signal} (confidence: {signal.confidence:.2%})")
        print(f"  Details: {signal.details}")
    
    print("\nPerformance Metrics:")
    print(f"Total Return: {returns.sum():.2%}")
    print(f"Volatility (annualized): {volatility.iloc[-1]:.2%}")
    
    print("\nFundamental Metrics:")
    for metric in fundamentals:
        print(f"ROE: {metric.return_on_equity:.2%}")
        print(f"Net Margin: {metric.net_margin:.2%}")
        print(f"P/E Ratio: {metric.price_to_earnings_ratio:.2f}")

if __name__ == "__main__":
    run_basic_analysis("AAPL") 