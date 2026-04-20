# DataLens AI — Conversational Business Intelligence

<p align="center">
  <img src="https://img.shields.io/badge/Status-Production Ready-brightgreen" alt="Status">
  <img src="https://img.shields.io/badge/Stack-FastAPI%20%2B%20Next.js-blue" alt="Stack">
  <img src="https://img.shields.io/badge/License-MIT-orange" alt="License">
</p>

> **Note:** This is the production-ready rewrite of the original CSV-analysis-agent project. See [Legacy Files](#legacy-files) for the old code.

---

## Overview

**DataLens AI** lets any team member upload their CSV/XLSX exports and have a natural language conversation with their data — no code, no SQL, no data analyst required.

### Features

- 🔐 **Authentication** — Secure JWT-based user registration and login
- 📁 **File Upload** — Drag & drop CSV/XLSX files with GCS storage
- 💬 **Natural Language Queries** — Ask questions in plain English
- 🧠 **AI-Powered Analysis** — LangChain agent with Groq LLM
- 📊 **Session Management** — Multiple analysis sessions with chat history
- ⚡ **Streaming Responses** — Real-time AI responses
- 🔒 **Production-Ready** — PostgreSQL, Redis rate limiting, secure auth

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14 + TypeScript + TailwindCSS |
| Backend | FastAPI (Python 3.11) |
| Database | PostgreSQL (asyncpg) |
| Auth | JWT (authlib) + bcrypt |
| Cache/Rate Limit | Redis |
| AI | LangChain + Groq (llama-3.1-70b) |
| File Storage | GCP Cloud Storage |

---

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/RYUKxAYU/CSV-analysis-agent-.git
cd CSV-analysis-agent-
```

### 2. Start Local Infrastructure

```bash
docker compose up -d
```

This starts PostgreSQL (port 5432) and Redis (port 6379).

### 3. Backend Setup

```bash
cd backend
cp .env.example .env
# Edit .env with your settings

pip install -r requirements.txt

# Run migrations
psql $DATABASE_URL < migrations/001_create_users.sql
psql $DATABASE_URL < migrations/002_create_files.sql
psql $DATABASE_URL < migrations/003_create_sessions.sql

# Start backend
uvicorn api.main:app --reload
```

### 4. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000`

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | ❌ | Create account |
| POST | `/auth/login` | ❌ | Login, returns JWT |
| POST | `/upload/` | ✅ | Upload CSV → returns `file_id` |
| GET | `/sessions/` | ✅ | List user's sessions |
| POST | `/sessions/` | ✅ | Create new session |
| DELETE | `/sessions/{id}` | ✅ | Delete session |
| POST | `/ask/` | ✅ | Query AI agent |
| POST | `/ask/stream` | ✅ | Query with streaming |
| GET | `/health` | ❌ | Health check |

---

## Environment Variables

```bash
# Backend (.env)
DATABASE_URL=postgresql://user:pass@localhost:5432/datalens
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-secret-key-min-32-chars
GROQ_API_KEY=your-groq-api-key

# Optional: GCP Cloud Storage
GCP_PROJECT_ID=your-project
GCS_BUCKET_NAME=your-bucket
GCP_SERVICE_ACCOUNT_JSON={"type":"service_account",...}
```

---

## Deployment

### Backend (Render)

1. Connect GitHub repo to Render
2. Set environment variables
3. Build: `pip install -r backend/requirements.txt`
4. Start: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

### Frontend (Vercel)

1. Connect GitHub repo to Vercel
2. Set `NEXT_PUBLIC_API_URL` to your backend URL
3. Deploy automatically

---

## Project Structure

```
datalens-ai/
├── backend/                    # FastAPI backend
│   ├── api/
│   │   ├── main.py            # App entry, CORS, lifespan
│   │   ├── dependencies.py    # JWT auth middleware
│   │   └── routes/
│   │       ├── auth.py        # /auth/* endpoints
│   │       ├── upload.py      # /upload endpoint
│   │       ├── sessions.py    # /sessions CRUD
│   │       └── ask.py         # /ask agent endpoint
│   ├── agent/
│   │   ├── agent.py           # LangChain agent builder
│   │   ├── tools.py           # CSV analysis tools
│   │   └── file_context.py    # File ID → DataFrame
│   ├── db/
│   │   ├── connection.py      # asyncpg pool
│   │   └── queries/           # SQL queries
│   ├── core/
│   │   ├── config.py          # Settings
│   │   ├── security.py        # JWT + bcrypt
│   │   ├── gcs.py             # GCP Storage
│   │   └── rate_limit.py      # Redis rate limiter
│   ├── migrations/            # SQL schemas
│   └── requirements.txt
├── frontend/                   # Next.js 14 frontend
│   ├── app/
│   │   ├── login/             # Login page
│   │   ├── register/          # Register page
│   │   └── dashboard/         # Main app
│   ├── components/            # UI components
│   └── lib/                   # API client
├── docker-compose.yml         # Local dev infra
├── Dockerfile                 # Container image
└── README.md
```

---

## Legacy Files

> These files are from the original MVP and are kept for reference. They are not part of the new production codebase.

| File | Description |
|------|-------------|
| `app.py` | Original Streamlit frontend (legacy) |
| `index.html` | Static HTML frontend (temporary) |
| `agent.py` | Original LangChain agent (replaced by `backend/agent/`) |
| `tools.py` | Original tools (replaced by `backend/agent/tools.py`) |
| `main.py` | Original FastAPI (replaced by `backend/api/main.py`) |
| `api/index.py` | Vercel serverless function (not used in new architecture) |
| `vercel.py` | Vercel ASGI handler (not used) |
| `vercel.json` | Old Vercel config (deprecated) |
| `requirements.txt` | Root requirements (use `backend/requirements.txt`) |
| `docker.yaml`, `compose.yaml` | Old Docker configs (use `docker-compose.yml`) |
| `pyproject.toml` | Old Python project config |

The new architecture uses `/backend` and `/frontend` directories with proper monorepo structure.

---

## License

MIT