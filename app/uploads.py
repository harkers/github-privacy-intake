"""File upload handling for privacy intake cases."""

import os
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional
from fastapi import UploadFile
from psycopg.types.json import Json

# Allowed file types with their MIME types
ALLOWED_EXTENSIONS = {
    '.pdf': 'application/pdf',
    '.doc': 'application/msword',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.txt': 'text/plain',
}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB max

# Upload storage path - can be overridden via environment
UPLOAD_DIR = Path(os.getenv('UPLOAD_DIR', './uploads'))


def validate_file(file: UploadFile) -> tuple[bool, str]:
    """Validate uploaded file.
    
    Returns (is_valid, error_message).
    """
    if not file.filename:
        return False, "No filename provided"
    
    # Check extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS.keys())}"
    
    # Filename security - prevent path traversal
    if '..' in file.filename or '/' in file.filename or '\\' in file.filename:
        return False, "Invalid filename"
    
    return True, ""


async def save_upload(file: UploadFile, case_id: str, case_ref: str) -> dict:
    """Save uploaded file and return artefact metadata.
    
    Creates directory structure: uploads/{case_ref}/
    Generates SHA256 hash for integrity.
    """
    # Ensure upload directory exists
    case_dir = UPLOAD_DIR / case_ref
    case_dir.mkdir(parents=True, exist_ok=True)
    
    # Sanitize filename
    safe_name = Path(file.filename).name
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    stored_name = f"{timestamp}_{safe_name}"
    file_path = case_dir / stored_name
    
    # Read and hash in chunks
    content = await file.read()
    
    # Check size
    if len(content) > MAX_FILE_SIZE:
        raise ValueError(f"File too large. Max size: {MAX_FILE_SIZE // (1024*1024)}MB")
    
    # Calculate hash
    sha256 = hashlib.sha256(content).hexdigest()
    
    # Write file
    file_path.write_bytes(content)
    
    # Get MIME type
    ext = Path(file.filename).suffix.lower()
    mime_type = ALLOWED_EXTENSIONS.get(ext, 'application/octet-stream')
    
    return {
        'filename': file.filename,
        'stored_name': stored_name,
        'storage_path': str(file_path),
        'mime_type': mime_type,
        'sha256': sha256,
        'size_bytes': len(content),
    }


def create_artefact_record(conn, case_id: str, task_id: Optional[str], upload_meta: dict, submitted_by: str) -> dict:
    """Create artefact record in database."""
    import uuid
    
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO artefacts (
                id, case_id, task_id, artefact_type, filename, storage_path,
                mime_type, sha256, created_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, filename, artefact_type, created_at
            """,
            (
                str(uuid.uuid4()),
                case_id,
                task_id,
                'submission_attachment',
                upload_meta['filename'],
                upload_meta['storage_path'],
                upload_meta['mime_type'],
                upload_meta['sha256'],
                submitted_by,
            ),
        )
        return cur.fetchone()