
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import SessionLocal
from backend.app.models.brand import Brand
from backend.app.models.knowledge_base import KnowledgeBaseEntry
from backend.app.schemas.knowledge_base import (
    KnowledgeBaseEntryCreate,
    KnowledgeBaseEntryResponse,
    KnowledgeBaseEntryUpdate
)
from backend.app.services.embedding_service import generate_embedding

router = APIRouter(
    prefix="/knowledge-base",
    tags=["Knowledge Base"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/",
    response_model=KnowledgeBaseEntryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_knowledge_base_entry(
    entry_data: KnowledgeBaseEntryCreate,
    db: Session = Depends(get_db),
):
    brand = (
        db.query(Brand)
        .filter(Brand.id == entry_data.brand_id)
        .first()
    )

    if brand is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found.",
        )

    
    policy_text = (
        f"Brand: {brand.id} - {brand.name}\n"
        f"Policy title: {entry_data.title}\n"
        f"Category: {entry_data.category}\n"
        f"Policy content: {entry_data.content}"
    )

    embedding = generate_embedding(
        policy_text,
        task_type="RETRIEVAL_DOCUMENT",
    )

    entry = KnowledgeBaseEntry(
        brand_id=entry_data.brand_id,
        title=entry_data.title,
        category=entry_data.category,
        content=entry_data.content,
        embedding=embedding,
    )

    db.add(entry)
    db.commit()
    db.refresh(entry)


    return entry



@router.get(
    "/brand/{brand_id}",
    response_model=list[KnowledgeBaseEntryResponse],
)
def list_brand_knowledge_base_entries(
    brand_id: int,
    db: Session = Depends(get_db),
):
    brand = db.query(Brand).filter(Brand.id == brand_id).first()

    if brand is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found.",
        )

    return (
        db.query(KnowledgeBaseEntry)
        .filter(
            KnowledgeBaseEntry.brand_id == brand_id,
            KnowledgeBaseEntry.is_active.is_(True),
        )
        .order_by(KnowledgeBaseEntry.id)
        .all()
    )



@router.get(
    "/{entry_id}",
    response_model=KnowledgeBaseEntryResponse,
)
def get_knowledge_base_entry(
    entry_id: int,
    db: Session = Depends(get_db),
):
    entry = (
        db.query(KnowledgeBaseEntry)
        .filter(KnowledgeBaseEntry.id == entry_id)
        .first()
    )

    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base entry not found.",
        )

    return entry




@router.put(
    "/{entry_id}",
    response_model=KnowledgeBaseEntryResponse,
)
def update_knowledge_base_entry(
    entry_id: int,
    entry_data: KnowledgeBaseEntryUpdate,
    db: Session = Depends(get_db),
):
    entry = (
        db.query(KnowledgeBaseEntry)
        .filter(KnowledgeBaseEntry.id == entry_id)
        .first()
    )

    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base entry not found.",
        )

    
    policy_text = (
        f"Brand: {entry.brand_id} - {entry.brand.name}\n"
        f"Policy title: {entry_data.title}\n"
        f"Category: {entry_data.category}\n"
        f"Policy content: {entry_data.content}"
    )

    embedding = generate_embedding(
        policy_text,
        task_type="RETRIEVAL_DOCUMENT",
    )

    entry.title = entry_data.title
    entry.category = entry_data.category
    entry.content = entry_data.content
    entry.embedding = embedding

    db.commit()
    db.refresh(entry)


    return entry



@router.patch(
    "/{entry_id}/deactivate",
    response_model=KnowledgeBaseEntryResponse,
)
def deactivate_knowledge_base_entry(
    entry_id: int,
    db: Session = Depends(get_db),
):
    entry = (
        db.query(KnowledgeBaseEntry)
        .filter(KnowledgeBaseEntry.id == entry_id)
        .first()
    )

    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base entry not found.",
        )

    entry.is_active = False

    db.commit()
    db.refresh(entry)

    return entry
