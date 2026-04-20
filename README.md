# CSV AI Agent

An AI-powered assistant that lets you chat with your CSV data using natural language. Built with FastAPI, LangChain, and Groq.

## Features

- **Natural Language Queries** - Ask questions about your CSV data in plain English
- **AI-Powered Analysis** - Uses Groq LLM with LangChain for intelligent responses
- **File Operations** - Read and analyze CSV files with ease
- **Modern UI** - Clean, responsive web interface
- **Serverless Deployment** - Deploy to Vercel with Python serverless functions

## Tech Stack

- **Backend**: FastAPI + LangChain + Groq
- **Frontend**: Static HTML/CSS/JS
- **Deployment**: Vercel (Python serverless)

## Prerequisites

- Python 3.10+
- Groq API Key ([get one free](https://console.groq.com))

## Local Development

### 1. Clone the repository

```bash
git clone https://github.com/RYUKxAYU/CSV-analysis-agent-.git
cd CSV-analysis-agent-
```

### 2. Create virtual environment

```bash
python -m venv .venv
# Activate on Windows
.venv\Scripts\activate
# Activate on Mac/Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Run the API server

```bash
uvicorn api.index:app --reload
```

The API will be available at `http://localhost:8000`

### 6. Open the frontend

Open `index.html` in your browser, or serve it:

```bash
# Using Python
python -m http.server 3000
```

Then visit `http://localhost:3000`

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API health check |
| `/health` | GET | Health status |
| `/ask` | POST | Send a query to the agent |

### Example Request

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"user_input": "What is the average price in my CSV?"}'
```

## Deployment

This project uses a split deployment:
- **Backend**: Render (Python serverless)
- **Frontend**: Vercel (static)

### Backend (Render)

1. Go to [render.com](https://render.com) → New Web Service
2. Connect your GitHub repository
3. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn api.index:app --host 0.0.0.0 --port $PORT`
4. Add environment variable: `GROQ_API_KEY`
5. Your backend URL: `https://csv-analysis-agent.onrender.com`

### Frontend (Vercel)

1. Go to [vercel.com](https://vercel.com) → New Project
2. Connect your GitHub repository
3. Deploy the `index.html` static file
4. Your frontend URL: `https://csv-ai-agent-orcin.vercel.app`

### Update Frontend API URL

After deploying the backend, update `index.html`:

```javascript
const API_URL = 'https://csv-analysis-agent.onrender.com';
```

Then commit and push to redeploy the frontend.

## Project Structure

```
csv_ai_agent/
├── api/
│   └── index.py          # FastAPI backend for Vercel
├── index.html            # Static frontend
├── agent.py              # LangChain agent logic
├── tools.py              # Tool functions (read/write CSV)
├── main.py               # Standalone FastAPI (for local)
├── app.py                # Streamlit frontend (legacy)
├── requirements.txt      # Python dependencies
├── vercel.json           # Vercel configuration
├── .vercelignore         # Files to exclude from deploy
└── Dockerfile            # Docker configuration
```

## Usage

1. **Upload a CSV** - Click the upload area or drag & drop a CSV file
2. **Ask questions** - Type questions like:
   - "What columns does this file have?"
   - "Show me the first 5 rows"
   - "What's the average of column X?"
   - "Summarize the data"

## License

MIT