
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api.routes import reply_drafts


client = TestClient(app)


def test_generate_reply_returns_502_when_ai_generation_fails(monkeypatch):
    def fake_generate_reply_draft(db, conversation_id):
        raise RuntimeError("Sensitive internal error details")

    monkeypatch.setattr(
        reply_drafts,
        "generate_reply_draft",
        fake_generate_reply_draft,
    )

    response = client.post("/reply-drafts/generate/1")

    assert response.status_code == 502
    assert response.json() == {
        "detail": "AI reply generation failed. Please try again."
    }
    assert "Sensitive internal error details" not in response.text
