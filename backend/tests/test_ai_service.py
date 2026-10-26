
from types import SimpleNamespace

from backend.app.services import ai_service


def test_generate_reply_passes_history_and_context_to_gemini(monkeypatch):
    captured = {}

    def fake_generate_content(*, model, contents, config):
        captured["model"] = model
        captured["contents"] = contents
        captured["config"] = config

        return SimpleNamespace(
            text="The current status cannot be verified.",
            candidates=[
                SimpleNamespace(finish_reason="STOP")
            ],
        )

    monkeypatch.setattr(
        ai_service.client.models,
        "generate_content",
        fake_generate_content,
    )

    reply = ai_service.generate_reply(
        customer_message="What is the status of my damaged bottle report?",
        brand_name="Acme Home",
        order_details="Order number: ORD-1001",
        retrieved_context="Damaged Item Returns: report within 7 days.",
        conversation_history="Customer: My bottle arrived broken.",
    )

    assert reply == "The current status cannot be verified."
    assert "Customer: My bottle arrived broken." in captured["contents"]
    assert "Damaged Item Returns" in captured["contents"]
    assert "ORD-1001" in captured["contents"]
    assert captured["config"].system_instruction



def test_rewrite_query_excludes_explicitly_unrelated_topic(monkeypatch):
    def fake_generate_content(*, model, contents, config):
        return SimpleNamespace(
            text="change account email address",
        )

    monkeypatch.setattr(
        ai_service.client.models,
        "generate_content",
        fake_generate_content,
    )

    query = ai_service.rewrite_query(
        "Can you help me change the email address on my account? "
        "This is unrelated to my damaged bottle."
    )

    assert query == "change account email address"
    assert "damaged bottle" not in query.lower()
    
    
    
def test_rerank_policies_excludes_irrelevant_policy(monkeypatch):
    def fake_generate_content(*, model, contents, config):
        return SimpleNamespace(text="1, 2")

    monkeypatch.setattr(
        ai_service.client.models,
        "generate_content",
        fake_generate_content,
    )

    policies = [
        {
            "id": 1,
            "category": "returns",
            "title": "Damaged Item Returns",
            "content": "Report damage within 7 days and provide photos.",
        },
        {
            "id": 2,
            "category": "refunds",
            "title": "Refund Policy",
            "content": "Refund eligibility is confirmed after review.",
        },
        {
            "id": 3,
            "category": "cancellation",
            "title": "Order Cancellation Policy",
            "content": "Orders can be cancelled before dispatch.",
        },
    ]

    result = ai_service.rerank_policies(
        "My order arrived damaged. What is your return policy?",
        policies,
    )

    assert [policy["id"] for policy in result] == [1, 2]