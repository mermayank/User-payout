"""Sale schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.sale import SaleStatus


class SaleBase(BaseModel):
    """Base sale schema."""
    
    brand: str = Field(..., min_length=1, max_length=100, description="Brand name")
    earning: float = Field(..., gt=0, description="Earning amount")


class SaleCreate(SaleBase):
    """Schema for creating a sale."""
    
    user_id: int = Field(..., description="User ID")


class SaleUpdate(BaseModel):
    """Schema for updating a sale."""
    
    status: SaleStatus = Field(..., description="Sale status")


class SaleResponse(SaleBase):
    """Schema for sale response."""
    
    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        """Pydantic config."""
        from_attributes = True


class ReconcileRequest(BaseModel):
    """Schema for reconciliation request."""
    
    sale_id: int = Field(..., description="Sale ID to reconcile")
    status: SaleStatus = Field(..., description="New status (approved or rejected)")
