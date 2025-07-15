"""Company News Research Agent"""
import os
import json
import logging
from typing import Dict, Any, List

import requests                                   # NEW – for HTTP call
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool

# ---------------------------------------------------------------------
# External data–fetching tools
# ---------------------------------------------------------------------

@tool
def search_company_news(company: str) -> Dict[str, Any]:
    """Call the local /api/search endpoint and return its JSON.
    
    Args:
        company: The company name, e.g. "Microsoft".
    
    Returns:
        Parsed JSON from the Next.js handler. Raises for HTTP errors.
    """
    url = os.getenv("SEARCH_API_URL", "http://localhost:3000/api/search")
    try:
        res = requests.post(url, files={"company": (None, company)})
        res.raise_for_status()
        return res.json()
    except Exception as exc:                      # log + re‑raise for the agent
        logging.exception("search_company_news failed: %s", exc)
        raise

# (You can flesh these out later or remove them if unused)
@tool
def get_news_article(article_id: str) -> Dict[str, Any]:
    """Return full text for a given article id (stub)."""
    return {}

@tool
def get_trending_topics() -> List[str]:
    """Return a list of trending news topics (stub)."""
    return []

# ---------------------------------------------------------------------
# Agent factory
# ---------------------------------------------------------------------

def create_news_info_agent(llm):
    """Configure and return a News‑Info Research ReAct agent."""
    return create_react_agent(
        model=llm,
        tools=[search_company_news],
        name="news_info_agent",
        prompt=(
            "You are a company‑news research assistant. "
            "When the user gives a company name or ticker, "
            "use the `search_company_news` tool first to retrieve the latest "
            "Brave + Tavily results and summary. "
            "Then analyse or drill down with the other tools as needed. "
            "Think step‑by‑step, show your reasoning, and finish with a clear answer."
        ),
    )
