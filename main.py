# FastAPI app with CORS support
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import pandas as pd
from io import StringIO
from agent import run_agent

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
        
        response = run_agent(user_input)
        return {"agent_response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))