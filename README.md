# AI Hedge Fund

An AI-powered market analysis tool that combines technical and fundamental analysis using agent-based architecture.

## Features

- Natural language interface for market analysis
- Technical analysis (momentum, trends, patterns)
- Fundamental analysis (valuation, financial health)
- Data from B3 (Brazilian stock exchange)
- Detailed reasoning from each analysis component
- Customizable date ranges for analysis

## Setup

1. Clone the repository:
```bash
git clone https://github.com/PedroDnT/ai-hedge-fund.git
cd ai-hedge-fund
```

2. Create and activate virtual environment:
```bash
# Create virtual environment
python -m venv venv

# Activate on Unix/macOS
source venv/bin/activate

# Activate on Windows
.\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Create .env file with your API keys
echo "BEARER_TOKEN=your_token_here" > .env
```

## Usage

### Command Line Interface

Basic usage:
```bash
python analyze.py "What's your technical analysis of PETR4?"
```

With date range:
```bash
python analyze.py "How's PETR4 performing?" --start-date 2024-01-01 --end-date 2024-03-10
```

Hide detailed reasoning:
```bash
python analyze.py "Analyze PETR4 fundamentals" --hide-reasoning
```

### Python API

```python
from src.agent_orchestrator import analyze_prompt

# Simple usage
result = analyze_prompt("What's your technical analysis of PETR4?")

# Advanced usage
result = analyze_prompt(
    prompt="How's PETR4 performing? Focus on valuation metrics.",
    start_date="2024-01-01",
    end_date="2024-03-10",
    show_reasoning=True
)
```

## Example Prompts

1. Technical Analysis:
   - "What's the momentum and trend analysis for PETR4?"
   - "Show me PETR4's technical indicators and price patterns"
   - "Is PETR4 showing any bullish signals?"

2. Fundamental Analysis:
   - "What's the valuation and financial health of PETR4?"
   - "Analyze PETR4's profitability ratios"
   - "How efficient is PETR4's operations?"

3. Combined Analysis:
   - "Give me a complete analysis of PETR4"
   - "Should I invest in PETR4? Consider all factors"
   - "What's your outlook on PETR4?"

## Architecture

The system uses an agent-based architecture:

1. Market Data Agent:
   - Fetches market data, financial statements, and company information
   - Uses DadosDeMercado API for Brazilian market data

2. Technical Analysis Agent:
   - Analyzes price patterns and momentum
   - Calculates technical indicators (RSI, MACD, Bollinger Bands, OBV)

3. Fundamental Analysis Agent:
   - Analyzes financial ratios and company health
   - Evaluates valuation metrics and profitability

4. Orchestrator:
   - Coordinates agents based on user prompts
   - Combines analyses into coherent responses
   - Provides natural language summaries

## Data Sources

- Market Data: DadosDeMercado API
- Coverage: Brazilian stocks (B3)
- Data Types:
  - Price data
  - Financial statements
  - Company information
  - Market ratios
  - Financial metrics

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
