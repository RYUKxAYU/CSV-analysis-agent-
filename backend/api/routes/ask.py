from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from api.dependencies import get_current_user
from agent.agent import build_agent_with_memory, run_agent_query
from db.queries.sessions import get_session_with_file, save_message, get_chat_history, update_session_activity
from db.queries.files import get_file_by_id
import json
import asyncio

router = APIRouter(prefix="/ask", tags=["ask"])


class AskRequest(BaseModel):
    session_id: str
    message: str = Field(..., min_length=1, max_length=2000)


@router.post("/")
async def ask_agent(
    body: AskRequest,
    current_user: dict = Depends(get_current_user)
):
    """Query the agent with a message."""
    session = await get_session_with_file(body.session_id, str(current_user["id"]))
    if not session:
        raise HTTPException(404, "Session not found.")
    
    file_id = session.get("file_id")
    if not file_id:
        raise HTTPException(400, "No file associated with this session. Please upload a file first.")

    # Get chat history
    history = await get_chat_history(body.session_id, limit=10)
    
    # Save user message
    await save_message(body.session_id, "user", body.message)
    
    # Run agent
    try:
        answer = await run_agent_query(file_id, body.message, history)
    except Exception as e:
        raise HTTPException(500, f"Agent error: {str(e)}")
    
    # Save assistant message
    await save_message(body.session_id, "assistant", answer)
    
    # Update session activity
    await update_session_activity(body.session_id)
    
    return {"response": answer, "session_id": body.session_id}


@router.post("/stream")
async def ask_agent_stream(
    body: AskRequest,
    current_user: dict = Depends(get_current_user)
):
    """Query the agent with streaming responses."""
    session = await get_session_with_file(body.session_id, str(current_user["id"]))
    if not session:
        raise HTTPException(404, "Session not found.")
    
    file_id = session.get("file_id")
    if not file_id:
        raise HTTPException(400, "No file associated with this session.")
    
    # Get chat history
    history = await get_chat_history(body.session_id, limit=10)
    
    # Save user message
    await save_message(body.session_id, "user", body.message)
    
    async def generate():
        try:
            agent_executor = build_agent_with_memory(file_id, history)
            
            # For streaming, we'll yield chunks (simplified)
            result = await agent_executor.ainvoke({"input": body.message})
            answer = result.get("output", "")
            
            # Save assistant message
            await save_message(body.session_id, "assistant", answer)
            await update_session_activity(body.session_id)
            
            # Stream the response
            for chunk in answer.split():
                yield f"data: {json.dumps({'token': chunk + ' '})}\n\n"
                await asyncio.sleep(0.05)
            
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")