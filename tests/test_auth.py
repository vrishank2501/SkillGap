from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_api_is_available_without_authentication():
    response = client.get("/api/providers/models")

    assert response.status_code == 200


def test_auth_config_endpoint_is_removed():
    response = client.get("/api/auth/config")

    assert response.status_code == 404


def test_progress_is_available_without_authentication():
    with patch(
        "app.api.progress.supabase_progress.get_user_progress_summary",
        new_callable=AsyncMock,
        return_value={"total_topics_studied": 0},
    ) as get_summary:
        response = client.get("/api/progress/summary")

    assert response.status_code == 200
    get_summary.assert_awaited_once_with("dev-user-01")


def test_home_page_serves_workspace_without_login_screen():
    response = client.get("/")

    assert response.status_code == 200
    assert "MAIN WORKSPACE" in response.text
    assert 'id="auth-screen"' not in response.text
