from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime

class MarketDataError(Exception):
    """Base exception for market data errors"""
    pass

class InvalidTickerError(MarketDataError):
    """Raised when ticker is not found"""
    pass

class InvalidCVMCodeError(MarketDataError):
    """Raised when CVM code is not found"""
    pass

class Quote(BaseModel):
    date: datetime
    open: float = Field(ge=0)
    close: float = Field(ge=0)
    adj_close: float = Field(ge=0)
    min: float = Field(ge=0)
    max: float = Field(ge=0)
    volume: int = Field(ge=0)

    @validator('date', pre=True)
    def parse_date(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v

class CompanyInfo(BaseModel):
    name: str
    trade_name: str
    cvm_code: str
    is_b3_listed: bool = True
    ticker: Optional[str] = None
    sector: Optional[str] = None
    subsector: Optional[str] = None
    segment: Optional[str] = None

class FinancialMetric(BaseModel):
    value: Optional[float] = None
    currency: Optional[str] = None
    unit: Optional[str] = None

class FinancialRatios(BaseModel):
    period: str
    statement_type: str
    period_type: str
    ebit: Union[float, FinancialMetric, None] = None
    ebitda: Union[float, FinancialMetric, None] = None
    net_income: Union[float, FinancialMetric, None] = None
    gross_margin: Optional[float] = Field(None, le=1.0, ge=-1.0)
    ebit_margin: Optional[float] = Field(None, le=1.0, ge=-1.0)
    net_margin: Optional[float] = Field(None, le=1.0, ge=-1.0)
    roe: Optional[float] = None
    roa: Optional[float] = None
    
    @validator('*', pre=True)
    def convert_financial_metric(cls, v):
        if isinstance(v, dict) and 'value' in v:
            return v['value']
        return v

class MarketRatios(BaseModel):
    date: datetime
    market_cap: Union[float, FinancialMetric, None] = Field(None, ge=0)
    enterprise_value: Union[float, FinancialMetric, None] = Field(None, ge=0)
    ev_ebit: Optional[float] = None
    ev_ebitda: Optional[float] = None
    p_e: Optional[float] = None
    p_b: Optional[float] = None
    dividend_yield: Optional[float] = Field(None, ge=0)
    
    @validator('date', pre=True)
    def parse_date(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v
    
    @validator('*', pre=True)
    def convert_financial_metric(cls, v, field):
        if field.name in ['market_cap', 'enterprise_value'] and isinstance(v, dict):
            return v.get('value')
        return v

class BalanceSheet(BaseModel):
    period: str
    statement_type: str
    assets: Dict[str, Union[float, FinancialMetric]]
    liabilities: Dict[str, Union[float, FinancialMetric]]
    equity: Dict[str, Union[float, FinancialMetric]]

    @validator('assets', 'liabilities', 'equity', pre=True)
    def convert_metrics(cls, v):
        return {k: v['value'] if isinstance(v, dict) and 'value' in v else v 
                for k, v in v.items()}

    @property
    def total_assets(self) -> float:
        return sum(float(v) for v in self.assets.values())

    @property
    def total_liabilities(self) -> float:
        return sum(float(v) for v in self.liabilities.values())

    @property
    def total_equity(self) -> float:
        return sum(float(v) for v in self.equity.values())

class IncomeStatement(BaseModel):
    period: str
    statement_type: str
    period_type: str
    revenue: Union[float, FinancialMetric] = Field(ge=0)
    gross_profit: Union[float, FinancialMetric]
    operating_income: Union[float, FinancialMetric]
    net_income: Union[float, FinancialMetric]
    ebit: Union[float, FinancialMetric]
    ebitda: Union[float, FinancialMetric]

    @validator('*', pre=True)
    def convert_financial_metric(cls, v):
        if isinstance(v, dict) and 'value' in v:
            return v['value']
        return v

    @property
    def gross_margin(self) -> float:
        revenue = float(self.revenue)
        return float(self.gross_profit) / revenue if revenue != 0 else 0

    @property
    def operating_margin(self) -> float:
        revenue = float(self.revenue)
        return float(self.operating_income) / revenue if revenue != 0 else 0

    @property
    def net_margin(self) -> float:
        revenue = float(self.revenue)
        return float(self.net_income) / revenue if revenue != 0 else 0
 