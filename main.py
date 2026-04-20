# from fastapi import FastAPI, HTTPException, File, UploadFile
# from pydantic import BaseModel
# import shutil
# import os
# from agent import run_agent

# app = FastAPI(title="CSV AI Agent API")
# @app.get("/")
# def home():
#     return {"message": "Backend is running! Visit /docs to test endpoints."}
from fastapi import FastAPI
from pydantic import BaseModel
from agent import run_agent

app = FastAPI(title="CSV AI Agent API")

class Query(BaseModel):
    user_input: str

@app.post("/")
def ask_agent(query: Query):
    # Call your agent logic
    response = run_agent(query.user_input)
    return {"agent_response": response}
