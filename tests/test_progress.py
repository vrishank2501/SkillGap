import pytest
from app.progress.supabase_progress import SupabaseProgressManager, supabase_progress

@pytest.mark.asyncio
async def test_progress_record_and_summary():
    user_id = "test-user-99"
    result = await supabase_progress.record_quiz_attempt(
        user_id=user_id,
        topic="Python Dictionaries",
        score=4,
        total_questions=5
    )
    assert result["percentage"] == 80.0

    summary = await supabase_progress.get_user_progress_summary(user_id)
    assert summary["quizzes_attempted"] >= 1
    assert "Python Dictionaries" in summary["completed_topics"]

    rec = await supabase_progress.get_recommendation(user_id)
    assert "recommendation_type" in rec


@pytest.mark.asyncio
async def test_memory_progress_is_isolated_by_user():
    manager = SupabaseProgressManager()
    await manager.record_quiz_attempt("user-a", "Biology", 5, 5)
    await manager.record_quiz_attempt("user-b", "Biology", 1, 5)

    user_a = await manager.get_user_progress_summary("user-a")
    user_b = await manager.get_user_progress_summary("user-b")

    assert user_a["quizzes_attempted"] == user_b["quizzes_attempted"] == 1
    assert user_a["average_score"] == 100.0
    assert user_b["average_score"] == 20.0
    assert user_a["completed_topics"] == ["Biology"]
    assert user_b["completed_topics"] == []

