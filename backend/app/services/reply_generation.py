
from sqlalchemy.orm import Session

from backend.app.models.conversation import Conversation
from backend.app.models.message import Message
from backend.app.models.reply_draft import ReplyDraft
from backend.app.services.ai_service import generate_reply
from backend.app.services.knowledge_retrieval import (
    retrieve_relevant_knowledge,
)


def generate_reply_draft(
    db: Session,
    conversation_id: int,
) -> ReplyDraft:
    # 1. Find the conversation.
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )

    if conversation is None:
        raise ValueError("Conversation not found.")

    # 2. Find the latest customer message.
    latest_customer_message = (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation_id,
            Message.sender_type == "customer",
        )
        .order_by(Message.created_at.desc(), Message.id.desc())
        .first()
    )

    if latest_customer_message is None:
        raise ValueError("No customer message found for this conversation.")
    
    # Include recent history so the model can avoid repeating questions.
    recent_messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc(), Message.id.desc())
        .limit(8)
        .all()
    )

    recent_messages.reverse()

    conversation_history = "\n".join(
        f"{message.sender_type.capitalize()}: {message.content}"
        for message in recent_messages
    )

    # 3. Retrieve policies for this conversation's brand only.
    policies = retrieve_relevant_knowledge(
        db=db,
        conversation=conversation,
        customer_message=latest_customer_message.content,
        limit=3,
    )

    # 4. Build the exact policy context supplied to Gemini.
    retrieved_context = "\n\n".join(
        f"Policy: {policy.title}\n"
        f"Category: {policy.category}\n"
        f"Content: {policy.content}"
        for policy in policies
    )

    # 5. Generate a reply using the brand and order details.
    brand_name = conversation.brand.name

    ai_response = generate_reply(
        customer_message=latest_customer_message.content,
        brand_name=brand_name,
        order_details=(
            f"Order number: {conversation.order_number or 'Not provided'}\n"
            f"Order status: {conversation.order_status}\n"
            f"Order details: {conversation.order_details}"
        ),
        retrieved_context=retrieved_context,
        conversation_history=conversation_history,
    )

    # 6. Save the generated response and retrieved context.
    draft = ReplyDraft(
        conversation_id=conversation_id,
        retrieved_context=(
            retrieved_context
            if retrieved_context
            else "No relevant policy was found."
        ),
        ai_response=ai_response,
        status="draft",
    )

    db.add(draft)
    db.commit()
    db.refresh(draft)

    return draft
