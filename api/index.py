# Vercel serverless FastAPI entry point
import os
from dotenv import load_dotenv

# Load environment variables - only from system env in Vercel
if os.path.exists('.env'):
    load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import pandas as pd
from io import StringIO

app = FastAPI(title="CSV AI Agent API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    user_input: str
    csv_content: str = None
    filename: str = "data.csv"

# Import the shared FILE_STORE from tools
from tools import FILE_STORE, save_file, get_file

def get_agent():
    from agent import run_agent
    return run_agent

@app.get("/")
def home():
    return {"message": "CSV AI Agent API is running!"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/ask")
def ask_agent(query: Query):
    """Main endpoint to query the AI agent."""
    try:
        if query.csv_content:
            # Save the CSV content to memory store
            file_id = save_file(StringIO(query.csv_content))
            user_input = f"Use analyze_csv with file_id: {file_id}. {query.user_input}"
        else:
            user_input = query.user_input
        
        run_agent = get_agent()
        response = run_agent(user_input)
        return {"agent_response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# For Vercel serverless function
def handler(request, context):
    """Vercel serverless function handler."""
    from mangum import Mangum
    asgi_handler = Mangum(app)
    return asgi_handler(request, context)