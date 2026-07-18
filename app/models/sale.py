"""Sale model."""

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Float, ForeignKey, String, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class SaleStatus(str, Enum):
    """Sale status enumeration."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Sale(Base):
    """
    Sale model.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to user
        brand: Brand name
        earning: Earning amount
        status: Sale status (pending, approved, rejected)
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = "sales"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    brand: Mapped[str] = mapped_column(String(100), nullable=False)
    earning: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=SaleStatus.PENDING.value, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # Composite index for advance payout queries
    __table_args__ = (
        Index("ix_sales_user_status", "user_id", "status"),
    )
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<Sale(id={self.id}, user_id={self.user_id}, brand={self.brand}, earning={self.earning}, status={self.status})>"
