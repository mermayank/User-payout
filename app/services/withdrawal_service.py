"""Withdrawal service for user withdrawals."""

from typing import List
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.withdrawal import Withdrawal, WithdrawalStatus
from app.repositories.user import UserRepository
from app.repositories.withdrawal import WithdrawalRepository
from app.repositories.adjustment import AdjustmentRepository
from app.core.exceptions import (
    UserNotFoundError,
    InsufficientBalanceError,
    WithdrawalCooldownError
)


class WithdrawalService:
    """
    Service for withdrawal operations.
    
    Handles user withdrawals with 24-hour cooldown enforcement.
    """
    
    def __init__(
        self,
        user_repo: UserRepository,
        withdrawal_repo: WithdrawalRepository,
        adjustment_repo: AdjustmentRepository
    ) -> None:
        """
        Initialize withdrawal service.
        
        Args:
            user_repo: User repository
            withdrawal_repo: Withdrawal repository
            adjustment_repo: Adjustment repository
        """
        self.user_repo = user_repo
        self.withdrawal_repo = withdrawal_repo
        self.adjustment_repo = adjustment_repo
    
    def create_withdrawal(
        self, 
        db: Session, 
        user_id: int, 
        amount: float
    ) -> Withdrawal:
        """
        Create a withdrawal request.
        
        Args:
            db: Database session
            user_id: User ID
            amount: Withdrawal amount
            
        Returns:
            Created withdrawal
            
        Raises:
            UserNotFoundError: If user doesn't exist
            InsufficientBalanceError: If user has insufficient balance
            WithdrawalCooldownError: If user is in cooldown period
        """
        # Get user
        user = self.user_repo.get(db, user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")
        
        # Check balance
        if user.withdrawable_balance < amount:
            raise InsufficientBalanceError(
                f"Insufficient balance. Available: {user.withdrawable_balance}, Requested: {amount}"
            )
        
        # Check cooldown
        if not self.withdrawal_repo.can_withdraw(db, user_id):
            raise WithdrawalCooldownError(
                "User can only withdraw once every 24 hours"
            )
        
        # Deduct from balance
        self.user_repo.update_balance(
            db,
            user,
            withdrawable_amount=-amount,
            earnings_amount=0
        )
        
        # Create withdrawal
        withdrawal = self.withdrawal_repo.create(
            db,
            user_id=user_id,
            amount=amount,
            status=WithdrawalStatus.PENDING.value
        )
        
        return withdrawal
    
    def recover_failed_withdrawal(self, db: Session, withdrawal_id: int) -> None:
        """
        Recover a failed withdrawal by crediting amount back to user.
        
        Args:
            db: Database session
            withdrawal_id: Withdrawal ID
            
        Raises:
            WithdrawalNotFoundError: If withdrawal doesn't exist
        """
        withdrawal = self.withdrawal_repo.get(db, withdrawal_id)
        if not withdrawal:
            raise WithdrawalNotFoundError(f"Withdrawal with id {withdrawal_id} not found")
        
        # Only recover failed, cancelled, or rejected withdrawals
        if withdrawal.status not in [
            WithdrawalStatus.FAILED.value,
            WithdrawalStatus.CANCELLED.value,
            WithdrawalStatus.REJECTED.value
        ]:
            return
        
        # Credit amount back to user
        user = self.user_repo.get(db, withdrawal.user_id)
        self.user_repo.update_balance(
            db,
            user,
            withdrawable_amount=withdrawal.amount,
            earnings_amount=0
        )
        
        # Create adjustment record
        self.adjustment_repo.create_recovery(
            db,
            user_id=withdrawal.user_id,
            withdrawal_id=withdrawal.id,
            amount=-withdrawal.amount,
            reason=f"Recovery for {withdrawal.status} withdrawal {withdrawal.id}"
        )
        
        # Update withdrawal status
        self.withdrawal_repo.update_status(db, withdrawal, WithdrawalStatus.COMPLETED)
    
    def get_user_withdrawals(
        self, 
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Withdrawal]:
        """
        Get withdrawals for a user.
        
        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of withdrawals
        """
        return self.withdrawal_repo.get_by_user(db, user_id, skip, limit)
