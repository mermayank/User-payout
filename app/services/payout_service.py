"""Payout service for advance payout processing."""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.sale import Sale, SaleStatus
from app.models.payout import Payout, PayoutStatus, PayoutType
from app.models.user import User
from app.repositories.sale import SaleRepository
from app.repositories.payout import PayoutRepository
from app.repositories.user import UserRepository
from app.repositories.adjustment import AdjustmentRepository
from app.core.config import settings
from app.core.exceptions import (
    SaleNotFoundError,
    PayoutAlreadyExistsError,
    InvalidSaleStatusError,
    InsufficientBalanceError
)


class PayoutService:
    """
    Service for payout operations.
    
    Handles advance payout processing with idempotency guarantees.
    """
    
    def __init__(
        self,
        sale_repo: SaleRepository,
        payout_repo: PayoutRepository,
        user_repo: UserRepository,
        adjustment_repo: AdjustmentRepository
    ) -> None:
        """
        Initialize payout service.
        
        Args:
            sale_repo: Sale repository
            payout_repo: Payout repository
            user_repo: User repository
            adjustment_repo: Adjustment repository
        """
        self.sale_repo = sale_repo
        self.payout_repo = payout_repo
        self.user_repo = user_repo
        self.adjustment_repo = adjustment_repo
    
    def process_advance_payout(
        self, 
        db: Session, 
        sale_id: int
    ) -> Payout:
        """
        Process advance payout for a pending sale.
        
        This method is idempotent - running it multiple times for the same sale
        will not create duplicate payouts.
        
        Args:
            db: Database session
            sale_id: Sale ID
            
        Returns:
            Created or existing payout
            
        Raises:
            SaleNotFoundError: If sale doesn't exist
            InvalidSaleStatusError: If sale is not pending
            PayoutAlreadyExistsError: If advance payout already exists
        """
        # Get sale
        sale = self.sale_repo.get(db, sale_id)
        if not sale:
            raise SaleNotFoundError(f"Sale with id {sale_id} not found")
        
        # Validate sale status
        if sale.status != SaleStatus.PENDING.value:
            raise InvalidSaleStatusError(
                f"Sale must be pending to process advance payout, current status: {sale.status}"
            )
        
        # Check if advance payout already exists (idempotency)
        existing_payout = self.payout_repo.get_advance_payout_for_sale(db, sale_id)
        if existing_payout:
            raise PayoutAlreadyExistsError(
                f"Advance payout already exists for sale {sale_id}"
            )
        
        # Calculate advance amount (10% of earning)
        advance_amount = sale.earning * settings.ADVANCE_PAYOUT_PERCENTAGE
        
        # Create payout in transaction
        try:
            # Create payout record
            payout = self.payout_repo.create(
                db,
                sale_id=sale.id,
                user_id=sale.user_id,
                type=PayoutType.ADVANCE.value,
                amount=advance_amount,
                status=PayoutStatus.COMPLETED.value
            )
            
            # Update user balance
            user = self.user_repo.get(db, sale.user_id)
            self.user_repo.update_balance(
                db,
                user,
                withdrawable_amount=advance_amount,
                earnings_amount=0  # Earnings updated on reconciliation
            )
            
            return payout
            
        except Exception as e:
            db.rollback()
            raise e
    
    def process_all_pending_advances(self, db: Session) -> List[Payout]:
        """
        Process advance payouts for all pending sales.
        
        This method is idempotent - it will only process sales that don't
        already have an advance payout.
        
        Args:
            db: Database session
            
        Returns:
            List of created payouts
        """
        pending_sales = self.sale_repo.get_pending_sales(db)
        processed_payouts = []
        
        for sale in pending_sales:
            try:
                payout = self.process_advance_payout(db, sale.id)
                processed_payouts.append(payout)
            except (PayoutAlreadyExistsError, InvalidSaleStatusError):
                # Skip if payout already exists or status changed
                continue
        
        return processed_payouts
    
    def recover_failed_payout(self, db: Session, payout_id: int) -> None:
        """
        Recover a failed payout by crediting amount back to user.
        
        Args:
            db: Database session
            payout_id: Payout ID
            
        Raises:
            PayoutNotFoundError: If payout doesn't exist
        """
        payout = self.payout_repo.get(db, payout_id)
        if not payout:
            raise PayoutNotFoundError(f"Payout with id {payout_id} not found")
        
        # Only recover failed, cancelled, or rejected payouts
        if payout.status not in [
            PayoutStatus.FAILED.value,
            PayoutStatus.CANCELLED.value,
            PayoutStatus.REJECTED.value
        ]:
            return
        
        # Credit amount back to user
        user = self.user_repo.get(db, payout.user_id)
        self.user_repo.update_balance(
            db,
            user,
            withdrawable_amount=payout.amount,
            earnings_amount=0
        )
        
        # Create adjustment record
        self.adjustment_repo.create_recovery(
            db,
            user_id=payout.user_id,
            sale_id=payout.sale_id,
            payout_id=payout.id,
            amount=-payout.amount,  # Negative to indicate recovery
            reason=f"Recovery for {payout.status} payout {payout.id}"
        )
        
        # Update payout status
        self.payout_repo.update_status(db, payout, PayoutStatus.COMPLETED)
