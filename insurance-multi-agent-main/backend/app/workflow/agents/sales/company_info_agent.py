"""Company Info Research Agent"""
from langgraph.prebuilt import create_react_agent
from typing import Dict, Any, List
from langchain_core.tools import tool
import os
import base64
import logging
import json

@tool
def get_policy_details(policy_number: str) -> Dict[str, Any]:
    return None


@tool
def get_claimant_history(claimant_id: str) -> Dict[str, Any]:
    return None

def create_company_info_agent(llm):  # noqa: D401
    """Return a configured Company Info Research Agent.

    Args:
        llm: An instantiated LangChain LLM shared by the app.
    """
    return create_react_agent(
        model=llm,
        tools=[get_policy_details, get_claimant_history],
        prompt="""TODO: Create a prompt here""",
        name="company_info_agent",
    )
