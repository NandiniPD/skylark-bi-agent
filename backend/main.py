"""
FastAPI Backend — Skylark Drones BI Agent
Main application entry point
"""

import os
import logging
import asyncio
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from monday_client import MondayClient
from data_processor import process_work_orders, process_deals
from ai_agent import BIAgent
from demo_data import DEMO_DEALS, DEMO_WORK_ORDERS

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# --- Global singletons ---
monday_client = MondayClient()
bi_agent = BIAgent()
_data_loaded = False
_data_load_error: Optional[str] = None


async def load_monday_data():
    """Fetch and process data from monday.com boards. Falls back to demo data on failure."""
    global _data_loaded, _data_load_error
    monday_ok = False

    # Try Monday.com first
    if monday_client.is_configured():
        try:
            logger.info("Fetching data from monday.com...")
            raw = await monday_client.get_all_data()
            wo_items = raw.get("work_orders", [])
            deals_items = raw.get("deals", [])

            if wo_items or deals_items:
                wo_processed = process_work_orders(wo_items)
                deals_processed = process_deals(deals_items)
                errors = {}
                if "work_orders_error" in raw:
                    errors["work_orders"] = raw["work_orders_error"]
                if "deals_error" in raw:
                    errors["deals"] = raw["deals_error"]
                bi_agent.update_data_context(wo_processed, deals_processed, errors or None)
                _data_loaded = True
                _data_load_error = None
                monday_ok = True
                logger.info(f"Monday.com data loaded: {wo_processed['total']} WOs, {deals_processed['total']} deals")
            else:
                logger.warning("Monday.com returned empty data — falling back to demo data")
        except Exception as e:
            logger.error(f"Monday.com failed: {e} — falling back to demo data")
    else:
        logger.warning("Monday.com not configured — loading demo data")

    # Fall back to demo data if Monday.com failed or returned nothing
    if not monday_ok:
        logger.info("Loading demo data (Skylark Drones sample data)...")
        wo_processed = process_work_orders(DEMO_WORK_ORDERS)
        deals_processed = process_deals(DEMO_DEALS)
        bi_agent.update_data_context(wo_processed, deals_processed)
        _data_loaded = True
        _data_load_error = "Using demo data — Monday.com API not authenticated yet"
        logger.info(f"Demo data loaded: {wo_processed['total']} WOs, {deals_processed['total']} deals")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load data on startup"""
    await load_monday_data()
    yield


app = FastAPI(
    title="Skylark Drones BI Agent API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend origins
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins + ["*"],  # Permissive for demo; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Pydantic Models ---

class ChatRequest(BaseModel):
    message: str
    conversation_history: list[dict] = []


class ChatResponse(BaseModel):
    reply: str
    data_status: dict


class RefreshResponse(BaseModel):
    success: bool
    message: str
    data_summary: dict


# --- Routes ---

@app.get("/")
async def root():
    return {
        "service": "Skylark Drones BI Agent",
        "version": "1.0.0",
        "status": "running",
        "data_loaded": _data_loaded,
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "monday_configured": monday_client.is_configured(),
        "data_loaded": _data_loaded,
        "data_error": _data_load_error,
        "data_summary": bi_agent.get_data_summary(),
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Main chat endpoint — accepts user message, returns AI response"""
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    reply = await bi_agent.chat(
        user_message=req.message.strip(),
        conversation_history=req.conversation_history,
    )

    return ChatResponse(
        reply=reply,
        data_status=bi_agent.get_data_summary(),
    )


@app.post("/refresh", response_model=RefreshResponse)
async def refresh_data():
    """Manually trigger a data refresh from monday.com"""
    await load_monday_data()
    summary = bi_agent.get_data_summary()

    if _data_load_error:
        return RefreshResponse(
            success=False,
            message=f"Data refresh failed: {_data_load_error}",
            data_summary=summary,
        )

    return RefreshResponse(
        success=True,
        message="Data refreshed successfully from monday.com",
        data_summary=summary,
    )


@app.get("/data/summary")
async def data_summary():
    """Get a summary of currently loaded data"""
    return {
        "loaded": _data_loaded,
        "error": _data_load_error,
        "summary": bi_agent.get_data_summary(),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
