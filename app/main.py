import os
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .repository import create_case, list_cases, get_case
from .uploads import validate_file, save_upload, create_artefact_record

app = FastAPI(title="Privacy Intake", version="0.1.0")
templates = Jinja2Templates(directory="app/templates")

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path(os.getenv('UPLOAD_DIR', './uploads'))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Mount static files for downloads
app.mount('/uploads', StaticFiles(directory=str(UPLOAD_DIR)), name='uploads')

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "cases": list_cases()})

@app.get("/cases/new", response_class=HTMLResponse)
def new_case(request: Request):
    return templates.TemplateResponse("new_case.html", {"request": request})

@app.post("/cases")
async def create_case_route(
    request_type: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    submitted_by: str = Form(...),
    urgency: str = Form("normal"),
    business_area: str = Form(""),
    controller_name: str = Form(""),
    client_name: str = Form(""),
    deadline_at: str = Form(""),
    confidentiality_level: str = Form("internal"),
    contains_phi: bool = Form(False),
    contains_special_category: bool = Form(False),
    international_transfer: bool = Form(False),
    files: list[UploadFile] = File(default=[]),
):
    payload = {
        "request_type": request_type,
        "title": title,
        "description": description,
        "submitted_by": submitted_by,
        "urgency": urgency,
        "business_area": business_area or None,
        "controller_name": controller_name or None,
        "client_name": client_name or None,
        "deadline_at": deadline_at or None,
        "confidentiality_level": confidentiality_level,
        "contains_phi": contains_phi,
        "contains_special_category": contains_special_category,
        "international_transfer": international_transfer,
        "metadata": {},
    }
    created = create_case(payload)
    
    # Process file uploads
    uploaded_artefacts = []
    if files:
        from .db import get_db
        for file in files:
            if file.filename:
                is_valid, error = validate_file(file)
                if not is_valid:
                    # Skip invalid files but continue processing
                    continue
                try:
                    upload_meta = await save_upload(file, created['id'], created['case_ref'])
                    # Create artefact record
                    with get_db() as conn:
                        artefact = create_artefact_record(
                            conn,
                            case_id=created['id'],
                            task_id=created.get('task_id'),
                            upload_meta=upload_meta,
                            submitted_by=submitted_by,
                        )
                        uploaded_artefacts.append(artefact)
                except Exception as e:
                    # Log error but don't fail the case creation
                    import logging
                    logging.error(f"Failed to save upload {file.filename}: {e}")
    
    return RedirectResponse(url=f"/cases/{created['id']}", status_code=303)

@app.get("/cases/{case_id}", response_class=HTMLResponse)
def case_detail(case_id: str, request: Request):
    data = get_case(case_id)
    return templates.TemplateResponse("case_detail.html", {"request": request, **data})

@app.get("/api/cases")
def api_cases():
    return JSONResponse(list_cases())
