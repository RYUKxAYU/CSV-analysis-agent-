import json
import os
from google.cloud import storage
from google.oauth2 import service_account
from core.config import settings


def _get_gcs_client() -> storage.Client:
    """Build GCS client from env var JSON (Render) or key file (local dev)."""
    if settings.GCP_SERVICE_ACCOUNT_JSON:
        info = json.loads(settings.GCP_SERVICE_ACCOUNT_JSON)
        creds = service_account.Credentials.from_service_account_info(info)
    else:
        creds = service_account.Credentials.from_service_account_file(
            settings.GCP_KEY_FILE_PATH
        )
    return storage.Client(credentials=creds, project=settings.GCP_PROJECT_ID)


async def upload_to_gcs(content: bytes, object_name: str, content_type: str) -> str:
    """Upload bytes to GCS. Returns gs:// URI."""
    client = _get_gcs_client()
    bucket = client.bucket(settings.GCS_BUCKET_NAME)
    blob = bucket.blob(object_name)
    blob.upload_from_string(content, content_type=content_type)
    return f"gs://{settings.GCS_BUCKET_NAME}/{object_name}"


async def download_from_gcs(object_name: str) -> bytes:
    """Download file content from GCS as bytes."""
    client = _get_gcs_client()
    bucket = client.bucket(settings.GCS_BUCKET_NAME)
    blob = bucket.blob(object_name)
    return blob.download_as_bytes()


async def delete_from_gcs(object_name: str) -> None:
    """Delete a file from GCS (call when session is deleted)."""
    client = _get_gcs_client()
    bucket = client.bucket(settings.GCS_BUCKET_NAME)
    blob = bucket.blob(object_name)
    blob.delete(if_generation_match=None)


def generate_signed_url(object_name: str, expiration_minutes: int = 60) -> str:
    """Generate a time-limited signed URL for direct browser download."""
    import datetime
    client = _get_gcs_client()
    bucket = client.bucket(settings.GCS_BUCKET_NAME)
    blob = bucket.blob(object_name)
    return blob.generate_signed_url(
        expiration=datetime.timedelta(minutes=expiration_minutes),
        method="GET",
    )