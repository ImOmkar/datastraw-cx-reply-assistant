

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.conversation import Conversation
from backend.app.models.knowledge_base import KnowledgeBaseEntry
from backend.app.services.embedding_service import generate_embedding

from backend.app.services.ai_service import rewrite_query, rerank_policies

# Cosine distance ranges from 0 (identical direction) upward.
MAX_COSINE_DISTANCE = 0.42


def retrieve_relevant_knowledge(
    db: Session,
    conversation: Conversation,
    customer_message: str,
    limit: int = 3,
) -> list[KnowledgeBaseEntry]:
    """
    Retrieve semantically relevant active policies for the
    conversation's brand using PostgreSQL pgvector.
    """
    
    if not customer_message or not customer_message.strip() or limit <= 0:
        return []

    search_query = rewrite_query(customer_message)

    query_embedding = generate_embedding(
        search_query,
        task_type="RETRIEVAL_QUERY",
    )
    
    distance = KnowledgeBaseEntry.embedding.cosine_distance(
        query_embedding
    ).label("cosine_distance")

    statement = (
        select(KnowledgeBaseEntry, distance)
        .where(
            KnowledgeBaseEntry.brand_id == conversation.brand_id,
            KnowledgeBaseEntry.is_active.is_(True),
            KnowledgeBaseEntry.embedding.is_not(None),
        )
        .order_by(distance, KnowledgeBaseEntry.id)
        .limit(limit)
    )

    results = db.execute(statement).all()
    

    relevant_entries = [
        entry
        for entry, cosine_distance in results
        if cosine_distance <= MAX_COSINE_DISTANCE
    ]
    

    if not relevant_entries:
        return []

    policies = [
        {
            "id": entry.id,
            "category": entry.category,
            "title": entry.title,
            "content": entry.content,
        }
        for entry in relevant_entries
    ]

    reranked_policies = rerank_policies(search_query, policies)
    
    entries_by_id = {
        entry.id: entry
        for entry in relevant_entries
    }

    return [
        entries_by_id[policy["id"]]
        for policy in reranked_policies
        if policy["id"] in entries_by_id
    ]