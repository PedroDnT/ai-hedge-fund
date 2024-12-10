#!/usr/bin/env python3
import argparse
from datetime import datetime, timedelta
from src.agent_orchestrator import analyze_prompt

def validate_date(date_str: str) -> str:
    """Validate date format"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return date_str
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_str}. Use YYYY-MM-DD")

def main():
    parser = argparse.ArgumentParser(description='AI Market Analysis Tool')
    
    parser.add_argument(
        'prompt',
        type=str,
        help='Analysis prompt (e.g., "What\'s your technical analysis of PETR4?")'
    )
    
    parser.add_argument(
        '--start-date',
        type=validate_date,
        help='Start date for analysis (YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--end-date',
        type=validate_date,
        help='End date for analysis (YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--hide-reasoning',
        action='store_true',
        help='Hide detailed reasoning from agents'
    )
    
    args = parser.parse_args()
    
    # Set default dates if not provided
    if not args.end_date:
        args.end_date = datetime.now().strftime('%Y-%m-%d')
    
    if not args.start_date:
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
        args.start_date = (end_date - timedelta(days=90)).strftime('%Y-%m-%d')
    
    # Run analysis
    result = analyze_prompt(
        prompt=args.prompt,
        start_date=args.start_date,
        end_date=args.end_date,
        show_reasoning=not args.hide_reasoning
    )
    
    print(result)

if __name__ == "__main__":
    main() 