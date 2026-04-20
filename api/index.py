# Vercel serverless FastAPI entry point
import os
from dotenv import load_dotenv

# Load environment variables - only from system env in Vercel
if os.path.exists('.env'):
    load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio

app = FastAPI(title="CSV AI Agent API")

class Query(BaseModel):
    user_input: str

# Lazy import to avoid cold start issues
def get_agent():
    from agent import run_agent
    return run_agent

@app.get("/")
def home():
    return {"message": "CSV AI Agent API is running! Send POST requests to /ask for agent queries."}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/ask")
def ask_agent(query: Query):
    """Main endpoint to query the AI agent."""
    try:
        run_agent = get_agent()
        response = run_agent(query.user_input)
        return {"agent_response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# For Vercel serverless function
def handler(request, context):
    """Vercel serverless function handler."""
    from mangum import Mangum
    asgi_handler = Mangum(app)
    return asgi_handler(request, context)