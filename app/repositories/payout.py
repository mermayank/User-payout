"""Payout repository."""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.payout import Payout, PayoutStatus, PayoutType
from app.repositories.base import BaseRepository


class PayoutRepository(BaseRepository[Payout]):
    """Repository for Payout model operations."""
    
    def __init__(self) -> None:
        """Initialize payout repository."""
        super().__init__(Payout)
    
    def get_by_user(
        self, 
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Payout]:
        """
        Get payouts by user ID.
        
        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of payouts
        """
        return db.query(Payout)\
            .filter(Payout.user_id == user_id)\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def get_by_sale(self, db: Session, sale_id: int) -> List[Payout]:
        """
        Get payouts by sale ID.
        
        Args:
            db: Database session
            sale_id: Sale ID
            
        Returns:
            List of payouts
        """
        return db.query(Payout).filter(Payout.sale_id == sale_id).all()
    
    def get_advance_payout_for_sale(
        self, 
        db: Session, 
        sale_id: int
    ) -> Optional[Payout]:
        """
        Get advance payout for a specific sale.
        
        Args:
            db: Database session
            sale_id: Sale ID
            
        Returns:
            Payout if found, None otherwise
        """
        return db.query(Payout)\
            .filter(Payout.sale_id == sale_id)\
            .filter(Payout.type == PayoutType.ADVANCE.value)\
            .first()
    
    def get_by_status(
        self, 
        db: Session, 
        status: PayoutStatus, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Payout]:
        """
        Get payouts by status.
        
        Args:
            db: Database session
            status: Payout status
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of payouts
        """
        return db.query(Payout)\
            .filter(Payout.status == status.value)\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def update_status(self, db: Session, payout: Payout, status: PayoutStatus) -> Payout:
        """
        Update payout status.
        
        Args:
            db: Database session
            payout: Payout to update
            status: New status
            
        Returns:
            Updated payout
        """
        payout.status = status.value
        db.commit()
        db.refresh(payout)
        return payout
    
    def get_failed_payouts(self, db: Session) -> List[Payout]:
        """
        Get failed payouts for recovery.
        
        Args:
            db: Database session
            
        Returns:
            List of failed payouts
        """
        return db.query(Payout)\
            .filter(Payout.status == PayoutStatus.FAILED.value)\
            .all()
