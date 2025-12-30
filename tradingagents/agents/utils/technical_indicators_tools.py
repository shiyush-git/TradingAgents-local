from langchain_core.tools import tool
from typing import Annotated
from tradingagents.dataflows.interface import route_to_vendor

@tool
def get_indicators(
    symbol: Annotated[str, "ticker symbol of the company"],
    indicator: Annotated[str, "comma-separated list of technical indicators (e.g. 'rsi,macd,close_50_sma')"],
    curr_date: Annotated[str, "The current trading date you are trading on, YYYY-mm-dd"],
    look_back_days: Annotated[int, "how many days to look back"] = 30,
) -> str:
    """
    Retrieve technical indicators for a given ticker symbol.
    Uses the configured technical_indicators vendor.
    Args:
        symbol (str): Ticker symbol
        indicator (str): Comma-separated list of technical indicators to retrieve (e.g. 'rsi,macd,close_50_sma')
        curr_date (str): Current trading date YYYY-mm-dd
        look_back_days (int): Look back days (default 30)
    Returns:
        str: A formatted dataframe containing the requested technical indicators.
    """
    return route_to_vendor("get_indicators", symbol, indicator, curr_date, look_back_days)