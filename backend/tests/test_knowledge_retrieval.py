
from backend.app.db.session import SessionLocal
from backend.app.models.conversation import Conversation
from backend.app.services.knowledge_retrieval import retrieve_relevant_knowledge


def test_retrieval_is_scoped_to_conversation_brand():
    db = SessionLocal()

    try:
        conversation = (
            db.query(Conversation)
            .filter(Conversation.brand_id == 1)
            .first()
        )
        assert conversation is not None

        results = retrieve_relevant_knowledge(
            db,
            conversation,
            "What is your shipping and delivery policy?",
        )

        assert results
        assert all(entry.brand_id == conversation.brand_id for entry in results)
        assert results[0].category == "shipping"
    finally:
        db.close()


def test_retrieval_returns_no_results_for_unrelated_message():
    db = SessionLocal()

    try:
        conversation = (
            db.query(Conversation)
            .filter(Conversation.brand_id == 1)
            .first()
        )
        assert conversation is not None

        results = retrieve_relevant_knowledge(
            db,
            conversation,
            "Can you tell me how to update my account profile?",
        )

        assert results == []
    finally:
        db.close()




def test_retrieval_excludes_inactive_policies():
    db = SessionLocal()

    try:
        conversation = (
            db.query(Conversation)
            .filter(Conversation.brand_id == 1)
            .first()
        )
        assert conversation is not None

        results = retrieve_relevant_knowledge(
            db,
            conversation,
            "I need help with garden furniture assembly instructions",
        )

        assert all(
            entry.is_active
            for entry in results
        )
        assert all(
            entry.title != "Garden Furniture Assembly"
            for entry in results
        )
    finally:
        db.close()



def test_retrieval_finds_damaged_item_policy_for_report_status_query():
    db = SessionLocal()

    try:
        conversation = (
            db.query(Conversation)
            .filter(Conversation.brand_id == 1)
            .first()
        )
        assert conversation is not None

        results = retrieve_relevant_knowledge(
            db,
            conversation,
            "I want to know the status of my damaged bottle report.",
        )

        assert results
        assert results[0].title == "Damaged Item Returns"
        assert all(
            entry.brand_id == conversation.brand_id
            for entry in results
        )
    finally:
        db.close()




def test_retrieval_returns_no_results_for_unrelated_email_change_query():
    db = SessionLocal()

    try:
        conversation = (
            db.query(Conversation)
            .filter(Conversation.brand_id == 2)
            .first()
        )
        assert conversation is not None

        results = retrieve_relevant_knowledge(
            db,
            conversation,
            "Can you help me change the email address on my account? "
        )

        assert results == []
    finally:
        db.close()
