from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from app.db.postgres import Base
import uuid
from sqlalchemy import String, DateTime, func, Boolean
from datetime import datetime


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))

    stripe_customer_id: Mapped[str] = mapped_column(String(), nullable=True)

    stripe_subscription_id: Mapped[str] = mapped_column(String(), nullable=True)

    stripe_price_id: Mapped[str] = mapped_column(String(), nullable=True)

    plan_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="trial",
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
    )

    trial_ends_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    current_period_start: Mapped[datetime] = mapped_column(DateTime(), nullable=True)

    current_period_end: Mapped[datetime] = mapped_column(DateTime(), nullable=True)

    cancel_at_period_end: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
