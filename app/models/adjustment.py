"""Adjustment history model."""

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Float, ForeignKey, String, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class AdjustmentType(str, Enum):
    """Adjustment type enumeration."""
    RECOVERY = "recovery"
    REFUND = "refund"
    CREDIT = "credit"
    DEBIT = "debit"


class AdjustmentHistory(Base):
    """
    Adjustment history model.
    
    Tracks all balance adjustments including:
    - Recovery of advance payouts on rejected sales
    - Refunds for failed withdrawals/payouts
    - Manual credits/debits
    
    Attributes:
        id: Primary key
        user_id: Foreign key to user
        sale_id: Foreign key to sale (optional)
        withdrawal_id: Foreign key to withdrawal (optional)
        payout_id: Foreign key to payout (optional)
        type: Adjustment type
        amount: Adjustment amount (negative for debits)
        reason: Adjustment reason
        created_at: Creation timestamp
    """
    
    __tablename__ = "adjustment_history"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id"), nullable=True, index=True)
    withdrawal_id: Mapped[int] = mapped_column(ForeignKey("withdrawals.id"), nullable=True, index=True)
    payout_id: Mapped[int] = mapped_column(ForeignKey("payouts.id"), nullable=True, index=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index("ix_adjustments_user_created", "user_id", "created_at"),
    )
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<AdjustmentHistory(id={self.id}, user_id={self.user_id}, type={self.type}, amount={self.amount})>"
