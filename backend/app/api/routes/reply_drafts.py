import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from datetime import datetime, timezone

from backend.app.db.session import SessionLocal
from backend.app.models.conversation import Conversation
from backend.app.models.reply_draft import ReplyDraft
from backend.app.schemas.reply_draft import (
    ReplyDraftCreate,
    ReplyDraftResponse,
    ReplyDraftUpdate
)
from backend.app.services.reply_generation import generate_reply_draft

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reply-drafts", tags=["Reply Drafts"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




@router.post("/{draft_id}/approve", response_model=ReplyDraftResponse)
def approve_reply_draft(
    draft_id: int,
    db: Session = Depends(get_db),
):
    draft = db.query(ReplyDraft).filter(
        ReplyDraft.id == draft_id
    ).first()

    if draft is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reply draft not found.",
        )

    if draft.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only drafts can be approved.",
        )

    draft.final_response = draft.edited_response or draft.ai_response
    draft.status = "approved"
    draft.approved_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(draft)

    return draft




@router.post(
    "/generate/{conversation_id}",
    response_model=ReplyDraftResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_conversation_reply(
    conversation_id: int,
    db: Session = Depends(get_db),
):
    try:
        return generate_reply_draft(
            db=db,
            conversation_id=conversation_id,
        )
    except ValueError as exc:
        if str(exc) == "Conversation not found.":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        db.rollback()
        logger.exception("AI reply generation failed for conversation %s", conversation_id)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI reply generation failed. Please try again.",
        ) from exc


@router.post(
    "/",
    response_model=ReplyDraftResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_reply_draft(
    draft_data: ReplyDraftCreate,
    db: Session = Depends(get_db),
):
    conversation = db.query(Conversation).filter(
        Conversation.id == draft_data.conversation_id
    ).first()

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found.",
        )

    draft = ReplyDraft(
        conversation_id=draft_data.conversation_id,
        retrieved_context=draft_data.retrieved_context,
        ai_response=draft_data.ai_response,
    )

    db.add(draft)
    db.commit()
    db.refresh(draft)

    return draft


@router.get("/{draft_id}", response_model=ReplyDraftResponse)
def get_reply_draft(
    draft_id: int,
    db: Session = Depends(get_db),
):
    draft = db.query(ReplyDraft).filter(
        ReplyDraft.id == draft_id
    ).first()

    if draft is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reply draft not found.",
        )

    return draft


@router.get(
    "/conversation/{conversation_id}/latest",
    response_model=ReplyDraftResponse,
)
def get_latest_reply_draft(
    conversation_id: int,
    db: Session = Depends(get_db),
):
    draft = (
        db.query(ReplyDraft)
        .filter(ReplyDraft.conversation_id == conversation_id)
        .order_by(
            ReplyDraft.created_at.desc(),
            ReplyDraft.id.desc(),
        )
        .first()
    )

    if draft is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No reply draft found for this conversation.",
        )

    return draft



@router.get(
    "/conversation/{conversation_id}/latest-approved",
    response_model=ReplyDraftResponse,
)
def get_latest_approved_reply_draft(
    conversation_id: int,
    db: Session = Depends(get_db),
):
    draft = (
        db.query(ReplyDraft)
        .filter(
            ReplyDraft.conversation_id == conversation_id,
            ReplyDraft.status == "approved",
        )
        .order_by(
            ReplyDraft.approved_at.desc(),
            ReplyDraft.id.desc(),
        )
        .first()
    )

    if draft is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No approved reply found for this conversation.",
        )

    return draft



@router.put("/{draft_id}", response_model=ReplyDraftResponse)
def update_reply_draft(
    draft_id: int,
    draft_data: ReplyDraftUpdate,
    db: Session = Depends(get_db),
):
    draft = db.query(ReplyDraft).filter(
        ReplyDraft.id == draft_id
    ).first()

    if draft is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reply draft not found.",
        )

    if draft.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only drafts can be edited.",
        )

    draft.edited_response = draft_data.edited_response

    db.commit()
    db.refresh(draft)

    return draft
