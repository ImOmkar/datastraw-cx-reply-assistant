from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.session import base
from pgvector.sqlalchemy import Vector

class KnowledgeBaseEntry(base):
    __tablename__ = "knowledge_base_entries"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    brand_id: Mapped[int] = mapped_column(
        ForeignKey("brands.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    
    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(768),
        nullable=True,
    ) # new addition    

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    brand = relationship("Brand")