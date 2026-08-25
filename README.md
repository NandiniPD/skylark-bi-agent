# Skylark Drones — BI Agent

An AI-powered Business Intelligence agent that connects to live monday.com boards and answers founder-level business queries using natural language. Built for the Skylark Drones Technical Assignment.

---

## What It Does

Founders can ask plain English questions like:
- *"How's our pipeline looking?"*
- *"Which sector has the highest deal value?"*
- *"Give me a leadership update"*
- *"Which work orders are not started?"*
- *"What is the average probable start date?"*

The agent fetches live data from monday.com, aggregates it, and passes it to an LLM (Groq) to generate a conversational, insightful answer — with a table + explanation, under 200 words.

---

## Architecture

```
frontend/                   React 18 + Vite + Tailwind CSS
│   src/
│   ├── App.jsx             Root app with health check banner
│   ├── api.js              Fetch wrappers for /chat, /refresh, /health
│   ├── components/
│   │   ├── ChatInterface.jsx   Full chat UI with suggested queries
│   │   └── Message.jsx         Markdown rendering with table + bullet styles
│   └── index.css           Custom prose-chat CSS for proper table/list rendering

backend/
│   main.py                 FastAPI — /chat, /refresh, /health, /data/summary
│   ai_agent.py             Groq LLM integration + pandas data aggregation
│   monday_client.py        GraphQL client for monday.com API (pagination + retry)
│   data_processor.py       Cleans messy data (dates, currency, nulls, status JSON)
│   demo_data.py            Fallback sample data if monday.com is unreachable
│   requirements.txt
│   .env.example
```

---

## Tech Stack & Why

| Component | Choice | Reason |
|-----------|--------|--------|
| LLM | **Groq** (`qwen/qwen3.6-27b`) | Free tier, fast inference, no billing setup needed |
| Backend | **FastAPI** (Python) | Async, lightweight, easy to deploy |
| Data layer | **Pandas** | Pre-aggregates board data into compact stats before sending to LLM — avoids token limits |
| Frontend | **React + Vite + Tailwind** | Fast dev setup, clean chat UI |
| monday.com | **GraphQL REST API** | Full control over pagination and field selection |
| Deployment | **Render** (backend) + **Vercel** (frontend) | Free tier, Git-connected, zero-config |

---

## How the LLM Works

1. On startup, the backend fetches all rows from both monday.com boards
2. `ai_agent.py` **pre-aggregates** the data into compact JSON stats (deals by sector, work orders by status, avg dates, totals etc.) — this keeps the LLM prompt well under Groq's token limit
3. Every chat message sends the system prompt (with schema + data summary) + last 6 messages of history to Groq
4. The LLM returns a markdown response (table + 2–4 sentences explanation, max 200 words)
5. The frontend renders markdown with proper table highlighting and bullet points

---

## Local Setup

### 1. Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# or: source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
cp .env.example .env           # then fill in your keys
python main.py
# API running at http://localhost:8000
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
# UI running at http://localhost:5173
```

### 3. Environment Variables (`backend/.env`)
```env
MONDAY_API_KEY=eyJ...          # From monday.com > Developer > API Tokens
WORK_ORDERS_BOARD_ID=123456    # Board ID from monday.com board URL
DEALS_BOARD_ID=987654          # Board ID from monday.com board URL
GROQ_API_KEY=gsk_...           # From console.groq.com/keys
```

---

## Deployment

### Backend → Render.com
1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → **New Web Service** → connect GitHub repo
3. Render auto-detects `render.yaml` — no manual config needed
4. Add your 4 environment variables in the Render dashboard
5. Copy the Render public URL (e.g. `https://skylark-bi-backend.onrender.com`)

### Frontend → Vercel
1. Go to [vercel.com](https://vercel.com) → **New Project** → connect GitHub repo
2. Set **Root Directory** to `frontend`
3. Add environment variable: `VITE_API_URL` = your Render backend URL
4. Click Deploy → Vercel gives you a live public URL

---

## Data Resilience

- **Null / missing values** — handled gracefully with `pd.to_numeric(..., errors='coerce')` and `.dropna()`
- **Inconsistent date formats** — normalized with `pd.to_datetime(..., errors='coerce')`
- **Messy status fields** — lowercased and fuzzy-matched
- **monday.com API down** — app falls back to `demo_data.py` automatically
- **LLM token limits** — raw rows are never sent; only pre-aggregated stats are passed (keeps prompt ~2k tokens vs 77k+)

---

## Assignment Requirements Checklist

| Requirement | Status |
|-------------|--------|
| monday.com API integration | ✅ Live GraphQL fetch |
| Handle missing/null data | ✅ pandas cleaning + graceful fallback |
| Interpret founder-level questions | ✅ Groq LLM |
| Clarifying questions for ambiguous queries | ✅ LLM-driven |
| Revenue, pipeline, sector, ops queries | ✅ All covered via data aggregation |
| Leadership update | ✅ KPI table + risks |
| Hosted prototype | ✅ Render + Vercel |
| Decision Log | ✅ `Decision_Log.md` |
| Source code ZIP | ✅ Available |

---

## Submission
- **Submission Form:** https://forms.gle/9wFwL5mdFbTXQtqq7
