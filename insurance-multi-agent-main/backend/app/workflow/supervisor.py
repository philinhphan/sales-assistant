"""Supervisor orchestration for the insurance claim workflow.

This module creates the specialized agents, compiles the LangGraph supervisor,
and exposes a `process_claim_with_supervisor` helper used by the service layer.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, TypedDict

from app.models.output import LeadIn, LeadOut
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langgraph_supervisor import create_handoff_tool, create_supervisor

from app.core.logging_config import configure_logging


from .agents.sales.company_info_agent import create_company_info_agent
from .agents.sales.news_info_agent import create_news_info_agent
from .agents.sales.product_fit_agent import create_product_fit_agent
from .agents.sales.sales_approach_agent import create_sales_approach_agent
from .agents.sales.poi_agent import create_poi_agent

load_dotenv()

# ---------------------------------------------------------------------------
# Configure logging (pretty icons + single-line formatter)
# ---------------------------------------------------------------------------

configure_logging()
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Shared LLM configuration (Azure OpenAI)
# ---------------------------------------------------------------------------


def _build_llm() -> AzureChatOpenAI:  # noqa: D401
    """Instantiate AzureChatOpenAI with centralized config."""
    from app.core.config import get_settings

    settings = get_settings()
    endpoint = settings.azure_openai_endpoint
    deployment = settings.azure_openai_deployment_name or "gpt-4o"
    api_key = settings.azure_openai_api_key

    logger.info("✅ Configuration loaded successfully")
    logger.info("Azure OpenAI Endpoint: %s", endpoint or "Not set")
    logger.info("Deployment Name: %s", deployment)
    logger.info("API Key configured: %s", "Yes" if api_key else "No")

    return AzureChatOpenAI(
            azure_deployment=deployment,
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version="2024-12-01-preview",
            temperature=0.1,
        )
    


LLM = _build_llm()

# ---------------------------------------------------------------------------
# Create specialized agents
# ---------------------------------------------------------------------------

company_info_agent = create_company_info_agent(LLM)
news_info_agent = create_news_info_agent(LLM)
product_fit_agent = create_product_fit_agent(LLM)
sales_approach_agent = create_sales_approach_agent(LLM)
poi_agent = create_poi_agent(LLM)

logger.info("✅ Specialized agents created successfully:")
logger.info("- 🔍 Company Info Agent: Retrieves company information and history")
logger.info("- 📋 News Info Agent: Gathers relevant news articles and updates")
logger.info("- ⚠️ Product Fit Agent: Assesses product suitability for the claim")
logger.info("- 📈 Sales Approach Agent: Develops sales strategies based on claim data")
logger.info("- 📍 POI Agent: Identifies points of interest related to the claim")

# ---------------------------------------------------------------------------
# Compile supervisor
# ---------------------------------------------------------------------------


# --- Build the supervisor with parallel fork/join ---
def create_sales_supervisor():
    """
    This supervisor will:
      1) Fork to company_info_agent & news_info_agent in parallel
      2) Join their outputs into product_fit_agent
      3) Fork again to poi_agent & sales_approach_agent in parallel
      4) Finally emit a pure JSON object matching our LeadOut schema
    """

    supervisor = create_supervisor(
        agents=[
            company_info_agent,
            news_info_agent,
            product_fit_agent,
            poi_agent,
            sales_approach_agent,
        ],
        model=LLM,
        prompt="""
You are a senior sales manager orchestrating a multi-agent workflow.

 1) Fork in parallel:
    - Call `transfer_to_company_info_agent` with {{lead data}}  
    - Call `transfer_to_news_info_agent` with {{lead data}}  

 2) When both return, call `transfer_to_product_fit_agent` with:
    {
      "companyInfo": <company_info JSON>,
      "newsInfo":    <news_info JSON>
    }

 3) Then fork again:
    - Call `transfer_to_poi_agent` with productFit JSON  
    - Call `transfer_to_sales_approach_agent` with productFit JSON  

4) Finally, return a JSON object like the following example:
{
  lufthansa: {
  name: "Lufthansa",
  headquarters: "Cologne, Germany",
  employees: "110,000+",
  coreProducts: ["Passenger Airlines", "Cargo Services", "Aircraft Maintenance", "Catering Services"],
  news: [
    {
      title: "Lufthansa Group invests €2.5B in fleet modernization and digitalization",
      description: "Major investment program includes new aircraft and comprehensive digital infrastructure upgrades to improve operational efficiency and customer experience.",
      type: "Success",
      date: "2024-12-05"
    },
    {
      title: "New sustainability initiative targets carbon neutrality by 2030",
      description: "Comprehensive program includes fuel efficiency optimization, sustainable aviation fuels, and carbon offset programs requiring advanced data analytics platforms.",
      type: "Success",
      date: "2024-11-20"
    },
    {
      title: "Digital transformation of maintenance operations announced",
      description: "Implementation of predictive maintenance systems and IoT sensors across fleet to reduce downtime and improve safety through real-time data analysis.",
      type: "Product",
      date: "2024-10-18"
    }
  ],
  productFit: {
    product: "Microsoft Azure IoT & Analytics",
    confidence: "High",
    reasoning: "Lufthansa's focus on fleet modernization, predictive maintenance, and sustainability initiatives requires robust IoT data processing and analytics capabilities that Azure specializes in."
  },
  keyContacts: [
    {
      name: "Christina Foerster",
      position: "Member of Executive Board",
      department: "Customer & Digital",
      reasoning: "Christina oversees Lufthansa's digital transformation initiatives and would champion cloud solutions that enhance customer experience and operational efficiency."
    },
    {
      name: "Detlef Kayser",
      position: "Member of Executive Board",
      department: "Fleet & Technology",
      reasoning: "Responsible for fleet management and technology infrastructure. Key decision-maker for IoT and analytics solutions for aircraft maintenance and operations."
    }
  ],
  salesApproach: "To align with Lufthansa’s ambitious €2.5 billion modernization and digitalization program, position Azure as the strategic backbone for their entire transformation journey. Begin by demonstrating how Azure IoT can seamlessly integrate with existing aircraft sensor data to enable predictive maintenance, reducing unscheduled downtime and maintenance costs. Emphasize advanced analytics services to optimize fuel consumption and support the carbon‑neutral 2030 goal through real‑time insights and sustainable aviation fuel tracking. Showcase scalable Azure infrastructure and global support footprint to handle large volumes of telemetry data from international operations, ensuring regulatory compliance and data sovereignty. Propose a phased pilot—integrating one hub’s maintenance workflows—to prove rapid ROI, followed by enterprise‑wide rollout. Highlight security, compliance certifications, and managed services that reduce IT overhead and accelerate time to value, reinforcing Lufthansa’s reputation for reliability and safety."
},
  enpal: {
    name: "Enpal",
    headquarters: "Berlin, Germany",
    employees: "2,500+",
    coreProducts: ["Solar Panel Installation", "Energy Storage Solutions", "Energy Management Software", "Green Energy Services"],
    news: [
      {
        title: "Enpal secures €215M Series C funding for European expansion",
        description: "Major funding round led by SoftBank to accelerate expansion across European markets and enhance technology platform for solar energy management.",
        type: "Success",
        date: "2024-11-30"
      },
      {
        title: "Launch of AI-powered energy optimization platform",
        description: "New platform uses machine learning to optimize energy consumption and storage for residential customers, requiring scalable cloud infrastructure for data processing.",
        type: "Product",
        date: "2024-11-12"
      },
      {
        title: "Partnership with major European utilities for grid integration",
        description: "Strategic partnerships to integrate Enpal's residential solar systems with national power grids, requiring robust data exchange and management systems.",
        type: "Partnership",
        date: "2024-10-25"
      }
    ],
    productFit: {
      product: "Microsoft Azure AI & Data Analytics",
      confidence: "High",
      reasoning: "Enpal's rapid growth, new AI-powered platform, and need for scalable infrastructure to support European expansion make Azure's AI and analytics services essential for their technology roadmap."
    },
    keyContacts: [
      {
        name: "Mario Kohle",
        position: "Co-Founder & CEO",
        department: "Executive",
        reasoning: "As CEO of a fast-growing startup, Mario makes strategic technology decisions. He'll appreciate Azure's scalability and AI capabilities for Enpal's expansion plans."
      },
      {
        name: "Victor Geissler",
        position: "CTO",
        department: "Technology",
        reasoning: "Victor leads Enpal's technology strategy and platform development. He's the key technical decision-maker for cloud infrastructure and AI/ML capabilities."
      }
    ],
    salesApproach: "Emphasize Azure's ability to scale with Enpal's rapid growth and European expansion. Highlight AI/ML capabilities for their energy optimization platform and cost-effective solutions suitable for a growing startup. Focus on innovation partnership and Microsoft's commitment to sustainability aligning with Enpal's mission."
  }
}


Do not emit any extra text or markdown—just the JSON.
        """,
        parallel_tool_calls=True,           # enable true fork/join
        response_format=LeadOut,    # enforce the JSON schema
        output_mode="last_message",         # return only the final combined response
    ).compile()

    return supervisor


sales_supervisor = create_sales_supervisor()
logger.info("✅ Sales supervisor created successfully")



def process_lead_with_json(lead_data: LeadIn) -> LeadOut:
    # Kick off the workflow with a single user message
    inputs = {
        "messages": [
            {
                "role": "user",
                "content": (
                    "Process this lead:\n\n"
                    f"{json.dumps(lead_data, indent=2)}"
                ),
            }
        ]
    }

    # Run synchronously (you could also stream if you prefer)
    result_state = sales_supervisor.invoke(inputs)
    # The structured JSON will live in `result_state["structured_response"]`
    return result_state["structured_response"]