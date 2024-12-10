from tools.new_tools import get_quotes, list_cia

def main():
    print("Testing API functionality...")
    
    # Test company listing
    companies = list_cia()
    print(f"\nFound {len(companies)} companies")
    if companies:
        print(f"First company: {companies[0]}")
    
    # Test quote retrieval
    quotes = get_quotes("PETR4")
    print(f"\nPETR4 latest quote:")
    print(quotes.iloc[-1])

if __name__ == "__main__":
    main() 