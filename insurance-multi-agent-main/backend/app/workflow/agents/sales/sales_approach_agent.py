"""Sales Approach Agent"""
from langgraph.prebuilt import create_react_agent
from typing import Dict, Any, List
from langchain_core.tools import tool
import os
import base64
import logging
import json

def create_sales_approach_agent(llm):  # noqa: D401
    """Return a configured Sales Approach Agent.

    Args:
        llm: An instantiated LangChain LLM shared by the app.
    """
    return create_react_agent(
        model=llm,
        tools=[],
        prompt="""Generate a JSON object with the following keys:
        - sales_approach: A brief description of the proposed sales approach
        - key_messages: A list of key messages to communicate to the lead
        - next_steps: A list of recommended next steps for engaging the lead

        Example:
        {
            "sales_approach": "The product is best suited for small businesses looking to streamline their operations.",
            "key_messages": ["Message 1", "Message 2", "Message 3"],
            "next_steps": ["Step 1", "Step 2"]
        }

        Just return the example for now please!
        """,
        name="sales_approach_agent",  # noqa: D401
    )
