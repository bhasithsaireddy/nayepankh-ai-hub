"""
main.py — FastAPI server for NayePankh AI Hub

Endpoints:
  POST /chat      — AI agent conversation
  POST /register  — Volunteer registration
  GET  /stats     — Live volunteer statistics
  GET  /health    — Health check
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from database import init_db, save_volunteer, get_stats, get_db
from agent import chat as agent_chat

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="NayePankh AI Hub API",
    description="AI-powered volunteer platform for NayePankh Foundation",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# REQUEST / RESPONSE MODELS
# ─────────────────────────────────────────────
class ChatRequest(BaseModel):
    messages: list


class RegisterRequest(BaseModel):
    name: str
    email: str
    skills: str
    city: str
    hours_per_week: int


# ─────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "service": "NayePankh AI Hub"}


@app.post("/chat")
def chat(req: ChatRequest):
    try:
        reply = agent_chat(req.messages)
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/register")
def register(req: RegisterRequest):
    try:
        from agent import match_department
        department = match_department(req.skills)
        db = next(get_db())
        save_volunteer(
            db=db,
            name=req.name,
            email=req.email,
            skills=req.skills,
            city=req.city,
            hours_per_week=req.hours_per_week,
            department=department
        )
        return {
            "success": True,
            "name": req.name,
            "department": department,
            "message": f"Welcome to NayePankh, {req.name}! You've been matched to {department}."
        }
    except Exception as e:
        error_msg = str(e)
        if "UNIQUE constraint" in error_msg:
            raise HTTPException(status_code=409, detail="This email is already registered.")
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/stats")
def stats():
    try:
        db = next(get_db())
        data = get_stats(db)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
