"""
Clarity Rx FastAPI Backend Server
Wraps existing Python modules as REST API endpoints.
"""

import os
import sys
import uuid
import json
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Ensure src is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import Config
from src.auth import AuthManager
from src.extractor import PrescriptionExtractor
from src.vector_store import VectorStoreManager
from src.graph import RAGGraph
from src.memory import MemoryManager
from src.otc_manager import OTCManager
from src.utils import setup_logger

logger = setup_logger(__name__)

app = FastAPI(title="Clarity Rx API", version="2.0")

# CORS for React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Initialize Managers (singletons) ──────────────────────────────
auth_manager = AuthManager()
extractor = PrescriptionExtractor()
vector_store = VectorStoreManager()
rag_graph = RAGGraph().build_graph()
memory_manager = MemoryManager()
otc_manager = OTCManager()

logger.info("All managers initialized successfully.")


# ── Pydantic Models ───────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str

class ChatRequest(BaseModel):
    question: str
    prescription_id: str
    session_id: str
    language: str = "English"

class OTCCheckRequest(BaseModel):
    session_id: str
    prescription_id: str
    details_text: str


# ── Auth Endpoints ────────────────────────────────────────────────

@app.post("/api/auth/login")
async def login(req: LoginRequest):
    if not req.username or not req.password:
        raise HTTPException(status_code=400, detail="Username and password are required.")
    success, msg = auth_manager.login_user(req.username, req.password)
    if success:
        return {"success": True, "message": msg, "username": req.username}
    raise HTTPException(status_code=401, detail=msg)


@app.post("/api/auth/register")
async def register(req: RegisterRequest):
    if not req.username or not req.password:
        raise HTTPException(status_code=400, detail="All fields are required.")
    success, msg = auth_manager.register_user(req.username, req.password)
    if success:
        return {"success": True, "message": msg}
    raise HTTPException(status_code=400, detail=msg)


# ── Prescription Endpoints ────────────────────────────────────────

@app.get("/api/prescriptions/list")
async def list_prescriptions(username: str = Query(...)):
    prescriptions = memory_manager.get_user_prescriptions(username)
    return {"prescriptions": prescriptions}


@app.post("/api/prescriptions/upload")
async def upload_prescription(
    file: UploadFile = File(...),
    username: str = Form(...)
):
    # Check if already uploaded
    existing_id = memory_manager.get_prescription_by_filename(username, file.filename)
    if existing_id:
        session_id = memory_manager.get_or_create_session(username, existing_id)
        return {
            "success": True,
            "already_exists": True,
            "prescription_id": existing_id,
            "session_id": session_id,
            "message": f"File '{file.filename}' already uploaded."
        }

    file_id = str(uuid.uuid4())

    # Save file
    from src.utils import ensure_directory
    ensure_directory(Config.INPUT_DIR)
    file_path = os.path.join(Config.INPUT_DIR, file.filename)
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    # Extract data
    data = extractor.extract_data(file_path)
    if not data:
        raise HTTPException(status_code=500, detail="Failed to extract prescription data.")

    # Format medicine details
    med_details = []
    for med in data.get("medicines", []):
        timing = med.get("timing", {})
        timing_str = (
            f"Morning: {timing.get('morning')}, "
            f"Afternoon: {timing.get('afternoon')}, "
            f"Night: {timing.get('night')}, "
            f"Instruction: {timing.get('instruction')}"
        )
        med_details.append(
            f"- {med.get('name')} (Qty: {med.get('quantity')}): "
            f"{timing_str}, Freq: {med.get('frequency')}, Duration: {med.get('duration')}"
        )

    meds_str = "\n".join(med_details)
    text_content = f"Date: {data.get('date')}\n\nMedicines:\n{meds_str}\n\nNotes: {data.get('notes')}"

    # Store in Pinecone
    metadata = {"filename": file.filename}
    vector_store.add_prescription(file_id, [text_content], metadata)

    # Generate title
    med_names = [m.get("name", "Unknown") for m in data.get("medicines", [])]
    if med_names:
        title = f"Prescription: {', '.join(med_names[:2])}"
        if len(med_names) > 2:
            title += "..."
    else:
        title = f"Prescription {file.filename}"

    session_id = memory_manager.get_or_create_session(
        username, file_id, title=title, filename=file.filename, details=meds_str
    )

    return {
        "success": True,
        "already_exists": False,
        "prescription_id": file_id,
        "session_id": session_id,
        "title": title,
        "extracted_data": data,
        "details": meds_str,
        "message": "Prescription processed successfully."
    }


# ── Session Endpoints ─────────────────────────────────────────────

@app.get("/api/sessions/{prescription_id}")
async def get_session(prescription_id: str, username: str = Query(...)):
    session_id = memory_manager.get_or_create_session(username, prescription_id)
    details = memory_manager.get_session_details(session_id)
    return {"session_id": session_id, "details": details}


# ── Chat Endpoints ────────────────────────────────────────────────

@app.get("/api/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    history = memory_manager.get_history(session_id)
    messages = [{"role": msg["role"], "content": msg["content"]} for msg in history]
    return {"messages": messages}


@app.post("/api/chat")
async def chat(req: ChatRequest):
    inputs = {
        "question": req.question,
        "prescription_id": req.prescription_id,
        "session_id": req.session_id,
        "language": req.language,
        "context": [],
        "answer": ""
    }
    result = rag_graph.invoke(inputs)
    return {"answer": result["answer"]}


# ── OTC Endpoints ─────────────────────────────────────────────────

@app.get("/api/otc/list")
async def get_otc_list():
    raw_list = otc_manager.get_otc_list()
    display_list = []
    for item in raw_list:
        display_list.append({
            "medicine_name": item["medicine_name"],
            "type": item["metadata"].get("type", "General")
        })
    return {"medicines": display_list}


@app.get("/api/otc/search")
async def search_otc(q: str = Query(...)):
    results = otc_manager.search_otc_db(q)
    return {"results": results}


@app.post("/api/otc/check")
async def check_otc(req: OTCCheckRequest):
    # Check DB cache first
    db_result = memory_manager.get_otc_result(req.session_id)
    if db_result:
        return {"result": db_result, "cached": True}

    # Run LLM check
    result = otc_manager.check_medicines_with_llm([req.details_text])

    # Cache if successful
    if "error" not in result:
        memory_manager.save_otc_result(req.session_id, result)

    return {"result": result, "cached": False}


@app.get("/api/otc/result/{session_id}")
async def get_otc_result(session_id: str):
    result = memory_manager.get_otc_result(session_id)
    return {"result": result}


# ── Health Check ──────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "2.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
