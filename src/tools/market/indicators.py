from typing import Tuple
import pandas as pd
import numpy as np
from ...schemas.analysis import TechnicalSignal, TechnicalAnalysis

def calculate_technical_indicators(prices_df: pd.DataFrame) -> TechnicalAnalysis:
    """Calculate all technical indicators and return analysis"""
    signals = []
    
    # MACD
    macd_signal = calculate_macd_signal(prices_df)
    signals.append(macd_signal)
    
    # RSI
    rsi_signal = calculate_rsi_signal(prices_df)
    signals.append(rsi_signal)
    
    # Bollinger Bands
    bb_signal = calculate_bb_signal(prices_df)
    signals.append(bb_signal)
    
    # OBV
    obv_signal = calculate_obv_signal(prices_df)
    signals.append(obv_signal)
    
    # Calculate overall signal
    bullish_count = sum(1 for s in signals if s.signal == "bullish")
    bearish_count = sum(1 for s in signals if s.signal == "bearish")
    
    if bullish_count > bearish_count:
        overall_signal = "bullish"
    elif bearish_count > bullish_count:
        overall_signal = "bearish"
    else:
        overall_signal = "neutral"
        
    overall_confidence = max(bullish_count, bearish_count) / len(signals)
    
    return TechnicalAnalysis(
        signals=signals,
        overall_signal=overall_signal,
        overall_confidence=overall_confidence,
        timestamp=pd.Timestamp.now()
    )

def calculate_macd_signal(prices_df: pd.DataFrame) -> TechnicalSignal:
    """Calculate MACD signal"""
    ema_12 = prices_df['close'].ewm(span=12, adjust=False).mean()
    ema_26 = prices_df['close'].ewm(span=26, adjust=False).mean()
    macd_line = ema_12 - ema_26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    
    # Determine signal
    if macd_line.iloc[-1] > signal_line.iloc[-1] and macd_line.iloc[-2] <= signal_line.iloc[-2]:
        signal = "bullish"
    elif macd_line.iloc[-1] < signal_line.iloc[-1] and macd_line.iloc[-2] >= signal_line.iloc[-2]:
        signal = "bearish"
    else:
        signal = "neutral"
        
    # Calculate confidence based on distance between lines
    confidence = min(abs(macd_line.iloc[-1] - signal_line.iloc[-1]) / prices_df['close'].iloc[-1], 1.0)
    
    return TechnicalSignal(
        indicator="MACD",
        signal=signal,
        confidence=confidence,
        details=f"MACD Line: {macd_line.iloc[-1]:.2f}, Signal Line: {signal_line.iloc[-1]:.2f}"
    )