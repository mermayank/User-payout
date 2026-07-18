"""Withdrawal model."""

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Float, ForeignKey, String, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class WithdrawalStatus(str, Enum):
    """Withdrawal status enumeration."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class Withdrawal(Base):
    """
    Withdrawal model.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to user
        amount: Withdrawal amount
        status: Withdrawal status
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = "withdrawals"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=WithdrawalStatus.PENDING.value, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    __table_args__ = (
        Index("ix_withdrawals_user_created", "user_id", "created_at"),
    )
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<Withdrawal(id={self.id}, user_id={self.user_id}, amount={self.amount}, status={self.status})>"
