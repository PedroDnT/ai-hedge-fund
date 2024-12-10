from src.tools.new_tools import (
    get_quotes,
    list_cia,
    get_balance_sheet,
    get_income_statements,
    get_financial_ratios,
    get_market_ratios
)
import pandas as pd
from datetime import datetime, timedelta

def test_api():
    """Test basic API functionality"""
    
    # Test company listing
    print("\n1. Testing company listing...")
    try:
        companies = list_cia()
        print(f"✓ Found {len(companies)} companies")
        if companies:
            company = companies[0]
            print(f"Sample company: {company['name']}")
            print(f"Fields available: {list(company.keys())}")
    except Exception as e:
        print(f"✗ Company listing failed: {str(e)}")
        return
    
    # Get a valid CVM code for further tests
    cvm_code = companies[0]['cvm_code']
    
    # Test quote retrieval
    print("\n2. Testing quote retrieval...")
    try:
        quotes = get_quotes("PETR4")
        print(f"✓ Retrieved quotes for PETR4")
        latest = quotes.iloc[-1]
        print(f"Latest quote fields: {list(latest.index)}")
        print(f"Latest values: {latest.to_dict()}")
    except Exception as e:
        print(f"✗ Quote retrieval failed: {str(e)}")
    
    # Test balance sheet
    print(f"\n3. Testing balance sheet for CVM {cvm_code}...")
    try:
        balance = get_balance_sheet(cvm_code)
        print("✓ Retrieved balance sheet")
        if isinstance(balance, list):
            sample = balance[0]
        else:
            sample = balance
        print(f"Fields available: {list(sample.keys())}")
        print(f"Sample data: {sample}")
    except Exception as e:
        print(f"✗ Balance sheet retrieval failed: {str(e)}")
    
    # Test income statement
    print(f"\n4. Testing income statement for CVM {cvm_code}...")
    try:
        income = get_income_statements(cvm_code)
        print("✓ Retrieved income statement")
        if isinstance(income, list):
            sample = income[0]
        else:
            sample = income
        print(f"Fields available: {list(sample.keys())}")
    except Exception as e:
        print(f"✗ Income statement retrieval failed: {str(e)}")
    
    # Test financial ratios
    print(f"\n5. Testing financial ratios for CVM {cvm_code}...")
    try:
        ratios = get_financial_ratios(cvm_code)
        print("✓ Retrieved financial ratios")
        if isinstance(ratios, list):
            sample = ratios[0]
        else:
            sample = ratios
        print(f"Fields available: {list(sample.keys())}")
    except Exception as e:
        print(f"✗ Financial ratios retrieval failed: {str(e)}")
    
    # Test market ratios
    print(f"\n6. Testing market ratios for CVM {cvm_code}...")
    try:
        market = get_market_ratios(cvm_code)
        print("✓ Retrieved market ratios")
        if isinstance(market, list):
            sample = market[0]
        else:
            sample = market
        print(f"Fields available: {list(sample.keys())}")
    except Exception as e:
        print(f"✗ Market ratios retrieval failed: {str(e)}")

if __name__ == "__main__":
    test_api() 