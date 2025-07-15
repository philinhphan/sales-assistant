"""Company News Research Agent"""
import os
import json
import logging
from typing import Dict, Any, List

import requests                                   # NEW – for HTTP call

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
    url = os.getenv("SEARCH_API_URL", "https://8fa1d6d81eba.ngrok-free.app/api/search")
    try:
        res = requests.post(url, files={"company": (None, company)})
        res.raise_for_status()
        return res.json()
    except Exception as exc:                      # log + re‑raise for the agent
        logging.exception("search_company_news failed: %s", exc)
        raise

# ---------------------------------------------------------------------
# Agent factory
# ---------------------------------------------------------------------

def create_news_info_agent(llm):
    """Configure and return a News‑Info Research ReAct agent."""
    return create_react_agent(
        model=llm,
        tools=[search_company_news],
        name="Microsoft",
        prompt=(
            "You are a company‑news research assistant. "
            "When the user gives a company name or ticker, "
            "use the `search_company_news` tool first to retrieve the latest "
            "Brave + Tavily results and summary. "
            "Then analyse or drill down with the other tools as needed. "
            "Think step‑by‑step, show your reasoning, and finish with a clear answer."
        ),
    )
