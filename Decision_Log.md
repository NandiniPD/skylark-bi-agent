# Skylark Drones BI Agent - Decision Log

## 1. Key Assumptions Made
* **Data Structure:** I assumed that the provided CSVs would be imported into monday.com directly without heavy schema alterations. The agent dynamically fetches column structures but relies on semantic keywords (e.g., "Amount", "Status", "Sector") to identify key data points.
* **API Access:** I assumed a read-only scope for the monday.com API is sufficient since a BI agent primarily aggregates and reports data rather than modifying it.
* **Data Volume:** For this prototype, I assumed board sizes would remain within the API pagination limits (a few hundred items) which allows for in-memory context building.

## 2. Trade-offs Chosen and Why
* **In-Memory Pandas + Gemini vs. Vector Database (RAG):**
  * *Why:* Given the dataset size (a few hundred rows) and the 6-hour limit, setting up a complex Vector DB (like Pinecone) would be over-engineering. Injecting structured JSON into the Gemini context window paired with a fallback pandas analytical engine provides fast, accurate, and deterministic results for financial math.
* **Manual Data Refresh vs. Webhooks:**
  * *Why:* The agent uses a "Refresh Data" mechanism rather than live webhooks to avoid rate limits and reduce the complexity of state management for a prototype.
* **REST API over Monday.com MCP (Model Context Protocol):**
  * *Why:* A custom FastAPI backend interacting with monday.com via GraphQL provides more granular control over data normalization and formatting before passing it to the LLM. 

## 3. What I'd Do Differently With More Time
* **Persistent Storage & Caching:** Implement a Redis cache or a lightweight PostgreSQL database to store synced board data, reducing API calls and improving load times.
* **Streaming Responses:** Implement Server-Sent Events (SSE) to stream the LLM response to the frontend, improving perceived latency.
* **Dynamic Charting:** Send structured JSON from the LLM to the frontend to render dynamic Recharts (graphs/charts) rather than just markdown text.

## 4. Interpretation of "Leadership Updates"
I interpreted "Leadership Updates" as an **Executive Briefing**. Founders don't want raw rows; they want:
1. **Pipeline Health:** Total value, deals won, conversion rates.
2. **Operational Execution:** Number of active work orders, completed work orders.
3. **Risks & Bottlenecks:** specifically highlighting Accounts Receivable (AR) that needs collection and delayed work orders.
The agent uses a dedicated "leadership_update" intent to aggregate these specific KPIs across both the Deals and Work Orders boards into a concise Markdown table and bulleted risk list.
