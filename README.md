# Skylark Drones — BI Agent

An AI-powered Business Intelligence agent that connects to live monday.com boards and answers founder-level queries about Work Orders and Deals pipeline using natural language.

## Features
- **Live monday.com Integration** — fetches real-time data from Deals and Work Orders boards via GraphQL API
- **LLM-Powered (Groq)** — uses `qwen/qwen3.6-27b` via Groq for dynamic, conversational answers
- **Data Resilience** — normalizes messy dates, currency, and missing fields; demo data fallback if API is down
- **Clarifying Questions** — asks for more detail when a query is ambiguous
- **Leadership Updates** — KPI table + risk highlights from live data
- **Chat UI** — React frontend with markdown rendering, table highlighting, and typing indicator

## Architecture
```
frontend/          React 18 + Vite + Tailwind CSS
backend/
  main.py          FastAPI app — /chat, /refresh, /health endpoints
  ai_agent.py      Groq LLM integration + data context builder
  monday_client.py GraphQL client for monday.com API
  data_processor.py Data cleaning and normalization
  demo_data.py     Fallback data if monday.com is unreachable
```

## Local Setup

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.example .env         # Fill in your keys
python main.py
# Runs on http://localhost:8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:5173
```

### Environment Variables (backend/.env)
```
MONDAY_API_KEY=eyJ...
WORK_ORDERS_BOARD_ID=123456789
DEALS_BOARD_ID=987654321
GROQ_API_KEY=gsk_...
```

## Deployment

### Backend → Render.com
1. Push repo to GitHub
2. Go to [render.com](https://render.com) → New Web Service → Connect GitHub repo
3. Render auto-detects `render.yaml` and configures the FastAPI service
4. Add environment variables in Render dashboard (same 4 keys above)
5. Copy the Render URL (e.g. `https://skylark-bi-backend.onrender.com`)

### Frontend → Vercel
1. Go to [vercel.com](https://vercel.com) → New Project → Connect GitHub repo
2. Set **Root Directory** to `frontend`
3. Add environment variable: `VITE_API_URL` = your Render backend URL
4. Click Deploy — Vercel gives you a public URL to submit

## Submission
- **Hosted Prototype:** *(your Vercel URL after deployment)*
- **Source Code ZIP:** generate with `python -c "import shutil; shutil.make_archive('Skylark_BI_Agent', 'zip', '.')"`
- **Form:** https://forms.gle/9wFwL5mdFbTXQtqq7
