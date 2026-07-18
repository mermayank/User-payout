"""Payout schemas."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.payout import PayoutStatus, PayoutType


class PayoutBase(BaseModel):
    """Base payout schema."""
    
    sale_id: int = Field(..., description="Sale ID")
    user_id: int = Field(..., description="User ID")
    type: PayoutType = Field(..., description="Payout type")
    amount: float = Field(..., gt=0, description="Payout amount")


class PayoutCreate(PayoutBase):
    """Schema for creating a payout."""
    
    pass


class PayoutUpdate(BaseModel):
    """Schema for updating a payout."""
    
    status: PayoutStatus = Field(..., description="Payout status")


class PayoutResponse(PayoutBase):
    """Schema for payout response."""
    
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        """Pydantic config."""
        from_attributes = True


class AdvancePayoutRequest(BaseModel):
    """Schema for advance payout request."""
    
    sale_id: int = Field(..., description="Sale ID for advance payout")
