import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from api.dependencies import get_current_user
from db.queries.sessions import (
    create_session, get_user_sessions, get_session_by_id,
    delete_session, update_session_title
)

router = APIRouter(prefix="/sessions", tags=["sessions"])


class CreateSessionRequest(BaseModel):
    file_id: str = None
    title: str = None


@router.get("/")
async def list_sessions(current_user: dict = Depends(get_current_user)):
    """List all sessions for the current user."""
    sessions = await get_user_sessions(str(current_user["id"]))
    return {"sessions": sessions}


@router.post("/")
async def create_new_session(
    request: CreateSessionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a new analysis session."""
    session = await create_session(
        user_id=str(current_user["id"]),
        file_id=request.file_id,
        title=request.title
    )
    return {"session": session}


@router.get("/{session_id}")
async def get_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific session."""
    session = await get_session_by_id(session_id, str(current_user["id"]))
    if not session:
        raise HTTPException(404, "Session not found")
    return {"session": session}


@router.delete("/{session_id}")
async def delete_session_endpoint(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a session."""
    success = await delete_session(session_id, str(current_user["id"]))
    if not success:
        raise HTTPException(404, "Session not found")
    return {"message": "Session deleted successfully"}


@router.patch("/{session_id}/title")
async def update_title(
    session_id: str,
    request: CreateSessionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update session title."""
    session = await get_session_by_id(session_id, str(current_user["id"]))
    if not session:
        raise HTTPException(404, "Session not found")
    
    await update_session_title(session_id, request.title)
    return {"message": "Title updated successfully"}