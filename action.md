# action.md — Production Upgrade Plan: CSV AI Agent → DataLens AI

> **Mindset**: Think like a startup CTO + hiring manager. Every decision here is portfolio-worthy, scalable, and solves a real problem.

---

## 1. Real-World Use Case

### Project Name: **DataLens AI — Conversational Business Intelligence for Non-Technical Teams**

### Problem Statement

Small-to-medium businesses drown in CSV exports from tools like Shopify, Google Ads, QuickBooks, HubSpot, and Stripe. Their marketing managers, operations leads, and finance teams can't write SQL or Python — but they need answers *right now*. Hiring a data analyst for every ad-hoc question isn't viable.

**DataLens AI** lets any team member upload their CSV/XLSX exports and have a natural language conversation with their data — no code, no SQL, no data analyst required.

### Target Users

- **Marketing managers** — analyzing ad performance CSVs from Meta/Google
- **E-commerce operators** — querying Shopify sales exports
- **Finance analysts** — reviewing expense reports and budget sheets
- **Operations teams** — tracking logistics and inventory CSVs

### Why It Matters (For Your Portfolio)

- Demonstrates end-to-end AI product thinking (not just a chatbot wrapper)
- Shows you understand real enterprise pain points
- Combines RAG, agentic design, auth, and production infra in one project
- Interviewers at AI/ML and full-stack companies will immediately understand the value

---

## 2. Architecture Upgrade

### High-Level System Design

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js)                    │
│  Drag-drop Upload │ Chat UI │ Column Preview │ Chart Output  │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTPS / WebSocket
┌──────────────────────────▼──────────────────────────────────┐
│                    API GATEWAY (FastAPI)                      │
│   /auth  /upload  /ask  /sessions  /history  /export         │
│            JWT Middleware │ Rate Limiter (Redis)              │
└───────┬──────────────────┬──────────────────────────────────┘
        │                  │
┌───────▼──────┐   ┌───────▼────────────────────────────┐
│  PostgreSQL  │   │          AI AGENT LAYER              │
│  Users       │   │  LangChain Agent + Tool Calling      │
│  Sessions    │   │  File Context Manager                │
│  File Meta   │   │  Groq LLM (llama3-70b)              │
│  Chat History│   │  pandas_agent / custom tools         │
└──────────────┘   └───────┬────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
     ┌────────▼────────┐    ┌──────────▼──────────┐
     │  GCP Cloud       │    │   Redis Cache        │
     │  Storage (GCS)   │    │   Rate limits        │
     │  CSV files       │    │   Session data       │
     │  Signed URLs     │    └─────────────────────┘
     └─────────────────┘
```

### Stack Decisions

| Layer | Tech | Reason |
|-------|------|--------|
| Frontend | Next.js 14 + TypeScript + TailwindCSS | SSR, type safety, modern DX |
| Backend | FastAPI (Python 3.11) | Async, fast, auto OpenAPI docs |
| Database | **PostgreSQL** (via asyncpg) | Production-grade, relational, no ORM |
| Auth | JWT (**authlib**) + bcrypt | Actively maintained, python-jose is discontinued |
| Cache / Rate Limit | Redis (upstash free tier) | Fast, serverless-friendly |
| AI / Agent | LangChain + Groq (llama3-70b-8192) | Fast inference, free tier |
| File Storage | **GCP Cloud Storage** (GCS) | Scalable, durable, signed URLs, free 5GB tier |
| Deployment | Render (backend) + Vercel (frontend) | Free tiers, CI/CD ready |

> ❌ No SQLite. ❌ No SQLAlchemy. ✅ Raw asyncpg queries.

---

## 3. Step-by-Step Development Plan

---

### Phase 1: Planning & Setup (Day 1–2)

**Goals**: Repository structure, environment setup, database schema design

**Deliverables**:
- Monorepo scaffold (`/backend`, `/frontend`)
- `.env.example` with all required keys documented
- PostgreSQL schema finalized
- README updated with architecture diagram

**Tools**: Git, Docker Compose (local Postgres + Redis), VS Code

---

### Phase 2: Backend Development (Day 3–6)

**Goals**: Auth system, file upload endpoint, session management

**Deliverables**:
- `POST /auth/register` — register with email + password
- `POST /auth/login` — returns JWT access token
- `POST /upload` — accepts multipart CSV, stores file, returns `file_id`
- `GET /sessions` — list user's analysis sessions
- JWT middleware protecting all non-auth routes
- Rate limiter middleware (10 req/min per user)

**Tools**: FastAPI, asyncpg, **authlib**, bcrypt, redis-py, aiofiles, google-cloud-storage

---

### Phase 3: Database Integration (Day 7–9)

**Goals**: Connect all endpoints to PostgreSQL using raw asyncpg

**Deliverables**:
- Async database connection pool initialized at startup
- All CRUD operations implemented (no ORM)
- Migration scripts (plain `.sql` files in `/migrations`)
- DB health check endpoint

**Tools**: asyncpg, PostgreSQL 15 (Docker local, Supabase/Neon for prod)

---

### Phase 4: Frontend Development (Day 10–14)

**Goals**: Polished Next.js UI with drag-and-drop upload, chat interface, column preview

**Deliverables**:
- `/login` and `/register` pages with JWT token storage (httpOnly cookie)
- `/dashboard` — upload zone, session list
- `/session/[id]` — chat interface + data preview panel
- No manual file path input — ever
- Responsive design (mobile + desktop)

**Tools**: Next.js 14, TailwindCSS, shadcn/ui, react-dropzone, axios

---

### Phase 5: AI / Agent Integration (Day 15–18)

**Goals**: Fix the core agent bug, integrate tool calling, maintain file context

**Deliverables**:
- Agent receives `file_id`, loads data into pandas DataFrame internally
- Custom LangChain tools: `read_csv`, `describe_data`, `filter_rows`, `compute_stats`, `generate_chart_data`
- Conversational memory per session (last 10 messages)
- Agent never asks for file path — it always knows the context
- Streaming responses via SSE (Server-Sent Events)

**Tools**: LangChain, Groq, pandas, matplotlib (for chart base64 output)

---

### Phase 6: Testing & Deployment (Day 19–22)

**Goals**: End-to-end tests, CI/CD, live deployment

**Deliverables**:
- Pytest test suite for all API endpoints
- GitHub Actions CI: lint + test on every push
- Backend live on Render, Frontend live on Vercel
- Environment secrets configured in both platforms
- Live demo URL in README

**Tools**: pytest, httpx (async test client), GitHub Actions, Render, Vercel

---

## 4. Implementation Guide

### Folder Structure

```
datalens-ai/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI app init, lifespan, CORS
│   │   ├── dependencies.py       # get_current_user(), get_db()
│   │   └── routes/
│   │       ├── auth.py           # /auth/register, /auth/login
│   │       ├── upload.py         # /upload (multipart file)
│   │       ├── sessions.py       # /sessions CRUD
│   │       └── ask.py            # /ask (agent query + streaming)
│   ├── agent/
│   │   ├── agent.py              # LangChain agent builder
│   │   ├── tools.py              # Custom CSV tools
│   │   ├── memory.py             # Per-session conversation memory
│   │   └── file_context.py       # File ID → DataFrame resolver
│   ├── db/
│   │   ├── connection.py         # asyncpg pool setup
│   │   └── queries/
│   │       ├── users.py
│   │       ├── sessions.py
│   │       └── files.py
│   ├── core/
│   │   ├── config.py             # Settings from env vars
│   │   ├── security.py           # JWT (authlib) encode/decode, bcrypt, magic bytes
│   │   ├── gcs.py                # GCP Cloud Storage upload/download/signed URLs
│   │   └── rate_limit.py         # Redis rate limiter middleware
│   ├── migrations/
│   │   ├── 001_create_users.sql
│   │   ├── 002_create_files.sql
│   │   └── 003_create_sessions.sql
│   ├── tests/
│   │   ├── test_auth.py
│   │   ├── test_upload.py
│   │   └── test_ask.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/page.tsx
│   │   │   └── register/page.tsx
│   │   ├── dashboard/page.tsx
│   │   └── session/[id]/page.tsx
│   ├── components/
│   │   ├── UploadZone.tsx         # Drag-and-drop, no path input
│   │   ├── ChatWindow.tsx         # Message bubbles + streaming
│   │   ├── DataPreview.tsx        # Column names + sample rows
│   │   └── ChartOutput.tsx        # Renders base64 chart images
│   ├── lib/
│   │   ├── api.ts                 # Axios instance with auth header
│   │   └── hooks/
│   │       ├── useSession.ts
│   │       └── useUpload.ts
│   ├── next.config.js
│   └── tailwind.config.ts
├── docker-compose.yml             # Local Postgres + Redis
└── README.md
```

### requirements.txt (key packages)

```txt
fastapi>=0.111.0
uvicorn[standard]>=0.29.0
asyncpg>=0.29.0
authlib>=1.3.0          # JWT — replaces discontinued python-jose
bcrypt>=4.1.0
python-multipart>=0.0.9
redis>=5.0.0
google-cloud-storage>=2.16.0  # GCP Cloud Storage
python-magic>=0.4.27    # file type validation via magic bytes
langchain>=0.2.0
langchain-groq>=0.1.0
pandas>=2.2.0
openpyxl>=3.1.0         # XLSX support for pandas
httpx>=0.27.0           # async HTTP (for tests)
pytest>=8.0.0
pytest-asyncio>=0.23.0
pydantic-settings>=2.2.0
```

---

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| POST | `/auth/register` | ❌ | Create account |
| POST | `/auth/login` | ❌ | Returns JWT token |
| POST | `/upload` | ✅ | Upload CSV → returns `file_id` |
| GET | `/sessions` | ✅ | List user's sessions |
| POST | `/sessions` | ✅ | Create new session with `file_id` |
| DELETE | `/sessions/{id}` | ✅ | Delete session + file |
| POST | `/ask` | ✅ | Query agent with `session_id` + `message` |
| GET | `/history/{session_id}` | ✅ | Get chat history |
| GET | `/health` | ❌ | Health check |

---

### Database Schema (PostgreSQL — raw SQL)

```sql
-- migrations/001_create_users.sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- migrations/002_create_files.sql
CREATE TABLE uploaded_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    original_name VARCHAR(255) NOT NULL,
    storage_path TEXT NOT NULL,       -- local path or cloud URL
    row_count INTEGER,
    column_names JSONB,               -- ["col1", "col2", ...]
    file_size_bytes BIGINT,
    uploaded_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '24 hours'
);

-- migrations/003_create_sessions.sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    file_id UUID REFERENCES uploaded_files(id) ON DELETE SET NULL,
    title VARCHAR(255),               -- auto-generated from first query
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_active_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    role VARCHAR(10) NOT NULL,        -- 'user' or 'assistant'
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

### Key File: Agent with File Context Fix

```python
# backend/agent/file_context.py

import pandas as pd
import io
from db.queries.files import get_file_by_id
from core.gcs import download_from_gcs

# In-memory cache: file_id → DataFrame (lives for process lifetime)
_df_cache: dict[str, pd.DataFrame] = {}

async def get_dataframe(file_id: str) -> pd.DataFrame:
    """Resolve file_id → download from GCS → return DataFrame. Cached after first load."""
    if file_id in _df_cache:
        return _df_cache[file_id]

    file_record = await get_file_by_id(file_id)
    if not file_record:
        raise FileNotFoundError(f"No file found for id: {file_id}")

    # Download CSV bytes from GCS
    content_bytes = await download_from_gcs(file_record["gcs_object_name"])
    df = pd.read_csv(io.BytesIO(content_bytes))
    _df_cache[file_id] = df
    return df

def evict_cache(file_id: str):
    """Call this when a session/file is deleted."""
    _df_cache.pop(file_id, None)
```

```python
# backend/agent/tools.py

from langchain.tools import tool
from agent.file_context import get_dataframe

# Tools receive file_id — NEVER a file path from the user

def build_csv_tools(file_id: str):
    """Returns tools pre-bound to a specific file_id."""
    
    @tool
    async def describe_data(_: str = "") -> str:
        """Returns shape, column names, and data types of the uploaded CSV."""
        df = await get_dataframe(file_id)
        return f"Shape: {df.shape}\nColumns: {list(df.columns)}\nDtypes:\n{df.dtypes.to_string()}"

    @tool
    async def compute_statistics(_: str = "") -> str:
        """Returns statistical summary (mean, median, std, etc.) of numeric columns."""
        df = await get_dataframe(file_id)
        return df.describe().to_string()

    @tool
    async def sample_rows(n: str = "5") -> str:
        """Returns the first N rows of the CSV."""
        df = await get_dataframe(file_id)
        return df.head(int(n)).to_string()

    @tool
    async def filter_and_count(condition: str) -> str:
        """
        Filter rows by a condition and return count + sample.
        Example condition: "Price > 100"
        """
        df = await get_dataframe(file_id)
        try:
            filtered = df.query(condition)
            return f"Matching rows: {len(filtered)}\n{filtered.head(5).to_string()}"
        except Exception as e:
            return f"Filter error: {str(e)}"

    return [describe_data, compute_statistics, sample_rows, filter_and_count]
```

```python
# backend/agent/agent.py

from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory
from agent.tools import build_csv_tools

SYSTEM_PROMPT = """You are DataLens AI, a data analyst assistant.
You have ALREADY been given access to the user's uploaded CSV file.
NEVER ask the user for a file path, file name, or file location.
The file is already loaded. Use your tools directly to answer questions.
Always be concise and present numbers clearly."""

def build_agent(file_id: str, chat_history: list):
    llm = ChatGroq(model="llama3-70b-8192", temperature=0)
    tools = build_csv_tools(file_id)

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=False)
```

---

### Key File: Upload Endpoint (with GCP Cloud Storage)

```python
# backend/api/routes/upload.py

import uuid
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from api.dependencies import get_current_user
from db.queries.files import create_file_record
from core.gcs import upload_to_gcs, delete_from_gcs
import pandas as pd
import io

router = APIRouter()
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@router.post("/upload")
async def upload_csv(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    if not file.filename.endswith((".csv", ".xlsx")):
        raise HTTPException(400, "Only CSV and XLSX files are supported.")

    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(413, "File too large. Maximum size is 10MB.")

    # Validate magic bytes — not just extension
    if not validate_csv_file(content):
        raise HTTPException(400, "File content does not match a valid CSV/XLSX format.")

    file_id = str(uuid.uuid4())
    # GCS object path: users/{user_id}/{file_id}/{original_name}
    gcs_object_name = f"users/{current_user['id']}/{file_id}/{file.filename}"

    # Upload to GCS — returns the public GCS URI (gs://bucket/path)
    gcs_uri = await upload_to_gcs(content, gcs_object_name, file.content_type or "text/csv")

    # Parse metadata in-memory — never touch disk
    df = pd.read_csv(io.BytesIO(content))

    await create_file_record({
        "id": file_id,
        "user_id": current_user["id"],
        "original_name": file.filename,
        "storage_path": gcs_uri,          # gs://your-bucket/users/...
        "gcs_object_name": gcs_object_name,
        "row_count": len(df),
        "column_names": list(df.columns),
        "file_size_bytes": len(content),
    })

    return {
        "file_id": file_id,
        "filename": file.filename,
        "rows": len(df),
        "columns": list(df.columns),
        "message": "File uploaded successfully. You can now ask questions."
    }
```

---

### Key File: /ask Endpoint with Streaming

```python
# backend/api/routes/ask.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from api.dependencies import get_current_user
from agent.agent import build_agent
from db.queries.sessions import get_session_with_file, save_message, get_chat_history
import json

router = APIRouter()

class AskRequest(BaseModel):
    session_id: str
    message: str

@router.post("/ask")
async def ask_agent(
    body: AskRequest,
    current_user: dict = Depends(get_current_user)
):
    session = await get_session_with_file(body.session_id, current_user["id"])
    if not session:
        raise HTTPException(404, "Session not found.")
    
    file_id = session["file_id"]
    if not file_id:
        raise HTTPException(400, "No file associated with this session. Please upload a file first.")

    history = await get_chat_history(body.session_id, limit=10)
    agent_executor = build_agent(file_id=file_id, chat_history=history)
    
    await save_message(body.session_id, "user", body.message)
    
    result = await agent_executor.ainvoke({
        "input": body.message,
        "chat_history": history,
    })
    
    answer = result.get("output", "I could not process that request.")
    await save_message(body.session_id, "assistant", answer)
    
    return {"response": answer, "session_id": body.session_id}
```

---

### Key File: Frontend Upload Component

```tsx
// frontend/components/UploadZone.tsx
// No manual file path input — ever.

"use client";
import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import api from "@/lib/api";

interface UploadZoneProps {
  onUploadSuccess: (fileId: string, columns: string[]) => void;
}

export function UploadZone({ onUploadSuccess }: UploadZoneProps) {
  const [uploading, setUploading] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(async (files: File[]) => {
    const file = files[0];
    if (!file) return;

    setUploading(true);
    setError(null);
    setFileName(file.name);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const { data } = await api.post("/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      // Pass file_id UP — frontend never shows a file path to the user
      onUploadSuccess(data.file_id, data.columns);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Upload failed.");
    } finally {
      setUploading(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "text/csv": [".csv"], "application/vnd.ms-excel": [".xlsx"] },
    maxFiles: 1,
  });

  return (
    <div
      {...getRootProps()}
      className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all
        ${isDragActive ? "border-blue-500 bg-blue-50" : "border-gray-300 hover:border-gray-400"}`}
    >
      <input {...getInputProps()} />
      {uploading ? (
        <p className="text-blue-500 animate-pulse">Uploading {fileName}...</p>
      ) : fileName ? (
        <p className="text-green-600">✓ {fileName} — ready for analysis</p>
      ) : (
        <p className="text-gray-500">Drop your CSV here, or click to browse</p>
      )}
      {error && <p className="text-red-500 mt-2">{error}</p>}
    </div>
  );
}
```

---

### Example End-to-End Workflow

```
1. User registers → POST /auth/register → JWT token stored in cookie

2. User uploads CSV
   → POST /upload (multipart)
   → Backend saves file, extracts metadata
   → Returns { file_id: "abc-123", columns: ["Date", "Revenue", ...] }
   → Frontend shows column preview — user never sees a file path

3. Session created
   → POST /sessions { file_id: "abc-123" }
   → Returns { session_id: "sess-456" }

4. User types: "What is the total revenue?"
   → POST /ask { session_id: "sess-456", message: "What is the total revenue?" }
   → Backend loads DataFrame from file_id (cached)
   → Agent calls compute_statistics tool internally
   → Returns: "Total revenue across all rows is $1,284,930"

5. Follow-up: "Break that down by month"
   → Same session_id → agent has memory of previous exchange
   → Agent calls filter_and_count with date grouping
   → Returns monthly breakdown

6. Session history saved to PostgreSQL messages table
```

---

## 5. Agent File Handling Fix (Detailed)

### Root Cause of the Bug

The original agent was initialized with LangChain's generic `create_csv_agent()` which internally calls a `PythonREPLTool` that requires a local file path. When deployed, that path doesn't exist in the agent's execution context.

### Fix Architecture

```
BEFORE (broken):
User uploads file → Frontend shows path "carbon_emission.csv"
                 → Agent is given: "analyze carbon_emission.csv"
                 → Agent asks: "Where is this file?"  ← BUG

AFTER (fixed):
User uploads file → Backend saves to /tmp/uuid_filename.csv
                 → DB stores file_id → storage_path mapping
                 → Frontend receives file_id only
                 → /ask endpoint is called with session_id (which has file_id)
                 → Agent tools receive file_id → resolve to DataFrame internally
                 → Agent NEVER receives or asks about a file path
```

### Session-Level File Context

```python
# When a session is created, file_id is permanently attached:
session = {
    "id": "sess-456",
    "file_id": "abc-123",   # set once on session creation, never changes
    "user_id": "user-789"
}

# Every /ask call for that session automatically has access to the file
# The agent prompt reinforces this with: "NEVER ask the user for a file path"
```

---

## 6. Security & Scalability

### JWT Authentication (authlib — python-jose is discontinued)

```python
# backend/core/security.py
# ✅ Uses authlib — actively maintained, OIDC-compliant
# ❌ NOT python-jose (abandoned since 2023, CVEs unfixed)

from authlib.jose import jwt, JoseError
from datetime import datetime, timedelta, timezone
import bcrypt
from core.config import settings

# authlib requires the key as a dict with "kty" for HMAC
JWT_KEY = {"kty": "oct", "k": settings.JWT_SECRET}
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

def create_access_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    # authlib encodes to bytes — decode to str for JSON serialization
    return jwt.encode({"alg": ALGORITHM}, payload, JWT_KEY).decode("utf-8")

def verify_token(token: str) -> str:
    """Decode and validate JWT. Raises JoseError if invalid/expired."""
    try:
        claims = jwt.decode(token, JWT_KEY)
        claims.validate()          # validates exp, iat, nbf automatically
        return claims["sub"]       # returns user_id
    except JoseError as e:
        raise ValueError(f"Invalid token: {e}")

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())
```

```python
# backend/api/dependencies.py — JWT middleware

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.security import verify_token
from db.queries.users import get_user_by_id

bearer_scheme = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> dict:
    try:
        user_id = verify_token(credentials.credentials)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await get_user_by_id(user_id)
    if not user or not user["is_active"]:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user
```

### Rate Limiting (Redis)

```python
# backend/core/rate_limit.py

import redis.asyncio as redis
from fastapi import Request, HTTPException

r = redis.from_url(settings.REDIS_URL, decode_responses=True)

async def rate_limit(request: Request, max_requests: int = 10, window: int = 60):
    user_id = request.state.user_id  # set by JWT middleware
    key = f"rate:{user_id}:{request.url.path}"
    count = await r.incr(key)
    if count == 1:
        await r.expire(key, window)
    if count > max_requests:
        raise HTTPException(429, "Too many requests. Please wait a moment.")
```

### Input Validation

```python
# All request bodies use Pydantic v2
class AskRequest(BaseModel):
    session_id: str = Field(..., min_length=36, max_length=36)  # UUID
    message: str = Field(..., min_length=1, max_length=2000)

    @field_validator("message")
    def no_injection(cls, v):
        banned = ["__import__", "exec(", "eval(", "os.system"]
        if any(b in v for b in banned):
            raise ValueError("Invalid input detected.")
        return v
```

### Secure File Handling + GCP Cloud Storage (Full Setup)

#### Step 1 — GCP Project Setup (One-Time)

```bash
# Install Google Cloud CLI
# https://cloud.google.com/sdk/docs/install

# Login and create project
gcloud auth login
gcloud projects create datalens-ai-prod --name="DataLens AI"
gcloud config set project datalens-ai-prod

# Enable Cloud Storage API
gcloud services enable storage.googleapis.com

# Create the GCS bucket (choose a region close to your users)
gcloud storage buckets create gs://datalens-ai-uploads \
  --location=asia-south1 \
  --uniform-bucket-level-access

# Create a Service Account for the backend to authenticate
gcloud iam service-accounts create datalens-backend \
  --display-name="DataLens Backend"

# Grant the service account permission to read/write the bucket
gcloud storage buckets add-iam-policy-binding gs://datalens-ai-uploads \
  --member="serviceAccount:datalens-backend@datalens-ai-prod.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

# Download the service account key JSON
gcloud iam service-accounts keys create ./backend/gcp-key.json \
  --iam-account=datalens-backend@datalens-ai-prod.iam.gserviceaccount.com
```

> ⚠️ **Never commit `gcp-key.json` to git.** Add it to `.gitignore` immediately.
> On Render, set `GCP_SERVICE_ACCOUNT_JSON` as an environment variable containing the full JSON content.

#### Step 2 — Lifecycle Policy (Auto-Delete Files After 24 Hours)

```bash
# Create lifecycle config — auto-deletes objects older than 1 day
cat > lifecycle.json << 'EOF'
{
  "rule": [
    {
      "action": {"type": "Delete"},
      "condition": {"age": 1}
    }
  ]
}
EOF

gcloud storage buckets update gs://datalens-ai-uploads \
  --lifecycle-file=lifecycle.json
```

This replaces the manual `schedule_file_deletion` background task — GCS handles it natively.

#### Step 3 — GCS Module in Backend

```python
# backend/core/gcs.py

import json
import os
from google.cloud import storage
from google.oauth2 import service_account
from core.config import settings

def _get_gcs_client() -> storage.Client:
    """Build GCS client from env var JSON (Render) or key file (local dev)."""
    if settings.GCP_SERVICE_ACCOUNT_JSON:
        # Production: JSON string stored in environment variable
        info = json.loads(settings.GCP_SERVICE_ACCOUNT_JSON)
        creds = service_account.Credentials.from_service_account_info(info)
    else:
        # Local dev: key file on disk
        creds = service_account.Credentials.from_service_account_file(
            settings.GCP_KEY_FILE_PATH  # e.g., "./gcp-key.json"
        )
    return storage.Client(credentials=creds, project=settings.GCP_PROJECT_ID)

async def upload_to_gcs(content: bytes, object_name: str, content_type: str) -> str:
    """Upload bytes to GCS. Returns gs:// URI."""
    client = _get_gcs_client()
    bucket = client.bucket(settings.GCS_BUCKET_NAME)
    blob = bucket.blob(object_name)
    blob.upload_from_string(content, content_type=content_type)
    return f"gs://{settings.GCS_BUCKET_NAME}/{object_name}"

async def download_from_gcs(object_name: str) -> bytes:
    """Download file content from GCS as bytes."""
    client = _get_gcs_client()
    bucket = client.bucket(settings.GCS_BUCKET_NAME)
    blob = bucket.blob(object_name)
    return blob.download_as_bytes()

async def delete_from_gcs(object_name: str) -> None:
    """Delete a file from GCS (call when session is deleted)."""
    client = _get_gcs_client()
    bucket = client.bucket(settings.GCS_BUCKET_NAME)
    blob = bucket.blob(object_name)
    blob.delete(if_generation_match=None)

def generate_signed_url(object_name: str, expiration_minutes: int = 60) -> str:
    """
    Generate a time-limited signed URL for direct browser download.
    Useful if you want users to re-download their original CSV.
    """
    import datetime
    client = _get_gcs_client()
    bucket = client.bucket(settings.GCS_BUCKET_NAME)
    blob = bucket.blob(object_name)
    return blob.generate_signed_url(
        expiration=datetime.timedelta(minutes=expiration_minutes),
        method="GET",
    )
```

#### Step 4 — Updated DB Schema (add gcs_object_name column)

```sql
-- Add to migrations/002_create_files.sql
ALTER TABLE uploaded_files ADD COLUMN IF NOT EXISTS
    gcs_object_name TEXT;   -- e.g. "users/uuid/file_id/sales.csv"
```

#### Step 5 — Validate File by Magic Bytes

```python
# backend/core/security.py (add to existing file)
import magic

def validate_csv_file(content: bytes) -> bool:
    """Reject files that aren't actually CSV/XLSX regardless of extension."""
    mime = magic.from_buffer(content[:2048], mime=True)
    return mime in [
        "text/plain", "text/csv", "application/csv",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ]
```

### Environment Variables

```bash
# backend/.env.example

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/datalens

# Redis
REDIS_URL=redis://localhost:6379

# Auth — authlib (NOT python-jose, which is discontinued)
JWT_SECRET=your-very-long-random-secret-key-here-min-32-chars

# AI
GROQ_API_KEY=your-groq-api-key

# GCP Cloud Storage
GCP_PROJECT_ID=datalens-ai-prod
GCS_BUCKET_NAME=datalens-ai-uploads

# Local dev: path to key file
GCP_KEY_FILE_PATH=./gcp-key.json

# Production (Render): paste full JSON content of service account key
# GCP_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":...}

# App
MAX_FILE_SIZE_MB=10
CORS_ORIGINS=http://localhost:3000,https://your-frontend.vercel.app
```

---

## 7. Database Constraint — PostgreSQL Implementation

**No SQLite. No SQLAlchemy. Raw asyncpg only.**

```python
# backend/db/connection.py

import asyncpg
from core.config import settings

_pool: asyncpg.Pool | None = None

async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            dsn=settings.DATABASE_URL,
            min_size=2,
            max_size=10,
            command_timeout=30,
        )
    return _pool

async def close_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
```

```python
# backend/db/queries/files.py

from db.connection import get_pool

async def create_file_record(data: dict):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO uploaded_files
                (id, user_id, original_name, storage_path, row_count, column_names, file_size_bytes)
            VALUES ($1, $2, $3, $4, $5, $6::jsonb, $7)
        """, data["id"], data["user_id"], data["original_name"],
            data["storage_path"], data["row_count"],
            str(data["column_names"]), data["file_size_bytes"])

async def get_file_by_id(file_id: str) -> dict | None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM uploaded_files WHERE id = $1", file_id
        )
        return dict(row) if row else None
```

---

## 8. Performance & UX Improvements

### Conversational Memory Per Session

```python
# backend/agent/memory.py

from langchain.schema import HumanMessage, AIMessage

def format_history(messages: list[dict]) -> list:
    """Convert DB message records to LangChain message objects."""
    result = []
    for msg in messages[-10:]:  # Keep last 10 messages only
        if msg["role"] == "user":
            result.append(HumanMessage(content=msg["content"]))
        else:
            result.append(AIMessage(content=msg["content"]))
    return result
```

### Caching DataFrame in Memory

Already covered in `file_context.py` — DataFrame is cached by `file_id` so repeated questions on the same file don't re-read from disk.

### Auto-Generated Session Titles

```python
# When first message is sent, auto-title the session from the filename
async def auto_title_session(session_id: str, filename: str):
    title = filename.replace(".csv", "").replace("_", " ").title()
    await update_session_title(session_id, f"{title} Analysis")
```

### UX — Column Preview on Upload

After upload, frontend immediately shows:
- File name, row count, column names
- Sample of first 3 rows
- No prompts, no "please provide file path"
- Chat is unlocked automatically

---

## 9. Bonus Improvements

### Docker Compose (Local Dev)

```yaml
# docker-compose.yml
version: "3.9"
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: datalens
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  pgdata:
```

### GitHub Actions CI

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: password
          POSTGRES_DB: datalens_test
        ports: ["5432:5432"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -r backend/requirements.txt
      - run: pytest backend/tests/ -v
        env:
          DATABASE_URL: postgresql://postgres:password@localhost:5432/datalens_test
          JWT_SECRET: test-secret
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
```

### Logging & Monitoring

```python
# backend/api/main.py — structured logging

import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "level": record.levelname,
            "message": record.getMessage(),
            "path": getattr(record, "path", ""),
            "user_id": getattr(record, "user_id", ""),
            "timestamp": self.formatTime(record),
        })

logging.getLogger().addHandler(logging.StreamHandler())
# Ship logs to Render's log drain or Logtail (free tier)
```

### Swagger / OpenAPI

FastAPI auto-generates this. Customize it:
```python
app = FastAPI(
    title="DataLens AI API",
    description="Conversational BI for non-technical teams",
    version="1.0.0",
    docs_url="/docs",      # Swagger UI
    redoc_url="/redoc",    # ReDoc
    openapi_url="/openapi.json"
)
```
**Live at**: `https://your-backend.onrender.com/docs`

### Interview-Ready Feature Ideas

- **Auto chart generation** — agent returns base64 matplotlib chart when asked to "visualize" or "plot"
- **Multi-file sessions** — join two CSVs by a common column (shows SQL-like thinking)
- **Export chat as PDF report** — downloadable summary of the entire analysis
- **Shareable sessions** — generate a read-only link to a session (like Notion sharing)
- **CSV anomaly detection** — flag outliers automatically on upload

---

## Quick Start (Full Project in 3 Commands)

```bash
# 1. Clone and enter
git clone https://github.com/YOUR_USERNAME/datalens-ai && cd datalens-ai

# 2. Start local infra
docker compose up -d

# 3. Start backend
cd backend && pip install -r requirements.txt
cp .env.example .env  # fill in GROQ_API_KEY
python -m alembic upgrade head  # or: psql < migrations/001_create_users.sql
uvicorn api.main:app --reload
```

Then visit `http://localhost:3000` for the frontend.

---

*Built to impress. Designed to scale. Ready for production.*
