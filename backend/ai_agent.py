"""
AI Agent — Skylark Drones BI Agent
Uses Groq REST API (qwen/qwen3.6-27b) for conversational intelligence.
"""

import os
import json
import logging
import httpx
import pandas as pd
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

DEALS_SCHEMA = """
Board: Deals
Columns:
  - Name (String)
  - Owner code (String)
  - Client Code (String)
  - Deal Status (Open / Won / Lost / Closed)
  - Close Date (A) (Date)
  - Closure Probability (High / Medium / Low)
  - Masked Deal value (Number in INR)
  - Tentative Close Date (Date)
  - Deal Stage (String)
  - Product deal (String)
  - Sector/service (String)
  - Created Date (Date)
"""

WORK_ORDERS_SCHEMA = """
Board: Work Orders
Columns:
  - Name (String)
  - Customer Name Code (String)
  - Serial # (String)
  - Nature of Work (One time / Monthly / POC)
  - Execution Status (Completed / In Progress / Delayed etc.)
  - Data Delivery Date (Date)
  - Date of PO/LOI (Date)
  - Probable Start Date (Date)
  - Probable End Date (Date)
  - Sector (String)
  - Type of Work (String)
  - Amount in Rupees (Excl of GST) (Masked) (Number)
  - Billed Value in Rupees (Incl of GST.) (Masked) (Number)
  - Collected Amount in Rupees (Incl of GST.) (Masked) (Number)
  - Amount Receivable (Masked) (Number)
  - WO Status (billed) (String)
  - Billing Status (String)
  - Invoice Status (String)
"""

SYSTEM_PROMPT = f"""You are a Business Intelligence AI Agent for Skylark Drones, an Indian drone services company.
You have live data from two monday.com boards — Deals (sales pipeline) and Work Orders (project execution).

{DEALS_SCHEMA}
{WORK_ORDERS_SCHEMA}

HOW TO RESPOND:
- **Max 200 words total. Never exceed.**
- Always include a markdown TABLE with the key numbers.
- After the table, write 2–4 sentences explaining what the numbers mean and one insight/action.
- Start directly with the table or a one-line headline. No filler like "Sure!" or "Great question!".
- Money always in ₹ Lakhs (L) or Crores (Cr). Example: ₹4.5 Cr.
- If the question is ambiguous (missing sector or time period), ask ONE specific clarifying question — no table needed.
- Always base answers on the DATA below. Never invent numbers.

DATA:
{{data_context}}
"""

async def call_groq(api_key: str, messages: list) -> Optional[str]:
    """Call Groq REST API"""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "qwen/qwen3.6-27b",
        "messages": messages,
        "temperature": 0.2
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            r = await client.post(url, json=payload, headers=headers)
            if r.status_code == 200:
                data = r.json()
                content = data["choices"][0]["message"]["content"]
                import re
                content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
                return content
            else:
                logger.error(f"Groq API error {r.status_code}: {r.text[:200]}")
        except Exception as e:
            logger.error(f"Groq call failed: {e}")
    return None

class BIAgent:
    def __init__(self):
        self.groq_key = os.getenv("GROQ_API_KEY", "")
        self._wo_data = []
        self._deals_data = []
        self._quality = {}
        self._data_context = ""

    def update_data_context(self, work_orders_processed: dict, deals_processed: dict, errors: dict = None):
        self._wo_data = work_orders_processed.get("data", [])
        self._deals_data = deals_processed.get("data", [])
        self._quality = {
            "wo_pct": work_orders_processed.get("completeness_pct", 0),
            "deals_pct": deals_processed.get("completeness_pct", 0),
        }

        # Build compact aggregated summary (not raw rows) to stay under token limits
        try:
            deals_df = pd.DataFrame(self._deals_data)
            wo_df = pd.DataFrame(self._wo_data)

            def find_col(df, keywords):
                for kw in keywords:
                    for col in df.columns:
                        if kw.lower() in col.lower():
                            return col
                return None

            summary = {
                "total_deals": len(deals_df),
                "total_work_orders": len(wo_df),
            }

            # Deals aggregations
            if not deals_df.empty:
                status_col = find_col(deals_df, ["deal_status", "status"])
                stage_col = find_col(deals_df, ["deal_stage", "stage"])
                sector_col = find_col(deals_df, ["sector/service", "sector"])
                val_col = find_col(deals_df, ["masked_deal_value", "deal_value", "value"])
                prob_col = find_col(deals_df, ["closure_probability", "probability"])

                if status_col:
                    summary["deals_by_status"] = deals_df[status_col].value_counts().to_dict()
                if stage_col:
                    summary["deals_by_stage"] = deals_df[stage_col].value_counts().to_dict()
                if sector_col:
                    summary["deals_by_sector"] = deals_df[sector_col].value_counts().to_dict()
                    if val_col:
                        deals_df[val_col] = pd.to_numeric(deals_df[val_col], errors='coerce')
                        summary["pipeline_value_by_sector"] = deals_df.groupby(sector_col)[val_col].sum().round(0).to_dict()
                if val_col:
                    deals_df[val_col] = pd.to_numeric(deals_df[val_col], errors='coerce')
                    summary["total_pipeline_value_inr"] = deals_df[val_col].sum()
                    summary["avg_deal_value_inr"] = deals_df[val_col].mean()
                    if status_col:
                        won_mask = deals_df[status_col].astype(str).str.lower().str.contains("won", na=False)
                        summary["won_revenue_inr"] = deals_df.loc[won_mask, val_col].sum()
                if prob_col:
                    summary["deals_by_closure_probability"] = deals_df[prob_col].value_counts().to_dict()

            # Work Orders aggregations
            if not wo_df.empty:
                exec_col = find_col(wo_df, ["execution_status", "status"])
                sector_col = find_col(wo_df, ["sector"])
                now_col = find_col(wo_df, ["nature_of_work", "nature of work"])
                billing_col = find_col(wo_df, ["billing_status", "billing status"])
                amount_col = find_col(wo_df, ["amount_in_rupees_(excl_of_gst)_(masked)", "budget", "amount", "value"])
                lem_col = find_col(wo_df, ["last_executed_month", "last executed month"])
                prob_start_col = find_col(wo_df, ["probable_start_date", "probable start date"])

                if exec_col:
                    summary["wo_by_execution_status"] = wo_df[exec_col].value_counts().to_dict()
                if sector_col:
                    summary["wo_by_sector"] = wo_df[sector_col].value_counts().to_dict()
                if now_col:
                    summary["wo_by_nature_of_work"] = wo_df[now_col].value_counts().to_dict()
                if billing_col:
                    summary["wo_by_billing_status"] = wo_df[billing_col].value_counts().to_dict()
                if amount_col:
                    wo_df[amount_col] = pd.to_numeric(wo_df[amount_col], errors='coerce')
                    summary["total_contract_value_inr"] = wo_df[amount_col].sum()
                if lem_col:
                    summary["last_executed_months"] = wo_df[lem_col].dropna().value_counts().to_dict()
                if prob_start_col:
                    try:
                        dates = pd.to_datetime(wo_df[prob_start_col], errors='coerce').dropna()
                        summary["avg_probable_start_date"] = dates.mean().strftime('%Y-%m-%d')
                        summary["earliest_start_date"] = dates.min().strftime('%Y-%m-%d')
                        summary["latest_start_date"] = dates.max().strftime('%Y-%m-%d')
                    except:
                        pass

            self._data_context = json.dumps(summary, default=str, indent=2)
            logger.info(f"Data context built: ~{len(self._data_context)} chars")

        except Exception as e:
            logger.error(f"Error building data context: {e}")
            self._data_context = json.dumps({"total_deals": len(self._deals_data), "total_work_orders": len(self._wo_data)})

        logger.info(f"Data updated: {len(self._wo_data)} WOs, {len(self._deals_data)} deals")

    async def chat(self, user_message: str, conversation_history: list[dict]) -> str:
        if not self._deals_data and not self._wo_data:
            return "⚠️ **No data loaded.** Please click **Refresh** to fetch data from monday.com."

        if not self.groq_key:
            return "⚠️ **API Key Missing.** Please add your GROQ_API_KEY to the .env file."

        # Build message history for the API
        messages = [{"role": "system", "content": SYSTEM_PROMPT.replace("{data_context}", self._data_context)}]
        for msg in conversation_history[-6:]:
            role = "assistant" if msg.get("role") == "bot" else "user"
            messages.append({"role": role, "content": msg.get("content", "")})
            
        messages.append({"role": "user", "content": user_message})

        logger.info("Calling Groq LLM API...")
        reply = await call_groq(self.groq_key, messages)
        
        if reply:
            return reply
        return "⚠️ I'm sorry, my LLM service experienced an error while generating a response. Please try again."

    def get_data_summary(self) -> dict:
        if not self._wo_data and not self._deals_data:
            return {"status": "no_data"}
        return {
            "status": "loaded",
            "work_orders": {"total": len(self._wo_data), "completeness_pct": self._quality.get("wo_pct", 0)},
            "deals": {"total": len(self._deals_data), "completeness_pct": self._quality.get("deals_pct", 0)},
        }
