"""User repository."""

from typing import Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model operations."""
    
    def __init__(self) -> None:
        """Initialize user repository."""
        super().__init__(User)
    
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            db: Database session
            email: User email
            
        Returns:
            User if found, None otherwise
        """
        return db.query(User).filter(User.email == email).first()
    
    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            db: Database session
            username: Username
            
        Returns:
            User if found, None otherwise
        """
        return db.query(User).filter(User.username == username).first()
    
    def update_balance(
        self, 
        db: Session, 
        user: User, 
        withdrawable_amount: float,
        earnings_amount: float
    ) -> User:
        """
        Update user balance.
        
        Args:
            db: Database session
            user: User to update
            withdrawable_amount: Amount to add to withdrawable balance
            earnings_amount: Amount to add to total earnings
            
        Returns:
            Updated user
        """
        user.withdrawable_balance += withdrawable_amount
        user.total_earnings += earnings_amount
        db.commit()
        db.refresh(user)
        return user
