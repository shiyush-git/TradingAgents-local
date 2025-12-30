
import os
import sys

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
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.utils.report_generator import generate_chinese_pdf
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

print("Initializing TradingAgentsGraph to get LLM...")
# Initialize with custom config
ta = TradingAgentsGraph(debug=True, config=config)

print("Starting PDF generation test...")
# Generate Chinese PDF Report
# We use the existing results for TSLA on 2025-12-29
generate_chinese_pdf(ta.quick_thinking_llm, "AAPL", "2025-12-30")

print("Test complete.")
