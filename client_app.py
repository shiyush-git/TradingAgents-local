
import os
import sys
from datetime import datetime, timedelta
import dotenv

# Load environment variables
dotenv.load_dotenv(override=True)

from tradingagents.graph.trading_graph import TradingAgentsGraph

def run_analysis(ticker: str):
    """
    Run the trading analysis for a given ticker.
    """
    print(f"\nAnalying {ticker}...")
    
    # Use today's date if possible, otherwise yesterday (common for market data availability)
    trade_date = datetime.now().strftime("%Y-%m-%d")
    
    # Initialize the graph with default configuration (which now points to Local Ollama/Cloud DeepSeek)
    try:
        trading_graph = TradingAgentsGraph(debug=True)
        
        # Propagate the graph
        final_state, decision = trading_graph.propagate(ticker, trade_date)
        
        print(f"\n--- Analysis Complete for {ticker} ---")
        print(f"Date: {final_state['trade_date']}")
        print(f"Final Decision: {final_state['final_trade_decision']}")
        print(f"Investment Plan: {final_state['investment_plan']}")
        
        # Optionally show where the report is saved
        print(f"\nDetailed logs saved to: eval_results/{ticker}/TradingAgentsStrategy_logs/")
        print(f"Individual reports (EN/CN) and PDFs saved to: results/{ticker}/{trade_date}/")
        
    except Exception as e:
        print(f"An error occurred during analysis: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("Welcome to TradingAgents (Local Ollama / DeepSeek Cloud Edition)")
    print("----------------------------------------------------------------")
    
    while True:
        user_input = input("\nEnter stock ticker (e.g., AAPL) or 'exit' to quit: ").strip().upper()
        
        if user_input == 'EXIT':
            print("Goodbye!")
            break
        
        if not user_input:
            continue
            
        run_analysis(user_input)

if __name__ == "__main__":
    main()
