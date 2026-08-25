"""
Data Processor: Cleans and normalizes raw monday.com board data
Handles messy real-world data: null values, inconsistent formats, etc.
"""

import re
import logging
from datetime import datetime
from typing import Any, Optional
import json

logger = logging.getLogger(__name__)

# Common date formats encountered in real-world data
DATE_FORMATS = [
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%m/%d/%Y",
    "%d-%m-%Y",
    "%B %d, %Y",
    "%b %d, %Y",
    "%d %B %Y",
    "%Y/%m/%d",
    "%d.%m.%Y",
]


def parse_date(raw: Any) -> Optional[str]:
    """Try multiple date formats and return ISO string or None"""
    if not raw:
        return None
    raw_str = str(raw).strip()
    if not raw_str or raw_str.lower() in ("none", "null", "n/a", "-", ""):
        return None

    # Try direct ISO parse from monday value JSON
    try:
        val = json.loads(raw_str)
        if isinstance(val, dict) and "date" in val:
            return val["date"]
    except Exception:
        pass

    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(raw_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    logger.debug(f"Could not parse date: {raw_str}")
    return raw_str  # Return as-is if can't parse


def parse_number(raw: Any) -> Optional[float]:
    """Extract numeric value from potentially messy string"""
    if raw is None:
        return None
    raw_str = str(raw).strip()
    if not raw_str or raw_str.lower() in ("none", "null", "n/a", "-", ""):
        return None
    # Remove currency symbols, commas, spaces
    cleaned = re.sub(r"[₹$€£,\s%]", "", raw_str)
    # Remove trailing/leading non-numeric chars
    cleaned = re.sub(r"[^\d.\-]", "", cleaned)
    try:
        return float(cleaned) if cleaned else None
    except ValueError:
        return None


def normalize_text(raw: Any) -> Optional[str]:
    """Normalize text: strip whitespace, handle nulls"""
    if raw is None:
        return None
    val = str(raw).strip()
    if val.lower() in ("none", "null", "n/a", "-", ""):
        return None
    return val


def normalize_status(raw: Any) -> Optional[str]:
    """Normalize status fields to consistent casing"""
    text = normalize_text(raw)
    if not text:
        return None
    # Parse monday.com status JSON
    try:
        val = json.loads(text)
        if isinstance(val, dict):
            return val.get("label") or val.get("text") or text
    except Exception:
        pass
    return text.title()


def extract_column_value(col: dict) -> Any:
    """
    Extract the human-readable value from a monday.com column_value object.
    Handles all common column types.
    """
    col_type = col.get("column", {}).get("type", "")
    text_val = col.get("text", "") or ""
    raw_value = col.get("value", "") or ""

    # Numbers, money, ratings
    if col_type in ("numbers", "numeric", "rating"):
        return parse_number(text_val or raw_value)

    # Date columns
    if col_type in ("date", "timeline"):
        return parse_date(raw_value or text_val)

    # Status/dropdown
    if col_type in ("color", "status", "dropdown", "multiple-person"):
        return normalize_status(text_val or raw_value)

    # Person column
    if col_type == "multiple-person":
        try:
            parsed = json.loads(raw_value)
            if isinstance(parsed, dict) and "personsAndTeams" in parsed:
                return ", ".join(
                    str(p.get("name", "")) for p in parsed["personsAndTeams"] if p.get("name")
                )
        except Exception:
            pass

    # Default: return normalized text
    return normalize_text(text_val) if text_val else normalize_text(raw_value)


def flatten_item(item: dict) -> dict:
    """Convert a monday.com item with column_values into a flat dictionary"""
    flat = {
        "id": item.get("id"),
        "name": normalize_text(item.get("name")),
        "created_at": parse_date(item.get("created_at", "")[:10] if item.get("created_at") else None),
        "updated_at": parse_date(item.get("updated_at", "")[:10] if item.get("updated_at") else None),
    }

    for col in item.get("column_values", []):
        col_title = col.get("column", {}).get("title", col.get("id", "unknown"))
        # Sanitize key: lowercase, replace spaces/special chars with underscore
        key = re.sub(r"[^a-z0-9_]", "_", col_title.lower().strip())
        flat[key] = extract_column_value(col)

    return flat


def process_work_orders(raw_items: list[dict]) -> dict:
    """Process and clean work order items, returning structured data + quality report"""
    processed = []
    issues = []

    for item in raw_items:
        flat = flatten_item(item)
        row_issues = []

        # Check for critical missing fields
        if not flat.get("name"):
            row_issues.append("Missing item name")

        # Try to identify budget/cost columns
        amount_keys = [k for k in flat if any(kw in k for kw in ["budget", "cost", "amount", "value", "revenue"])]
        for k in amount_keys:
            if flat.get(k) is None:
                row_issues.append(f"Missing value in '{k}'")

        if row_issues:
            issues.append({"id": flat.get("id"), "name": flat.get("name"), "issues": row_issues})

        processed.append(flat)

    return {
        "data": processed,
        "total": len(processed),
        "quality_issues": issues,
        "completeness_pct": round((1 - len(issues) / max(len(processed), 1)) * 100, 1),
    }


def process_deals(raw_items: list[dict]) -> dict:
    """Process and clean deal items, returning structured data + quality report"""
    processed = []
    issues = []

    for item in raw_items:
        flat = flatten_item(item)
        row_issues = []

        if not flat.get("name"):
            row_issues.append("Missing deal name")

        # Check common deal fields
        value_keys = [k for k in flat if any(kw in k for kw in ["value", "amount", "revenue", "deal", "price"])]
        for k in value_keys:
            if flat.get(k) is None:
                row_issues.append(f"Missing value in '{k}'")

        if row_issues:
            issues.append({"id": flat.get("id"), "name": flat.get("name"), "issues": row_issues})

        processed.append(flat)

    return {
        "data": processed,
        "total": len(processed),
        "quality_issues": issues,
        "completeness_pct": round((1 - len(issues) / max(len(processed), 1)) * 100, 1),
    }


def summarize_dataset(processed: dict, board_name: str) -> str:
    """Generate a human-readable data summary for the AI agent"""
    data = processed["data"]
    if not data:
        return f"No data found in {board_name}."

    columns = list(data[0].keys()) if data else []
    lines = [
        f"**{board_name}**: {processed['total']} records",
        f"Columns: {', '.join(columns)}",
        f"Data completeness: {processed['completeness_pct']}%",
    ]
    if processed["quality_issues"]:
        lines.append(f"⚠️ {len(processed['quality_issues'])} records with missing/incomplete fields")

    return "\n".join(lines)
