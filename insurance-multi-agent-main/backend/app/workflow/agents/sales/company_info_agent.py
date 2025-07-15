"""Company Info Research Agent"""
from langgraph.prebuilt import create_react_agent
from typing import Dict, Any, List
from dotenv import load_dotenv
from langchain_core.tools import tool
import os
import requests
import base64
import logging
import json

load_dotenv()

@tool
def get_company_info_from_handelsregister(company_query: str) -> Dict[str, Any]:
    """
    Query handelsregister.ai for company information by company name and location.
    Args:
        company_query: The company name.
    Returns:
        A dictionary with company information.
    """
    try:
        api_key = os.getenv("HANDELSREGISTER_API_KEY")
        url = "https://handelsregister.ai/api/v1/fetch-organization"
        params = {
            "api_key": api_key,
            "q": company_query,
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data and "entity_id" in data:
            return data
        else:
            return {"error": "No company found for the given query."}
    except Exception as e:
        return {"error": str(e)}

def create_company_info_agent(llm):  # noqa: D401
    """Return a configured Company Info Research Agent.

    Args:
        llm: An instantiated LangChain LLM shared by the app.
    """
    return create_react_agent(
        model=llm,
        tools=[get_company_info_from_handelsregister],
        prompt=(
            "You are a company information research specialist. "
            "Given a company name provided by the supervisor, "
            "use the 'get_company_info_from_handelsregister' tool to retrieve company information from handelsregister.ai. "
            "Return the raw JSON response from the API call without modification. "
            "If no information is found, return the error message."
        ),
        name="company_info_agent",
    )