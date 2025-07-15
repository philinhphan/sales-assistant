"""Person of Interest (POI) Search Agent"""
from langgraph.prebuilt import create_react_agent
from typing import Dict, Any, List
from langchain_core.tools import tool
import os
import base64
import logging
import json

def create_poi_agent(llm):  # noqa: D401
    """Return a configured Person of Interest (POI) Search Agent.

    Args:
        llm: An instantiated LangChain LLM shared by the app.
    """
    return create_react_agent(
        model=llm,
        tools=[],
        prompt="""
        Return a json object with the following keys:
        - name: The name of the person of interest
        - position: The current position or role of the person
        - company: The company where the person works
        - location: The geographical location of the person
        - linkedin_url: A URL to the person's LinkedIn profile

        Example:
        {
            "name": "John Doe",
            "position": "Software Engineer",
            "company": "Tech Corp",
            "location": "San Francisco, CA",
            "linkedin_url": "https://www.linkedin.com/in/johndoe"
        }

        Just return the example for now please!
        """,
        name="poi_agent",  # noqa: D401
    )
