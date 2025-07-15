"""Product Fit Agent"""
from langgraph.prebuilt import create_react_agent
from typing import Dict, Any, List
from langchain_core.tools import tool
import os
import base64
import logging
import json

@tool
def get_news_article(article_id: str) -> Dict[str, Any]:
    return None


@tool
def get_trending_topics() -> List[str]:
    return []

def create_product_fit_agent(llm):  # noqa: D401
    """Return a configured Product Fit Agent.

    Args:
        llm: An instantiated LangChain LLM shared by the app.
    """
    return create_react_agent(
        model=llm,
        tools=[get_news_article, get_trending_topics],
        prompt="""TODO: Create a prompt here""",
        name="product_fit_agent",  # noqa: D401
    )
