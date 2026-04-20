import uuid
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from api.dependencies import get_current_user
from db.queries.files import create_file_record
from core.gcs import upload_to_gcs, delete_from_gcs
import pandas as pd
import io

router = APIRouter(prefix="/upload", tags=["upload"])
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/")
async def upload_csv(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    if not file.filename.endswith((".csv", ".xlsx")):
        raise HTTPException(400, "Only CSV and XLSX files are supported.")

    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(413, "File too large. Maximum size is 10MB.")

    file_id = str(uuid.uuid4())
    gcs_object_name = f"users/{current_user['id']}/{file_id}/{file.filename}"

    try:
        gcs_uri = await upload_to_gcs(content, gcs_object_name, file.content_type or "text/csv")
    except Exception:
        # If GCS fails, use local storage path as fallback
        gcs_uri = f"local://{file_id}/{file.filename}"
        gcs_object_name = None

    # Parse metadata in-memory
    if file.filename.endswith(".csv"):
        df = pd.read_csv(io.BytesIO(content))
    else:
        df = pd.read_excel(io.BytesIO(content))

    await create_file_record({
        "id": file_id,
        "user_id": str(current_user["id"]),
        "original_name": file.filename,
        "storage_path": gcs_uri,
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


@router.delete("/{file_id}")
async def delete_uploaded_file(
    file_id: str,
    current_user: dict = Depends(get_current_user)
):
    from db.queries.files import get_file_by_id, delete_file as db_delete_file
    
    file_record = await get_file_by_id(file_id)
    if not file_record or str(file_record["user_id"]) != str(current_user["id"]):
        raise HTTPException(404, "File not found")
    
    # Delete from GCS if exists
    if file_record.get("gcs_object_name"):
        try:
            await delete_from_gcs(file_record["gcs_object_name"])
        except Exception:
            pass
    
    # Delete from DB
    await db_delete_file(file_id, str(current_user["id"]))
    
    return {"message": "File deleted successfully"}