"""Adjustment schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.adjustment import AdjustmentType


class AdjustmentBase(BaseModel):
    """Base adjustment schema."""
    
    user_id: int = Field(..., description="User ID")
    sale_id: Optional[int] = Field(None, description="Related sale ID")
    withdrawal_id: Optional[int] = Field(None, description="Related withdrawal ID")
    payout_id: Optional[int] = Field(None, description="Related payout ID")
    type: AdjustmentType = Field(..., description="Adjustment type")
    amount: float = Field(..., description="Adjustment amount (negative for debits)")
    reason: str = Field(..., min_length=1, max_length=500, description="Adjustment reason")


class AdjustmentCreate(AdjustmentBase):
    """Schema for creating an adjustment."""
    
    pass


class AdjustmentResponse(AdjustmentBase):
    """Schema for adjustment response."""
    
    id: int
    created_at: datetime
    
    class Config:
        """Pydantic config."""
        from_attributes = True
