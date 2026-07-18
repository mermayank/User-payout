"""Recovery service for failed payouts and withdrawals."""

from typing import List
from sqlalchemy.orm import Session

from app.repositories.payout import PayoutRepository
from app.repositories.withdrawal import WithdrawalRepository
from app.services.payout_service import PayoutService
from app.services.withdrawal_service import WithdrawalService
from app.core.exceptions import PayoutNotFoundError, WithdrawalNotFoundError


class RecoveryService:
    """
    Service for recovery operations.
    
    Handles recovery of failed payouts and withdrawals.
    """
    
    def __init__(
        self,
        payout_repo: PayoutRepository,
        withdrawal_repo: WithdrawalRepository,
        payout_service: PayoutService,
        withdrawal_service: WithdrawalService
    ) -> None:
        """
        Initialize recovery service.
        
        Args:
            payout_repo: Payout repository
            withdrawal_repo: Withdrawal repository
            payout_service: Payout service
            withdrawal_service: Withdrawal service
        """
        self.payout_repo = payout_repo
        self.withdrawal_repo = withdrawal_repo
        self.payout_service = payout_service
        self.withdrawal_service = withdrawal_service
    
    def recover_all_failed_payouts(self, db: Session) -> List[int]:
        """
        Recover all failed payouts.
        
        Args:
            db: Database session
            
        Returns:
            List of recovered payout IDs
        """
        failed_payouts = self.payout_repo.get_failed_payouts(db)
        recovered_ids = []
        
        for payout in failed_payouts:
            try:
                self.payout_service.recover_failed_payout(db, payout.id)
                recovered_ids.append(payout.id)
            except Exception as e:
                # Log error and continue
                print(f"Failed to recover payout {payout.id}: {e}")
                continue
        
        return recovered_ids
    
    def recover_all_failed_withdrawals(self, db: Session) -> List[int]:
        """
        Recover all failed withdrawals.
        
        Args:
            db: Database session
            
        Returns:
            List of recovered withdrawal IDs
        """
        failed_withdrawals = self.withdrawal_repo.get_failed_withdrawals(db)
        recovered_ids = []
        
        for withdrawal in failed_withdrawals:
            try:
                self.withdrawal_service.recover_failed_withdrawal(db, withdrawal.id)
                recovered_ids.append(withdrawal.id)
            except Exception as e:
                # Log error and continue
                print(f"Failed to recover withdrawal {withdrawal.id}: {e}")
                continue
        
        return recovered_ids
    
    def recover_all_failed_transactions(self, db: Session) -> dict:
        """
        Recover all failed transactions (payouts and withdrawals).
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with recovered counts
        """
        recovered_payouts = self.recover_all_failed_payouts(db)
        recovered_withdrawals = self.recover_all_failed_withdrawals(db)
        
        return {
            "recovered_payouts": len(recovered_payouts),
            "recovered_withdrawals": len(recovered_withdrawals),
            "payout_ids": recovered_payouts,
            "withdrawal_ids": recovered_withdrawals
        }
