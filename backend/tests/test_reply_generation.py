
from backend.app.db.session import SessionLocal
from backend.app.models.conversation import Conversation
from backend.app.models.message import Message
from backend.app.services import reply_generation


def test_generate_reply_passes_conversation_history(monkeypatch):
    db = SessionLocal()
    conversation_id = None

    captured = {}

    def fake_retrieve_relevant_knowledge(
        db, conversation, customer_message, limit=3
    ):
        return []

    def fake_generate_reply(
        customer_message,
        brand_name,
        order_details,
        retrieved_context,
        conversation_history="",
    ):
        captured["customer_message"] = customer_message
        captured["brand_name"] = brand_name
        captured["order_details"] = order_details
        captured["retrieved_context"] = retrieved_context
        captured["conversation_history"] = conversation_history
        return "We will help you check the status."

    monkeypatch.setattr(
        reply_generation,
        "retrieve_relevant_knowledge",
        fake_retrieve_relevant_knowledge,
    )
    monkeypatch.setattr(
        reply_generation,
        "generate_reply",
        fake_generate_reply,
    )

    try:
        existing_conversation = (
            db.query(Conversation)
            .filter(Conversation.brand_id == 1)
            .first()
        )
        assert existing_conversation is not None

        conversation = Conversation(
            brand_id=existing_conversation.brand_id,
            customer_name="Reply Generation Test",
            customer_email="reply-generation-test@example.com",
            order_number="TEST-HISTORY-001",
            order_status="delivered",
            order_details="A bottle arrived damaged.",
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        conversation_id = conversation.id

        db.add_all(
            [
                Message(
                    conversation_id=conversation_id,
                    sender_type="customer",
                    content="My bottle arrived broken.",
                ),
                Message(
                    conversation_id=conversation_id,
                    sender_type="agent",
                    content="Could you share the order number?",
                ),
                Message(
                    conversation_id=conversation_id,
                    sender_type="customer",
                    content="The order number is TEST-HISTORY-001.",
                ),
                Message(
                    conversation_id=conversation_id,
                    sender_type="customer",
                    content="What is the status of my damaged item report?",
                ),
            ]
        )
        db.commit()

        draft = reply_generation.generate_reply_draft(
            db=db,
            conversation_id=conversation_id,
        )

        assert draft.ai_response == "We will help you check the status."
        assert captured["customer_message"] == (
            "What is the status of my damaged item report?"
        )
        assert captured["brand_name"] == existing_conversation.brand.name
        assert "TEST-HISTORY-001" in captured["order_details"]

        history = captured["conversation_history"]
        assert "Customer: My bottle arrived broken." in history
        assert "Agent: Could you share the order number?" in history
        assert "Customer: The order number is TEST-HISTORY-001." in history
        assert "Customer: What is the status of my damaged item report?" in history

        assert history.index("Customer: My bottle arrived broken.") < (
            history.index("Agent: Could you share the order number?")
        )
        assert captured["retrieved_context"] == ""

    finally:
        if conversation_id is not None:
            db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).delete(synchronize_session=False)

            db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).delete(synchronize_session=False)

            db.commit()

        db.close()




def test_generate_reply_draft_raises_for_missing_conversation():
    db = SessionLocal()

    try:
        import pytest

        with pytest.raises(ValueError, match="Conversation not found."):
            reply_generation.generate_reply_draft(
                db=db,
                conversation_id=-999999,
            )
    finally:
        db.close()
