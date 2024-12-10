from src.tools.new_tools import (
    get_quotes,
    list_cia,
    get_balance_sheet,
    get_income_statements,
    get_financial_ratios,
    get_market_ratios
)
from src.schemas.market_data_schema import (
    Quote,
    CompanyInfo,
    FinancialRatios,
    MarketRatios,
    BalanceSheet,
    IncomeStatement
)
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
import json

def validate_quote_fields():
    """Validate Quote schema against actual API data"""
    print("\nValidating Quote fields...")
    quotes = get_quotes("PETR4")
    sample_quote = quotes.iloc[0].to_dict()
    print(f"API fields: {list(sample_quote.keys())}")
    print(f"Schema fields: {list(Quote.__fields__.keys())}")
    
    # Try creating Quote object
    quote = Quote(
        date=pd.to_datetime(sample_quote['date']),
        open=sample_quote['open'],
        close=sample_quote['close'],
        adj_close=sample_quote['adj_close'],
        min=sample_quote['min'],
        max=sample_quote['max'],
        volume=sample_quote['volume']
    )
    print("✓ Quote validation successful")
    return quote

def validate_company_fields():
    """Validate CompanyInfo schema against actual API data"""
    print("\nValidating CompanyInfo fields...")
    companies = list_cia()
    sample_company = companies[0]
    print(f"API fields: {list(sample_company.keys())}")
    print(f"Schema fields: {list(CompanyInfo.__fields__.keys())}")
    
    # Try creating CompanyInfo object
    company = CompanyInfo(**sample_company)
    print("✓ CompanyInfo validation successful")
    return company

def validate_financial_ratios(cvm_code: str):
    """Validate FinancialRatios schema against actual API data"""
    print("\nValidating FinancialRatios fields...")
    ratios = get_financial_ratios(cvm_code)
    sample_ratio = ratios[0] if isinstance(ratios, list) else ratios
    print(f"API fields: {list(sample_ratio.keys())}")
    print(f"Schema fields: {list(FinancialRatios.__fields__.keys())}")
    
    # Try creating FinancialRatios object
    ratio = FinancialRatios(**sample_ratio)
    print("✓ FinancialRatios validation successful")
    return ratio

def validate_market_ratios(cvm_code: str):
    """Validate MarketRatios schema against actual API data"""
    print("\nValidating MarketRatios fields...")
    ratios = get_market_ratios(cvm_code)
    sample_ratio = ratios[0] if isinstance(ratios, list) else ratios
    print(f"API fields: {list(sample_ratio.keys())}")
    print(f"Schema fields: {list(MarketRatios.__fields__.keys())}")
    
    # Try creating MarketRatios object
    ratio = MarketRatios(**sample_ratio)
    print("✓ MarketRatios validation successful")
    return ratio

def validate_balance_sheet(cvm_code: str):
    """Validate BalanceSheet schema against actual API data"""
    print("\nValidating BalanceSheet fields...")
    balance = get_balance_sheet(cvm_code)
    sample_balance = balance[0] if isinstance(balance, list) else balance
    print(f"API fields: {list(sample_balance.keys())}")
    print(f"Schema fields: {list(BalanceSheet.__fields__.keys())}")
    
    # Try creating BalanceSheet object
    sheet = BalanceSheet(**sample_balance)
    print("✓ BalanceSheet validation successful")
    return sheet

def validate_income_statement(cvm_code: str):
    """Validate IncomeStatement schema against actual API data"""
    print("\nValidating IncomeStatement fields...")
    income = get_income_statements(cvm_code)
    sample_income = income[0] if isinstance(income, list) else income
    print(f"API fields: {list(sample_income.keys())}")
    print(f"Schema fields: {list(IncomeStatement.__fields__.keys())}")
    
    # Try creating IncomeStatement object
    statement = IncomeStatement(**sample_income)
    print("✓ IncomeStatement validation successful")
    return statement

def run_validation():
    """Run all validations"""
    try:
        # Get a sample company first
        companies = list_cia()
        sample_cvm = companies[0]['cvm_code']
        
        # Run all validations
        quote = validate_quote_fields()
        company = validate_company_fields()
        fin_ratios = validate_financial_ratios(sample_cvm)
        market_ratios = validate_market_ratios(sample_cvm)
        balance = validate_balance_sheet(sample_cvm)
        income = validate_income_statement(sample_cvm)
        
        print("\n✓ All validations completed successfully!")
        
        # Save sample data for reference
        sample_data = {
            "quote": quote.dict(),
            "company": company.dict(),
            "financial_ratios": fin_ratios.dict(),
            "market_ratios": market_ratios.dict(),
            "balance_sheet": balance.dict(),
            "income_statement": income.dict()
        }
        
        with open("validation_samples.json", "w") as f:
            json.dump(sample_data, f, indent=2, default=str)
            print("\nSample data saved to validation_samples.json")
            
    except Exception as e:
        print(f"\n❌ Validation failed: {str(e)}")
        raise

if __name__ == "__main__":
    run_validation() 