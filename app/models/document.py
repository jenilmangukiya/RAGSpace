from email.policy import default
from operator import index
import uuid

from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.db.postgres import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    app_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("apps.id", ondelete="cascade"),
        nullable=False,
        index=True,
    )

    file_name: Mapped[str] = mapped_column(String(500), nullable=False)

    storage_path: Mapped[str] = mapped_column(String(1000), nullable=False)

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="uploaded")

    error_message: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    app = relationship("App", back_populates="documents")
