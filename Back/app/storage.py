import os
import uuid
import shutil
from .config import settings

def get_s3_client():
    if not (settings.AWS_ENDPOINT_URL_S3 and settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY):
        return None
    try:
        import boto3
        return boto3.client(
            "s3",
            endpoint_url=settings.AWS_ENDPOINT_URL_S3,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
    except Exception as e:
        print("S3 Init Warning:", e)
        return None

def upload_file_bytes(file_bytes: bytes, filename: str, content_type: str = "image/png") -> str:
    """
    Upload file bytes to S3 or fallback to local disk. Returns accessible URL.
    """
    ext = os.path.splitext(filename)[1].lower() or ".png"
    unique_key = f"uploads/prod_{uuid.uuid4().hex[:12]}{ext}"

    s3 = get_s3_client()
    if s3:
        try:
            bucket = settings.AWS_S3_BUCKET
            s3.put_object(
                Bucket=bucket,
                Key=unique_key,
                Body=file_bytes,
                ContentType=content_type
            )
            # If endpoint has custom domain or standard S3 format:
            endpoint = settings.AWS_ENDPOINT_URL_S3.rstrip('/')
            return f"{endpoint}/{bucket}/{unique_key}"
        except Exception as s3_err:
            print("S3 Upload Failed, falling back to local disk:", s3_err)

    # Local fallback
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    upload_dir = os.path.join(base_dir, "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    local_filename = os.path.basename(unique_key)
    filepath = os.path.join(upload_dir, local_filename)

    with open(filepath, "wb") as f:
        f.write(file_bytes)

    return f"/uploads/{local_filename}"
