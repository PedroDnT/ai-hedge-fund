from typing import Annotated, Any, Dict, Sequence, TypedDict, List
import operator
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai.chat_models import ChatOpenAI
from langgraph.graph import END, StateGraph
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.tools.new_tools import (
    get_quotes,
    get_financial_ratios,
    get_market_ratios,
    get_income_statements,
    get_balance_sheet,
    list_cia,
    match_company_data
)

from src.schemas.market_data_schema import (
    Quote,
    FinancialRatios,
    MarketRatios,
    BalanceSheet,
    IncomeStatement,
    CompanyInfo
)

llm = ChatOpenAI(model="gpt-4")

def merge_dicts(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    return {**a, **b}

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    data: Annotated[Dict[str, Any], merge_dicts]
    metadata: Annotated[Dict[str, Any], merge_dicts]

def calculate_rsi(prices_df: pd.DataFrame, periods: int = 14) -> pd.Series:
    """Calculate Relative Strength Index"""
    delta = prices_df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_macd(prices_df: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """Calculate MACD and Signal Line"""
    exp1 = prices_df['close'].ewm(span=12, adjust=False).mean()
    exp2 = prices_df['close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal

def calculate_bollinger_bands(prices_df: pd.DataFrame, window: int = 20) -> tuple[pd.Series, pd.Series]:
    """Calculate Bollinger Bands"""
    sma = prices_df['close'].rolling(window=window).mean()
    std = prices_df['close'].rolling(window=window).std()
    upper_band = sma + (std * 2)
    lower_band = sma - (std * 2)
    return upper_band, lower_band

def calculate_obv(prices_df: pd.DataFrame) -> pd.Series:
    """Calculate On-Balance Volume"""
    obv = pd.Series(0, index=prices_df.index)
    for i in range(1, len(prices_df)):
        if prices_df['close'].iloc[i] > prices_df['close'].iloc[i-1]:
            obv.iloc[i] = obv.iloc[i-1] + prices_df['volume'].iloc[i]
        elif prices_df['close'].iloc[i] < prices_df['close'].iloc[i-1]:
            obv.iloc[i] = obv.iloc[i-1] - prices_df['volume'].iloc[i]
        else:
            obv.iloc[i] = obv.iloc[i-1]
    return obv

##### Market Data Agent #####
def market_data_agent(state: AgentState):
    """Responsible for gathering and preprocessing market data"""
    messages = state["messages"]
    data = state["data"]
    ticker = data["ticker"]

    try:
        # Get company info
        company_data = match_company_data()
        company = company_data[company_data['ticker'] == ticker].iloc[0]
        cvm_code = company['cvm_code']
        
        # Get market data
        quotes_df = get_quotes(
            ticker=ticker,
            period_init=data.get("start_date"),
            period_end=data.get("end_date")
        )
        
        # Get financial data
        financials = {
            "ratios": get_financial_ratios(cvm_code),
            "market_ratios": get_market_ratios(cvm_code),
            "income": get_income_statements(cvm_code),
            "balance": get_balance_sheet(cvm_code)
        }
        
        return {
            "messages": messages,
            "data": {
                **data,
                "quotes": quotes_df,
                "company": company,
                "financials": financials
            }
        }
    except Exception as e:
        raise Exception(f"Failed to fetch market data: {str(e)}")

##### Quantitative Agent #####
def quant_agent(state: AgentState):
    """Analyzes technical indicators and generates trading signals."""
    show_reasoning = state["metadata"]["show_reasoning"]
    data = state["data"]
    prices_df = data["quotes"]
    
    # Calculate indicators
    macd_line, signal_line = calculate_macd(prices_df)
    rsi = calculate_rsi(prices_df)
    upper_band, lower_band = calculate_bollinger_bands(prices_df)
    obv = calculate_obv(prices_df)
    
    # Generate signals
    signals = []
    
    # MACD signal
    if macd_line.iloc[-2] < signal_line.iloc[-2] and macd_line.iloc[-1] > signal_line.iloc[-1]:
        signals.append('bullish')
    elif macd_line.iloc[-2] > signal_line.iloc[-2] and macd_line.iloc[-1] < signal_line.iloc[-1]:
        signals.append('bearish')
    else:
        signals.append('neutral')
    
    # RSI signal
    if rsi.iloc[-1] < 30:
        signals.append('bullish')
    elif rsi.iloc[-1] > 70:
        signals.append('bearish')
    else:
        signals.append('neutral')
    
    # Bollinger Bands signal
    current_price = prices_df['close'].iloc[-1]
    if current_price < lower_band.iloc[-1]:
        signals.append('bullish')
    elif current_price > upper_band.iloc[-1]:
        signals.append('bearish')
    else:
        signals.append('neutral')
    
    # OBV signal
    obv_slope = obv.diff().iloc[-5:].mean()
    if obv_slope > 0:
        signals.append('bullish')
    elif obv_slope < 0:
        signals.append('bearish')
    else:
        signals.append('neutral')
    
    # Add reasoning
    reasoning = {
        "MACD": {
            "signal": signals[0],
            "details": f"MACD Line crossed {'above' if signals[0] == 'bullish' else 'below' if signals[0] == 'bearish' else 'neither above nor below'} Signal Line"
        },
        "RSI": {
            "signal": signals[1],
            "details": f"RSI is {rsi.iloc[-1]:.2f} ({'oversold' if signals[1] == 'bullish' else 'overbought' if signals[1] == 'bearish' else 'neutral'})"
        },
        "Bollinger": {
            "signal": signals[2],
            "details": f"Price is {'below lower band' if signals[2] == 'bullish' else 'above upper band' if signals[2] == 'bearish' else 'within bands'}"
        },
        "OBV": {
            "signal": signals[3],
            "details": f"OBV slope is {obv_slope:.2f} ({signals[3]})"
        }
    }
    
    # Overall signal
    bullish_count = signals.count('bullish')
    bearish_count = signals.count('bearish')
    
    if bullish_count > bearish_count:
        overall_signal = 'bullish'
    elif bearish_count > bullish_count:
        overall_signal = 'bearish'
    else:
        overall_signal = 'neutral'
    
    # Confidence level
    confidence = max(bullish_count, bearish_count) / len(signals)
    
    message_content = {
        "signal": overall_signal,
        "confidence": round(confidence, 2),
        "reasoning": reasoning
    }

    message = HumanMessage(
        content=str(message_content),
        name="quant_agent",
    )
    
    return {
        "messages": [message],
        "data": data,
    }

##### Fundamental Agent #####
def fundamentals_agent(state: AgentState):
    """Analyzes fundamental data and generates trading signals."""
    show_reasoning = state["metadata"]["show_reasoning"]
    data = state["data"]
    financials = data["financials"]
    
    # Get latest data
    ratios = financials["ratios"][0] if isinstance(financials["ratios"], list) else financials["ratios"]
    market = financials["market_ratios"][0] if isinstance(financials["market_ratios"], list) else financials["market_ratios"]
    income = financials["income"][0] if isinstance(financials["income"], list) else financials["income"]
    balance = financials["balance"][0] if isinstance(financials["balance"], list) else financials["balance"]
    
    # Initialize signals
    signals = []
    reasoning = {}
    
    # 1. Profitability Analysis
    profitability_score = 0
    if ratios.roe and ratios.roe > 0.15:  # Strong ROE
        profitability_score += 1
    if income.net_margin > 0.20:  # Good margins
        profitability_score += 1
    if income.operating_margin > 0.15:  # Good operating efficiency
        profitability_score += 1
        
    signals.append('bullish' if profitability_score >= 2 else 'bearish' if profitability_score == 0 else 'neutral')
    reasoning["Profitability"] = {
        "signal": signals[0],
        "details": f"ROE: {ratios.roe*100:.1f}%, Net Margin: {income.net_margin*100:.1f}%, Op Margin: {income.operating_margin*100:.1f}%"
    }
    
    # 2. Valuation Analysis
    valuation_score = 0
    if market.p_e and market.p_e < 15:  # Attractive P/E
        valuation_score += 1
    if market.p_b and market.p_b < 2:  # Attractive P/B
        valuation_score += 1
    if market.dividend_yield and market.dividend_yield > 0.03:  # Good dividend yield
        valuation_score += 1
        
    signals.append('bullish' if valuation_score >= 2 else 'bearish' if valuation_score == 0 else 'neutral')
    reasoning["Valuation"] = {
        "signal": signals[1],
        "details": f"P/E: {market.p_e:.1f}, P/B: {market.p_b:.1f}, Div Yield: {market.dividend_yield*100:.1f}%"
    }
    
    # 3. Financial Health
    health_score = 0
    current_ratio = balance.total_assets / balance.total_liabilities if balance.total_liabilities != 0 else float('inf')
    if current_ratio > 1.5:  # Good liquidity
        health_score += 1
    if balance.total_liabilities / balance.total_equity < 1.0:  # Conservative leverage
        health_score += 1
        
    signals.append('bullish' if health_score >= 1 else 'bearish' if health_score == 0 else 'neutral')
    reasoning["Financial_Health"] = {
        "signal": signals[2],
        "details": f"Current Ratio: {current_ratio:.2f}, D/E: {balance.total_liabilities/balance.total_equity:.2f}"
    }
    
    # Overall signal
    bullish_count = signals.count('bullish')
    bearish_count = signals.count('bearish')
    
    if bullish_count > bearish_count:
        overall_signal = 'bullish'
    elif bearish_count > bullish_count:
        overall_signal = 'bearish'
    else:
        overall_signal = 'neutral'
    
    # Confidence level
    confidence = max(bullish_count, bearish_count) / len(signals)
    
    message_content = {
        "signal": overall_signal,
        "confidence": round(confidence, 2),
        "reasoning": reasoning
    }

    message = HumanMessage(
        content=str(message_content),
        name="fundamentals_agent",
    )
    
    return {
        "messages": [message],
        "data": data,
    }
