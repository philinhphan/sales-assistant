from app.models.output import LeadIn, LeadOut
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging

from app.workflow.supervisor import process_lead_with_json
router = APIRouter(tags=["sales"])

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 1. Define your request & response schemas
# ──────────────────────────────────────────────────────────────────────────────


# ──────────────────────────────────────────────────────────────────────────────
# 2. The endpoint
# ──────────────────────────────────────────────────────────────────────────────
@router.post("/workflow/run", response_model=LeadOut)
async def run_sales_workflow(lead: LeadIn):
    """
    1) Pull company_name & country from the request
    2) Call the LangGraph supervisor to process the lead
    3) Return the JSON structure it emits
    """
    try:
        # 1. Build the minimal lead_data dict
        lead_data = {
            "company_name": lead.company_name,
            "country":      lead.country,
        }

        # 2. Call your helper which orchestrates the graph and parses JSON
        result: dict = process_lead_with_json(lead_data)

        # 3. Return it directly (FastAPI will jsonify for you)
        return result

    except Exception as exc:
        logger.error("Sales workflow failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))
