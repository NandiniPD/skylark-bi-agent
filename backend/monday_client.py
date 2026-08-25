"""
Monday.com GraphQL API Client
Handles all monday.com data fetching with retry logic and error handling
"""

import os
import httpx
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)

MONDAY_API_URL = "https://api.monday.com/v2"


class MondayClient:
    def __init__(self):
        self.api_key = os.getenv("MONDAY_API_KEY", "")
        self.work_orders_board_id = os.getenv("WORK_ORDERS_BOARD_ID", "")
        self.deals_board_id = os.getenv("DEALS_BOARD_ID", "")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _query(self, query: str, variables: Optional[dict] = None) -> dict:
        """Execute a GraphQL query against monday.com API"""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                MONDAY_API_URL,
                json=payload,
                headers=self.headers,
            )
            response.raise_for_status()
            data = response.json()

            if "errors" in data:
                logger.error(f"Monday API errors: {data['errors']}")
                raise Exception(f"Monday API error: {data['errors'][0].get('message', 'Unknown error')}")

            return data.get("data", {})

    async def get_board_items(self, board_id: str, limit: int = 500) -> list[dict]:
        """Fetch all items from a monday.com board with pagination"""
        all_items = []
        cursor = None

        while True:
            if cursor:
                query = """
                query($boardId: ID!, $limit: Int!, $cursor: String!) {
                    boards(ids: [$boardId]) {
                        items_page(limit: $limit, cursor: $cursor) {
                            cursor
                            items {
                                id
                                name
                                created_at
                                updated_at
                                column_values {
                                    id
                                    column { title type }
                                    text
                                    value
                                }
                            }
                        }
                    }
                }
                """
                variables = {"boardId": board_id, "limit": limit, "cursor": cursor}
            else:
                query = """
                query($boardId: ID!, $limit: Int!) {
                    boards(ids: [$boardId]) {
                        items_page(limit: $limit) {
                            cursor
                            items {
                                id
                                name
                                created_at
                                updated_at
                                column_values {
                                    id
                                    column { title type }
                                    text
                                    value
                                }
                            }
                        }
                    }
                }
                """
                variables = {"boardId": board_id, "limit": limit}

            data = await self._query(query, variables)
            boards = data.get("boards", [])
            if not boards:
                break

            items_page = boards[0].get("items_page", {})
            items = items_page.get("items", [])
            all_items.extend(items)

            cursor = items_page.get("cursor")
            if not cursor or len(items) < limit:
                break

        return all_items

    async def get_board_info(self, board_id: str) -> dict:
        """Fetch board metadata and column definitions"""
        query = """
        query($boardId: ID!) {
            boards(ids: [$boardId]) {
                id
                name
                description
                columns {
                    id
                    title
                    type
                }
            }
        }
        """
        data = await self._query(query, {"boardId": board_id})
        boards = data.get("boards", [])
        return boards[0] if boards else {}

    async def get_work_orders(self) -> list[dict]:
        """Fetch all work orders from the Work Orders board"""
        return await self.get_board_items(self.work_orders_board_id)

    async def get_deals(self) -> list[dict]:
        """Fetch all deals from the Deals board"""
        return await self.get_board_items(self.deals_board_id)

    async def get_all_data(self) -> dict:
        """Fetch data from both boards concurrently"""
        work_orders_task = self.get_work_orders()
        deals_task = self.get_deals()
        work_orders, deals = await asyncio.gather(work_orders_task, deals_task, return_exceptions=True)

        result = {}
        if isinstance(work_orders, Exception):
            logger.error(f"Failed to fetch work orders: {work_orders}")
            result["work_orders"] = []
            result["work_orders_error"] = str(work_orders)
        else:
            result["work_orders"] = work_orders

        if isinstance(deals, Exception):
            logger.error(f"Failed to fetch deals: {deals}")
            result["deals"] = []
            result["deals_error"] = str(deals)
        else:
            result["deals"] = deals

        return result

    def is_configured(self) -> bool:
        """Check if required environment variables are set"""
        return bool(self.api_key and self.work_orders_board_id and self.deals_board_id)
