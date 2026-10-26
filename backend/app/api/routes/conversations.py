
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import SessionLocal
from backend.app.models.brand import Brand
from backend.app.models.conversation import Conversation
from backend.app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
)

router = APIRouter(prefix="/conversations", tags=["Conversations"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_conversation(
    conversation_data: ConversationCreate,
    db: Session = Depends(get_db),
):
    brand = db.query(Brand).filter(
        Brand.id == conversation_data.brand_id
    ).first()

    if brand is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found.",
        )

    conversation = Conversation(
        brand_id=conversation_data.brand_id,
        customer_name=conversation_data.customer_name,
        customer_email=conversation_data.customer_email,
        order_number=conversation_data.order_number,
        order_status=conversation_data.order_status,
        order_details=conversation_data.order_details,
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


@router.get("/", response_model=list[ConversationResponse])
def list_conversations(db: Session = Depends(get_db)):
    return db.query(Conversation).order_by(Conversation.id.desc()).all()


@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
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

    return conversation
