"""User schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""
    
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=100, description="Username")


class UserCreate(UserBase):
    """Schema for creating a user."""
    
    pass


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)


class UserResponse(UserBase):
    """Schema for user response."""
    
    id: int
    withdrawable_balance: float = Field(..., ge=0, description="Available balance for withdrawal")
    total_earnings: float = Field(..., ge=0, description="Total earnings from sales")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        """Pydantic config."""
        from_attributes = True


class BalanceResponse(BaseModel):
    """Schema for balance response."""
    
    user_id: int
    withdrawable_balance: float
    total_earnings: float
    
    class Config:
        """Pydantic config."""
        from_attributes = True
