# from fastapi import FastAPI, HTTPException, File, UploadFile
# from pydantic import BaseModel
# import shutil
# import os
# from agent import run_agent

# app = FastAPI(title="CSV AI Agent API")
# @app.get("/")
# def home():
#     return {"message": "Backend is running! Visit /docs to test endpoints."}
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import run_agent

app = FastAPI(title="CSV AI Agent API")

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    user_input: str

@app.get("/")
def home():
    return {"message": "CSV AI Agent API is running! Visit /docs to test endpoints."}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/ask")
def ask_agent(query: Query):
    # Call your agent logic
    try:
        response = run_agent(query.user_input)
        return {"agent_response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))