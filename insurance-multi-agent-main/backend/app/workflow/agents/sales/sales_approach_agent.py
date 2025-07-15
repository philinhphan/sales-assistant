"""Sales Approach Agent"""
from langgraph.prebuilt import create_react_agent
from typing import Dict, Any, List
from langchain_core.tools import tool
import os
import base64
import logging
import json

# TODO: Implement tooling and pass it into the agent
@tool
def get_news_article(article_id: str) -> Dict[str, Any]:
    return None


@tool
def get_trending_topics() -> List[str]:
    return []

def create_sales_approach_agent(llm):  # noqa: D401
    """Return a configured Sales Approach Agent.

    Args:
        llm: An instantiated LangChain LLM shared by the app.
    """
    return create_react_agent(
        model=llm,
        tools=[get_news_article, get_trending_topics],
        prompt="""TODO: Create a prompt here""",
        name="sales_approach_agent",  # noqa: D401
    )
