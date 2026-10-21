from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

from app.main import app


client = TestClient(app)


def test_protected_api_rejects_missing_bearer_token():
    response = client.get("/api/providers/models")

    assert response.status_code == 401


def test_protected_api_rejects_invalid_bearer_token():
    with patch("app.main.get_authenticated_user", side_effect=ValueError("invalid token")):
        response = client.get(
            "/api/providers/models",
            headers={"Authorization": "Bearer invalid-token"},
        )

    assert response.status_code == 401


def test_progress_uses_authenticated_user_instead_of_query_parameter():
    with (
        patch("app.main.get_authenticated_user", return_value=SimpleNamespace(id="trusted-user")),
        patch(
            "app.api.progress.supabase_progress.get_user_progress_summary",
            new_callable=AsyncMock,
            return_value={"total_topics_studied": 0},
        ) as get_summary,
    ):
        response = client.get(
            "/api/progress/summary?user_id=attacker-user",
            headers={"Authorization": "Bearer valid-token"},
        )

    assert response.status_code == 200
    get_summary.assert_awaited_once_with("trusted-user")