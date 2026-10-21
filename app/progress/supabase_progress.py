import logging
from datetime import date
from typing import Dict, Any, List, Optional
from app.core.supabase import get_supabase_client

logger = logging.getLogger(__name__)

class SupabaseProgressManager:
    """
    Lightweight progress tracker backed directly by Supabase tables:
    - user_progress
    - quiz_attempts
    - daily_activity
    """

    def __init__(self):
        # In-memory storage fallback for local development without Supabase credentials
        self._memory_quizzes: List[Dict[str, Any]] = []
        self._memory_progress: Dict[tuple[str, str], Dict[str, Any]] = {}

    async def record_quiz_attempt(
        self,
        user_id: str,
        topic: str,
        score: int,
        total_questions: int,
        answers_json: Optional[Any] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        client = get_supabase_client()
        percentage = round((score / total_questions) * 100, 1) if total_questions > 0 else 0.0

        if client and user_id:
            try:
                # 1. Insert Quiz Attempt
                quiz_data = {
                    "user_id": user_id,
                    "session_id": session_id,
                    "topic": topic,
                    "score": score,
                    "total_questions": total_questions,
                    "answers_json": answers_json,
                }
                client.table("quiz_attempts").insert(quiz_data).execute()

                # 2. Upsert user_progress
                existing = (
                    client.table("user_progress")
                    .select("id, quizzes_taken, best_score")
                    .eq("user_id", user_id)
                    .eq("topic_name", topic)
                    .execute()
                )

                if existing.data and len(existing.data) > 0:
                    row = existing.data[0]
                    new_quizzes_taken = (row.get("quizzes_taken") or 0) + 1
                    best_score = max(row.get("best_score") or 0.0, percentage)
                    status = "completed" if best_score >= 70.0 else "in_progress"
                    client.table("user_progress").update({
                        "quizzes_taken": new_quizzes_taken,
                        "best_score": best_score,
                        "status": status,
                    }).eq("id", row["id"]).execute()
                else:
                    status = "completed" if percentage >= 70.0 else "in_progress"
                    client.table("user_progress").insert({
                        "user_id": user_id,
                        "topic_name": topic,
                        "status": status,
                        "quizzes_taken": 1,
                        "best_score": percentage,
                    }).execute()

                # 3. Log daily activity
                today_str = date.today().isoformat()
                daily = (
                    client.table("daily_activity")
                    .select("id, actions_count")
                    .eq("user_id", user_id)
                    .eq("activity_date", today_str)
                    .execute()
                )
                if daily.data and len(daily.data) > 0:
                    client.table("daily_activity").update({
                        "actions_count": (daily.data[0].get("actions_count") or 1) + 1
                    }).eq("id", daily.data[0]["id"]).execute()
                else:
                    client.table("daily_activity").insert({
                        "user_id": user_id,
                        "activity_date": today_str,
                        "actions_count": 1,
                    }).execute()

                return {"status": "saved", "percentage": percentage}

            except Exception as e:
                logger.error(f"Failed to record quiz in Supabase: {e}")

        # In-memory fallback
        attempt = {
            "user_id": user_id,
            "topic": topic,
            "score": score,
            "total_questions": total_questions,
            "percentage": percentage,
        }
        self._memory_quizzes.append(attempt)
        prog = self._memory_progress.setdefault(
            (user_id, topic),
            {"quizzes_taken": 0, "best_score": 0.0, "status": "in_progress"},
        )
        prog["quizzes_taken"] += 1
        prog["best_score"] = max(prog["best_score"], percentage)
        if prog["best_score"] >= 70.0:
            prog["status"] = "completed"

        return {"status": "saved_in_memory", "percentage": percentage}

    async def get_user_progress_summary(self, user_id: str) -> Dict[str, Any]:
        client = get_supabase_client()
        if client and user_id:
            try:
                prog_resp = client.table("user_progress").select("*").eq("user_id", user_id).execute()
                quiz_resp = client.table("quiz_attempts").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
                activity_resp = client.table("daily_activity").select("*").eq("user_id", user_id).execute()

                topics = prog_resp.data or []
                quizzes = quiz_resp.data or []
                streak_count = len(activity_resp.data or [])

                total_topics = len(topics)
                completed_topics = [t["topic_name"] for t in topics if t.get("status") == "completed"]
                avg_score = 0.0
                if quizzes:
                    scores = [q.get("score", 0) / max(q.get("total_questions", 1), 1) * 100 for q in quizzes]
                    avg_score = round(sum(scores) / len(scores), 1)

                return {
                    "total_topics_studied": total_topics,
                    "completed_topics": completed_topics,
                    "quizzes_attempted": len(quizzes),
                    "average_score": avg_score,
                    "active_streak_days": streak_count,
                    "recent_attempts": quizzes[:5],
                    "all_topics": topics,
                }
            except Exception as e:
                logger.error(f"Failed to fetch Supabase progress: {e}")

        # Fallback from memory
        user_progress = {
            topic: progress
            for (owner_id, topic), progress in self._memory_progress.items()
            if owner_id == user_id
        }
        user_quizzes = [quiz for quiz in self._memory_quizzes if quiz["user_id"] == user_id]
        total_topics = len(user_progress)
        completed = [topic for topic, data in user_progress.items() if data["status"] == "completed"]
        avg_score = 0.0
        if user_quizzes:
            avg_score = round(sum(quiz["percentage"] for quiz in user_quizzes) / len(user_quizzes), 1)

        return {
            "total_topics_studied": total_topics,
            "completed_topics": completed,
            "quizzes_attempted": len(user_quizzes),
            "average_score": avg_score,
            "active_streak_days": 1 if user_quizzes else 0,
            "recent_attempts": user_quizzes[-5:],
            "all_topics": [{"topic_name": topic, **progress} for topic, progress in user_progress.items()],
        }

    async def get_recommendation(self, user_id: str) -> Dict[str, Any]:
        summary = await self.get_user_progress_summary(user_id)
        topics = summary.get("all_topics", [])

        # 1. Find topics that need review (best_score < 70)
        weak_topics = [t for t in topics if t.get("best_score", 0) < 70.0]
        if weak_topics:
            target = weak_topics[0]
            return {
                "recommendation_type": "review_weak_area",
                "topic": target.get("topic_name"),
                "reason": f"Your current score on {target.get('topic_name')} is {target.get('best_score')}%. Let's practice and strengthen it.",
                "suggested_command": f"/explain {target.get('topic_name')} beginner",
            }

        # 2. Find in-progress topics
        in_progress = [t for t in topics if t.get("status") == "in_progress"]
        if in_progress:
            target = in_progress[0]
            return {
                "recommendation_type": "complete_topic",
                "topic": target.get("topic_name"),
                "reason": f"You started {target.get('topic_name')}. Take a quiz to verify your understanding.",
                "suggested_command": f"/quiz {target.get('topic_name')} 3",
            }

        # 3. Default recommendation
        return {
            "recommendation_type": "new_topic",
            "topic": "Core Fundamentals",
            "reason": "You're in great shape! Explore a new topic or upload fresh notes to continue your streak.",
            "suggested_command": "/explain Core Fundamentals beginner",
        }

supabase_progress = SupabaseProgressManager()

