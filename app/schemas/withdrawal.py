"""Withdrawal schemas."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.withdrawal import WithdrawalStatus


class WithdrawalBase(BaseModel):
    """Base withdrawal schema."""
    
    user_id: int = Field(..., description="User ID")
    amount: float = Field(..., gt=0, description="Withdrawal amount")


class WithdrawalCreate(WithdrawalBase):
    """Schema for creating a withdrawal."""
    
    pass


class WithdrawalUpdate(BaseModel):
    """Schema for updating a withdrawal."""
    
    status: WithdrawalStatus = Field(..., description="Withdrawal status")


class WithdrawalResponse(WithdrawalBase):
    """Schema for withdrawal response."""
    
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        """Pydantic config."""
        from_attributes = True
