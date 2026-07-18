"""Sale repository."""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.sale import Sale, SaleStatus
from app.repositories.base import BaseRepository


class SaleRepository(BaseRepository[Sale]):
    """Repository for Sale model operations."""
    
    def __init__(self) -> None:
        """Initialize sale repository."""
        super().__init__(Sale)
    
    def get_by_user(
        self, 
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Sale]:
        """
        Get sales by user ID.
        
        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of sales
        """
        return db.query(Sale)\
            .filter(Sale.user_id == user_id)\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def get_pending_sales(
        self, 
        db: Session, 
        user_id: Optional[int] = None
    ) -> List[Sale]:
        """
        Get pending sales.
        
        Args:
            db: Database session
            user_id: Optional user ID to filter by
            
        Returns:
            List of pending sales
        """
        query = db.query(Sale).filter(Sale.status == SaleStatus.PENDING.value)
        if user_id:
            query = query.filter(Sale.user_id == user_id)
        return query.all()
    
    def get_by_status(
        self, 
        db: Session, 
        status: SaleStatus, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Sale]:
        """
        Get sales by status.
        
        Args:
            db: Database session
            status: Sale status
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of sales
        """
        return db.query(Sale)\
            .filter(Sale.status == status.value)\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def update_status(self, db: Session, sale: Sale, status: SaleStatus) -> Sale:
        """
        Update sale status.
        
        Args:
            db: Database session
            sale: Sale to update
            status: New status
            
        Returns:
            Updated sale
        """
        sale.status = status.value
        db.commit()
        db.refresh(sale)
        return sale
