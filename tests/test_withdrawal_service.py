"""Tests for withdrawal service."""

import pytest
from datetime import datetime, timedelta
from app.models.withdrawal import WithdrawalStatus
from app.services.withdrawal_service import WithdrawalService
from app.repositories.user import UserRepository
from app.repositories.withdrawal import WithdrawalRepository
from app.repositories.adjustment import AdjustmentRepository
from app.core.exceptions import (
    UserNotFoundError,
    InsufficientBalanceError,
    WithdrawalCooldownError
)


class TestWithdrawal:
    """Tests for withdrawal operations."""
    
    def test_create_withdrawal_success(
        self, 
        db_session, 
        user_factory
    ):
        """Test successful withdrawal creation."""
        user = user_factory()
        
        # Give user balance
        user_repo = UserRepository()
        user_repo.update_balance(db_session, user, 100.0, 100.0)
        
        withdrawal_service = WithdrawalService(
            UserRepository(),
            WithdrawalRepository(),
            AdjustmentRepository()
        )
        
        withdrawal = withdrawal_service.create_withdrawal(db_session, user.id, 50.0)
        
        assert withdrawal.user_id == user.id
        assert withdrawal.amount == 50.0
        assert withdrawal.status == WithdrawalStatus.PENDING.value
        
        # Check balance deducted
        db_session.refresh(user)
        assert user.withdrawable_balance == 50.0
    
    def test_create_withdrawal_insufficient_balance(
        self, 
        db_session, 
        user_factory
    ):
        """Test withdrawal with insufficient balance."""
        user = user_factory()
        
        withdrawal_service = WithdrawalService(
            UserRepository(),
            WithdrawalRepository(),
            AdjustmentRepository()
        )
        
        with pytest.raises(InsufficientBalanceError):
            withdrawal_service.create_withdrawal(db_session, user.id, 50.0)
    
    def test_create_withdrawal_user_not_found(self, db_session):
        """Test withdrawal for non-existent user."""
        withdrawal_service = WithdrawalService(
            UserRepository(),
            WithdrawalRepository(),
            AdjustmentRepository()
        )
        
        with pytest.raises(UserNotFoundError):
            withdrawal_service.create_withdrawal(db_session, 999, 50.0)
    
    def test_withdrawal_cooldown(
        self, 
        db_session, 
        user_factory
    ):
        """Test 24-hour withdrawal cooldown."""
        user = user_factory()
        
        # Give user balance
        user_repo = UserRepository()
        user_repo.update_balance(db_session, user, 100.0, 100.0)
        
        withdrawal_service = WithdrawalService(
            UserRepository(),
            WithdrawalRepository(),
            AdjustmentRepository()
        )
        
        # First withdrawal should succeed
        withdrawal_service.create_withdrawal(db_session, user.id, 50.0)
        
        # Second withdrawal should fail due to cooldown
        with pytest.raises(WithdrawalCooldownError):
            withdrawal_service.create_withdrawal(db_session, user.id, 25.0)
    
    def test_recover_failed_withdrawal(
        self, 
        db_session, 
        user_factory,
        withdrawal_factory
    ):
        """Test recovery of failed withdrawal."""
        user = user_factory()
        
        # Give user balance
        user_repo = UserRepository()
        user_repo.update_balance(db_session, user, 100.0, 100.0)
        
        # Create withdrawal
        withdrawal = withdrawal_factory(user_id=user.id, amount=50.0)
        
        # Deduct from balance
        user_repo.update_balance(db_session, user, -50.0, 0)
        
        # Mark as failed
        withdrawal_repo = WithdrawalRepository()
        withdrawal_repo.update_status(db_session, withdrawal, WithdrawalStatus.FAILED)
        
        # Recover
        withdrawal_service = WithdrawalService(
            UserRepository(),
            WithdrawalRepository(),
            AdjustmentRepository()
        )
        withdrawal_service.recover_failed_withdrawal(db_session, withdrawal.id)
        
        # Check balance restored
        db_session.refresh(user)
        assert user.withdrawable_balance == 100.0
        
        # Check adjustment created
        adjustment_repo = AdjustmentRepository()
        adjustments = adjustment_repo.get_by_withdrawal(db_session, withdrawal.id)
        assert len(adjustments) == 1
        assert adjustments[0].amount == -50.0
    
    def test_get_user_withdrawals(
        self, 
        db_session, 
        user_factory,
        withdrawal_factory
    ):
        """Test getting user withdrawals."""
        user = user_factory()
        withdrawal_factory(user_id=user.id, amount=50.0)
        withdrawal_factory(user_id=user.id, amount=25.0)
        
        withdrawal_service = WithdrawalService(
            UserRepository(),
            WithdrawalRepository(),
            AdjustmentRepository()
        )
        
        withdrawals = withdrawal_service.get_user_withdrawals(db_session, user.id)
        
        assert len(withdrawals) == 2
