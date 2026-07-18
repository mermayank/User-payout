"""Reconciliation service for sale approval/rejection."""

from typing import Optional
from sqlalchemy.orm import Session

from app.models.sale import Sale, SaleStatus
from app.models.payout import Payout, PayoutStatus, PayoutType
from app.repositories.sale import SaleRepository
from app.repositories.payout import PayoutRepository
from app.repositories.user import UserRepository
from app.repositories.adjustment import AdjustmentRepository
from app.core.exceptions import (
    SaleNotFoundError,
    InvalidSaleStatusError,
    PayoutNotFoundError
)


class ReconciliationService:
    """
    Service for reconciliation operations.
    
    Handles sale approval and rejection with proper balance adjustments.
    """
    
    def __init__(
        self,
        sale_repo: SaleRepository,
        payout_repo: PayoutRepository,
        user_repo: UserRepository,
        adjustment_repo: AdjustmentRepository
    ) -> None:
        """
        Initialize reconciliation service.
        
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
    
    def reconcile_sale(
        self, 
        db: Session, 
        sale_id: int, 
        new_status: SaleStatus
    ) -> Sale:
        """
        Reconcile a sale by approving or rejecting it.
        
        Args:
            db: Database session
            sale_id: Sale ID
            new_status: New status (approved or rejected)
            
        Returns:
            Updated sale
            
        Raises:
            SaleNotFoundError: If sale doesn't exist
            InvalidSaleStatusError: If sale is not pending or already reconciled
        """
        # Get sale
        sale = self.sale_repo.get(db, sale_id)
        if not sale:
            raise SaleNotFoundError(f"Sale with id {sale_id} not found")
        
        # Validate current status
        if sale.status != SaleStatus.PENDING.value:
            raise InvalidSaleStatusError(
                f"Sale must be pending to reconcile, current status: {sale.status}"
            )
        
        # Validate new status
        if new_status not in [SaleStatus.APPROVED, SaleStatus.REJECTED]:
            raise InvalidSaleStatusError(
                f"Invalid reconciliation status: {new_status}"
            )
        
        # Get advance payout if exists
        advance_payout = self.payout_repo.get_advance_payout_for_sale(db, sale_id)
        
        if new_status == SaleStatus.APPROVED:
            self._handle_approval(db, sale, advance_payout)
        elif new_status == SaleStatus.REJECTED:
            self._handle_rejection(db, sale, advance_payout)
        
        # Update sale status
        return self.sale_repo.update_status(db, sale, new_status)
    
    def _handle_approval(
        self, 
        db: Session, 
        sale: Sale, 
        advance_payout: Optional[Payout]
    ) -> None:
        """
        Handle sale approval.
        
        Credits remaining payout (earning - advance_paid) to user.
        
        Args:
            db: Database session
            sale: Sale to approve
            advance_payout: Existing advance payout (if any)
        """
        advance_paid = advance_payout.amount if advance_payout else 0
        remaining_payout = sale.earning - advance_paid
        
        # Update user balance
        user = self.user_repo.get(db, sale.user_id)
        self.user_repo.update_balance(
            db,
            user,
            withdrawable_amount=remaining_payout,
            earnings_amount=sale.earning
        )
        
        # Create reconciliation payout if there's remaining amount
        if remaining_payout > 0:
            self.payout_repo.create(
                db,
                sale_id=sale.id,
                user_id=sale.user_id,
                type=PayoutType.RECONCILIATION.value,
                amount=remaining_payout,
                status=PayoutStatus.COMPLETED.value
            )
    
    def _handle_rejection(
        self, 
        db: Session, 
        sale: Sale, 
        advance_payout: Optional[Payout]
    ) -> None:
        """
        Handle sale rejection.
        
        Recovers previously paid advance by applying negative adjustment.
        
        Args:
            db: Database session
            sale: Sale to reject
            advance_payout: Existing advance payout (if any)
        """
        if advance_payout:
            # Recover advance payout
            user = self.user_repo.get(db, sale.user_id)
            self.user_repo.update_balance(
                db,
                user,
                withdrawable_amount=-advance_payout.amount,
                earnings_amount=0
            )
            
            # Create adjustment record
            self.adjustment_repo.create_recovery(
                db,
                user_id=sale.user_id,
                sale_id=sale.id,
                payout_id=advance_payout.id,
                amount=-advance_payout.amount,
                reason=f"Recovery of advance payout for rejected sale {sale.id}"
            )
