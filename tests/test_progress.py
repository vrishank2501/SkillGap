import pytest
from app.progress.supabase_progress import supabase_progress

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

