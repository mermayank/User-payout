"""Adjustment history repository."""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.adjustment import AdjustmentHistory, AdjustmentType
from app.repositories.base import BaseRepository


class AdjustmentRepository(BaseRepository[AdjustmentHistory]):
    """Repository for AdjustmentHistory model operations."""
    
    def __init__(self) -> None:
        """Initialize adjustment repository."""
        super().__init__(AdjustmentHistory)
    
    def get_by_user(
        self, 
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[AdjustmentHistory]:
        """
        Get adjustments by user ID.
        
        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of adjustments
        """
        return db.query(AdjustmentHistory)\
            .filter(AdjustmentHistory.user_id == user_id)\
            .order_by(AdjustmentHistory.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def get_by_sale(self, db: Session, sale_id: int) -> List[AdjustmentHistory]:
        """
        Get adjustments by sale ID.
        
        Args:
            db: Database session
            sale_id: Sale ID
            
        Returns:
            List of adjustments
        """
        return db.query(AdjustmentHistory)\
            .filter(AdjustmentHistory.sale_id == sale_id)\
            .all()
    
    def get_by_withdrawal(
        self, 
        db: Session, 
        withdrawal_id: int
    ) -> List[AdjustmentHistory]:
        """
        Get adjustments by withdrawal ID.
        
        Args:
            db: Database session
            withdrawal_id: Withdrawal ID
            
        Returns:
            List of adjustments
        """
        return db.query(AdjustmentHistory)\
            .filter(AdjustmentHistory.withdrawal_id == withdrawal_id)\
            .all()
    
    def get_by_payout(self, db: Session, payout_id: int) -> List[AdjustmentHistory]:
        """
        Get adjustments by payout ID.
        
        Args:
            db: Database session
            payout_id: Payout ID
            
        Returns:
            List of adjustments
        """
        return db.query(AdjustmentHistory)\
            .filter(AdjustmentHistory.payout_id == payout_id)\
            .all()
    
    def create_recovery(
        self,
        db: Session,
        user_id: int,
        sale_id: Optional[int],
        withdrawal_id: Optional[int],
        payout_id: Optional[int],
        amount: float,
        reason: str
    ) -> AdjustmentHistory:
        """
        Create a recovery adjustment.
        
        Args:
            db: Database session
            user_id: User ID
            sale_id: Optional sale ID
            withdrawal_id: Optional withdrawal ID
            payout_id: Optional payout ID
            amount: Recovery amount (negative)
            reason: Recovery reason
            
        Returns:
            Created adjustment
        """
        return self.create(
            db,
            user_id=user_id,
            sale_id=sale_id,
            withdrawal_id=withdrawal_id,
            payout_id=payout_id,
            type=AdjustmentType.RECOVERY.value,
            amount=amount,
            reason=reason
        )
