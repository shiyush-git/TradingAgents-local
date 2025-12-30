import os
import sys
from datetime import datetime
from langchain_core.messages import HumanMessage

# Add GTK3 to PATH for WeasyPrint
gtk_location = r"C:\gtk\bin"
if os.path.exists(gtk_location):
    if gtk_location not in os.environ['PATH']:
        os.environ['PATH'] = gtk_location + os.pathsep + os.environ['PATH']
    if hasattr(os, 'add_dll_directory'):
        try:
            os.add_dll_directory(gtk_location)
        except Exception:
            pass

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.utils.report_generator import generate_chinese_pdf
from tradingagents.default_config import DEFAULT_CONFIG

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create a custom config
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = os.getenv("LLM_PROVIDER", "ollama")
config["deep_think_llm"] = os.getenv("DEEP_THINK_LLM", "deepseek-v3.2:cloud")
config["quick_think_llm"] = os.getenv("QUICK_THINK_LLM", "qwen3:14b")
config["news_agent_llm"] = os.getenv("NEWS_AGENT_LLM", "qwen3:14b")
config["backend_url"] = os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1")

config["max_debate_rounds"] = 1  # Increase debate rounds

# Configure data vendors (default uses yfinance and alpha_vantage)
config["data_vendors"] = {
    "core_stock_apis": "yfinance",           # Options: yfinance, alpha_vantage, local
    "technical_indicators": "yfinance",      # Options: yfinance, alpha_vantage, local
    "fundamental_data": "alpha_vantage",     # Options: openai, alpha_vantage, local
    "news_data": "alpha_vantage",            # Options: openai, alpha_vantage, google, local
}

# Initialize with custom config
ta = TradingAgentsGraph(debug=True, config=config)

# Get ticker from command line or default
user_input = sys.argv[1] if len(sys.argv) > 1 else "TSLA"

# Resolve ticker if it's likely a company name
def resolve_ticker(llm, input_str):
    # Heuristic: if it's 1-5 chars and all upper case, assume it's already a ticker
    if input_str.isalpha() and input_str.isupper() and len(input_str) <= 5:
        return input_str
    
    print(f"Resolving ticker for '{input_str}'...")
    prompt = f"""What is the stock ticker symbol for '{input_str}'? 
    Rules:
    1. Provide ONLY the ticker symbol (e.g., AAPL). 
    2. If the query is an index (like S&P 500, Nasdaq), provide the ticker for the most popular ETF tracking it (e.g., SPY for S&P 500, QQQ for Nasdaq). 
    3. Do NOT include special characters like '^' or '$'.
    4. Do not include any explanation or extra text."""
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        ticker = response.content.strip().upper().replace("$", "").replace("^", "")
        print(f"Resolved to: {ticker}")
        return ticker
    except Exception as e:
        print(f"Error resolving ticker: {e}")
        return input_str.upper()

ticker = resolve_ticker(ta.quick_thinking_llm, user_input)
date_str = datetime.now().strftime("%Y-%m-%d")

print(f"Starting analysis for {ticker} on {date_str}...")

# forward propagate
_, decision = ta.propagate(ticker, date_str)
print(decision)

# Generate Chinese PDF Report
generate_chinese_pdf(ta.quick_thinking_llm, ticker, date_str)

# Memorize mistakes and reflect
# ta.reflect_and_remember(1000) # parameter is the position returns
