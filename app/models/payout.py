"""Payout model."""

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Float, ForeignKey, String, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class PayoutStatus(str, Enum):
    """Payout status enumeration."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class PayoutType(str, Enum):
    """Payout type enumeration."""
    ADVANCE = "advance"
    RECONCILIATION = "reconciliation"


class Payout(Base):
    """
    Payout model.
    
    Attributes:
        id: Primary key
        sale_id: Foreign key to sale
        user_id: Foreign key to user
        type: Payout type (advance, reconciliation)
        amount: Payout amount
        status: Payout status
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = "payouts"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=PayoutStatus.PENDING.value, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # Ensure one advance payout per sale
    __table_args__ = (
        UniqueConstraint("sale_id", "type", name="uq_sale_payout_type"),
        Index("ix_payouts_user_status", "user_id", "status"),
    )
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<Payout(id={self.id}, sale_id={self.sale_id}, type={self.type}, amount={self.amount}, status={self.status})>"
