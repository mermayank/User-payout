"""Withdrawal repository."""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.withdrawal import Withdrawal, WithdrawalStatus
from app.repositories.base import BaseRepository
from app.core.config import settings


class WithdrawalRepository(BaseRepository[Withdrawal]):
    """Repository for Withdrawal model operations."""
    
    def __init__(self) -> None:
        """Initialize withdrawal repository."""
        super().__init__(Withdrawal)
    
    def get_by_user(
        self, 
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Withdrawal]:
        """
        Get withdrawals by user ID.
        
        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of withdrawals
        """
        return db.query(Withdrawal)\
            .filter(Withdrawal.user_id == user_id)\
            .order_by(Withdrawal.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def get_last_withdrawal(
        self, 
        db: Session, 
        user_id: int
    ) -> Optional[Withdrawal]:
        """
        Get last withdrawal for a user.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Last withdrawal if found, None otherwise
        """
        return db.query(Withdrawal)\
            .filter(Withdrawal.user_id == user_id)\
            .order_by(Withdrawal.created_at.desc())\
            .first()
    
    def can_withdraw(self, db: Session, user_id: int) -> bool:
        """
        Check if user can withdraw (24-hour cooldown).
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            True if user can withdraw, False otherwise
        """
        last_withdrawal = self.get_last_withdrawal(db, user_id)
        if not last_withdrawal:
            return True
        
        cooldown_period = timedelta(hours=settings.WITHDRAWAL_COOLDOWN_HOURS)
        time_since_last = datetime.utcnow() - last_withdrawal.created_at
        
        return time_since_last >= cooldown_period
    
    def update_status(
        self, 
        db: Session, 
        withdrawal: Withdrawal, 
        status: WithdrawalStatus
    ) -> Withdrawal:
        """
        Update withdrawal status.
        
        Args:
            db: Database session
            withdrawal: Withdrawal to update
            status: New status
            
        Returns:
            Updated withdrawal
        """
        withdrawal.status = status.value
        db.commit()
        db.refresh(withdrawal)
        return withdrawal
    
    def get_failed_withdrawals(self, db: Session) -> List[Withdrawal]:
        """
        Get failed withdrawals for recovery.
        
        Args:
            db: Database session
            
        Returns:
            List of failed withdrawals
        """
        return db.query(Withdrawal)\
            .filter(Withdrawal.status == WithdrawalStatus.FAILED.value)\
            .all()
