from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.session import base


class Conversation(base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    brand_id: Mapped[int] = mapped_column(
        ForeignKey("brands.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    customer_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    customer_email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    order_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    order_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    order_details: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="open",
        nullable=False,
    )

    brand = relationship("Brand")
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )