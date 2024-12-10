from typing import Dict, List, Optional, Union, Literal
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum

class MarketDataError(Exception):
    """Base exception for market data errors"""
    pass

class InvalidTickerError(MarketDataError):
    """Raised when ticker is not found"""
    pass

class InvalidCVMCodeError(MarketDataError):
    """Raised when CVM code is not found"""
    pass

class StatementType(str, Enum):
    CONSOLIDATED = "con"
    INDIVIDUAL = "ind"

class PeriodType(str, Enum):
    TTM = "ttm"
    QUARTER = "quarter"
    YEAR = "year"

class CompanyInfo(BaseModel):
    name: str
    trade_name: str
    cvm_code: str
    is_b3_listed: bool = True
    sector: Optional[str] = None
    subsector: Optional[str] = None
    segment: Optional[str] = None

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

class FinancialMetric(BaseModel):
    value: float
    currency: str
    unit: Optional[str] = None

class BalanceSheet(BaseModel):
    period: str
    statement_type: StatementType
    assets: Dict[str, FinancialMetric]
    liabilities: Dict[str, FinancialMetric]
    equity: Dict[str, FinancialMetric]

    @property
    def total_assets(self) -> float:
        return sum(asset.value for asset in self.assets.values())

    @property
    def total_liabilities(self) -> float:
        return sum(liability.value for liability in self.liabilities.values())

    @property
    def total_equity(self) -> float:
        return sum(equity.value for equity in self.equity.values())

class IncomeStatement(BaseModel):
    period: str
    statement_type: StatementType
    period_type: PeriodType
    revenue: FinancialMetric
    gross_profit: FinancialMetric
    operating_income: FinancialMetric
    net_income: FinancialMetric
    ebit: FinancialMetric
    ebitda: FinancialMetric

    @property
    def gross_margin(self) -> float:
        return self.gross_profit.value / self.revenue.value if self.revenue.value != 0 else 0

    @property
    def operating_margin(self) -> float:
        return self.operating_income.value / self.revenue.value if self.revenue.value != 0 else 0

    @property
    def net_margin(self) -> float:
        return self.net_income.value / self.revenue.value if self.revenue.value != 0 else 0

class CashFlow(BaseModel):
    period: str
    statement_type: StatementType
    period_type: PeriodType
    operating: Dict[str, FinancialMetric]
    investing: Dict[str, FinancialMetric]
    financing: Dict[str, FinancialMetric]

    @property
    def net_operating_cash_flow(self) -> float:
        return sum(flow.value for flow in self.operating.values())

    @property
    def net_investing_cash_flow(self) -> float:
        return sum(flow.value for flow in self.investing.values())

    @property
    def net_financing_cash_flow(self) -> float:
        return sum(flow.value for flow in self.financing.values())

class FinancialRatios(BaseModel):
    period: str
    statement_type: StatementType
    period_type: PeriodType
    ebit: Optional[FinancialMetric] = None
    ebitda: Optional[FinancialMetric] = None
    net_income: Optional[FinancialMetric] = None
    gross_margin: Optional[float] = Field(None, le=1.0, ge=-1.0)
    ebit_margin: Optional[float] = Field(None, le=1.0, ge=-1.0)
    net_margin: Optional[float] = Field(None, le=1.0, ge=-1.0)
    roe: Optional[float] = None
    roa: Optional[float] = None

class MarketRatios(BaseModel):
    date: datetime
    market_cap: Optional[FinancialMetric] = None
    enterprise_value: Optional[FinancialMetric] = None
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

class Ticker(BaseModel):
    ticker: str
    name: str
    type: str
    market: str
    market_type: str
    currency: str
    isin: str
    issuer_code: str
    last_quote: Quote
    penultimate_quote: Optional[Quote] = None
    change: Optional[float] = None

class Fund(BaseModel):
    begin_date: datetime
    benchmark: Optional[str] = None
    cnpj: str
    fund_class: str
    cvm_code: str
    name: str
    trade_name: str
    net_worth: Optional[float] = None
    shareholders: Optional[int] = None
    type: str
    management_fee: Optional[float] = None
    performance_fee: Optional[float] = None
    management_fee_description: Optional[str] = None
    performance_fee_description: Optional[str] = None

    @validator('begin_date', pre=True)
    def parse_date(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v
 