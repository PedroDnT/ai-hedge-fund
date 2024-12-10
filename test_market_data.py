from src.tools.new_tools import (
    get_quotes,
    list_cia,
    get_balance_sheet,
    get_income_statements,
    get_financial_ratios,
    get_market_ratios
)

def test_api_calls():
    """Test basic API functionality"""
    print("\nTesting API Calls")
    print("=" * 50)
    
    # Test company listing
    print("\n1. Testing company listing...")
    try:
        companies = list_cia()
        print(f"✓ Found {len(companies)} companies")
        if companies:
            print(f"Sample company: {companies[0]['name']} (CVM: {companies[0]['cvm_code']})")
    except Exception as e:
        print(f"✗ Company listing failed: {str(e)}")
    
    # Test quote retrieval
    print("\n2. Testing quote retrieval...")
    try:
        quotes = get_quotes("PETR4")
        print(f"✓ Retrieved quotes for PETR4")
        print(f"Latest quote: {quotes.iloc[-1].to_dict()}")
    except Exception as e:
        print(f"✗ Quote retrieval failed: {str(e)}")
    
    # Test financial data
    if companies:
        cvm_code = companies[0]['cvm_code']
        print(f"\n3. Testing financial data for CVM {cvm_code}...")
        
        try:
            # Balance sheet
            balance = get_balance_sheet(cvm_code)
            print("✓ Retrieved balance sheet")
            
            # Income statement
            income = get_income_statements(cvm_code)
            print("✓ Retrieved income statement")
            
            # Financial ratios
            ratios = get_financial_ratios(cvm_code)
            print("✓ Retrieved financial ratios")
            
            # Market ratios
            market = get_market_ratios(cvm_code)
            print("✓ Retrieved market ratios")
            
        except Exception as e:
            print(f"✗ Financial data retrieval failed: {str(e)}")

if __name__ == "__main__":
    test_api_calls() 