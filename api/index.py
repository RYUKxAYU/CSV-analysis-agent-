# Vercel serverless FastAPI entry point
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

# Load environment variables
load_dotenv()

app = FastAPI(title="CSV AI Agent API")


class Query(BaseModel):
    user_input: str


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
        from agent import run_agent
        response = run_agent(query.user_input)
        return {"agent_response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# For Vercel serverless function handler
def handler(request, context):
    """Vercel serverless function handler."""
    return app