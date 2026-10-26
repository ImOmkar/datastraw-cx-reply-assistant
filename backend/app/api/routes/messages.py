
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import SessionLocal
from backend.app.models.conversation import Conversation
from backend.app.models.message import Message
from backend.app.schemas.message import MessageCreate, MessageResponse

router = APIRouter(
    prefix="/conversations/{conversation_id}/messages",
    tags=["Messages"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_message(
    conversation_id: int,
    message_data: MessageCreate,
    db: Session = Depends(get_db),
):
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found.",
        )

    message = Message(
        conversation_id=conversation_id,
        sender_type=message_data.sender_type,
        content=message_data.content,
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


@router.get("/", response_model=list[MessageResponse])
def list_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
):
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found.",
        )

    return (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at, Message.id)
        .all()
    )
