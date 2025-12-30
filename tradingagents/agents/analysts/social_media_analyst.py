from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from tradingagents.agents.utils.agent_utils import get_news
from tradingagents.dataflows.config import get_config


def create_social_media_analyst(llm):
    def social_media_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        tools = [
            get_news,
        ]

        system_message = (
            "You are a dedicated Social Media and Sentiment Analyst. Your job is to capture the 'pulse' of the market regarding the target company."
            "\n\nKey Objectives:"
            "\n1. Use 'get_news' to find discussions, forum posts, and sentiment-heavy articles."
            "\n2. Analyze the emotional tone: Is the crowd euphoric, fearful, or indifferent?"
            "\n3. Identify contrarian indicators (e.g., peak euphoria often precedes a crash)."
            "\n\nIMPORTANT:"
            "\n- Dig deep into the qualitative feel of the market."
            "\n- Do not just list headlines; interpret the *sentiment*."
            "\n- Output a professional Markdown report."
            "\n- Include a Markdown table summarizing Sentiment Score (1-10) and Key Discussion Topics."
            "\n\nTool Usage Guidelines:"
            "\n- Use 'get_news' with creative queries if needed (e.g., '$TICKER sentiment', '$TICKER reddit')."
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK; another assistant with different tools"
                    " will help where you left off. Execute what you can to make progress."
                    " If you or any other assistant has the FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** or deliverable,"
                    " prefix your response with FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** so the team knows to stop."
                    " You have access to the following tools: {tool_names}.\n{system_message}"
                    "For your reference, the current date is {current_date}. The current company we want to analyze is {ticker}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "sentiment_report": report,
        }

    return social_media_analyst_node
