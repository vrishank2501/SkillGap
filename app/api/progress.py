import logging
from typing import Optional, Any
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Header
from app.progress.supabase_progress import supabase_progress

router = APIRouter(prefix="/progress", tags=["progress"])
logger = logging.getLogger(__name__)

class QuizSubmission(BaseModel):
    user_id: Optional[str] = "dev-user-01"
    session_id: Optional[str] = None
    topic: str
    score: int
    total_questions: int
    answers_json: Optional[Any] = None

@router.get("/summary")
async def get_progress_summary(user_id: Optional[str] = "dev-user-01", x_user_id: Optional[str] = Header(None)):
    uid = x_user_id or user_id or "dev-user-01"
    summary = await supabase_progress.get_user_progress_summary(uid)
    return summary

@router.post("/quiz")
async def submit_quiz(submission: QuizSubmission, x_user_id: Optional[str] = Header(None)):
    uid = x_user_id or submission.user_id or "dev-user-01"
    result = await supabase_progress.record_quiz_attempt(
        user_id=uid,
        topic=submission.topic,
        score=submission.score,
        total_questions=submission.total_questions,
        answers_json=submission.answers_json,
        session_id=submission.session_id,
    )
    return result

@router.get("/recommend")
async def get_recommendation(user_id: Optional[str] = "dev-user-01", x_user_id: Optional[str] = Header(None)):
    uid = x_user_id or user_id or "dev-user-01"
    rec = await supabase_progress.get_recommendation(uid)
    return rec

