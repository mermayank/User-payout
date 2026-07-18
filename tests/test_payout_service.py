"""Tests for payout service."""

import pytest
from app.models.sale import SaleStatus
from app.models.payout import PayoutStatus, PayoutType
from app.services.payout_service import PayoutService
from app.repositories.sale import SaleRepository
from app.repositories.payout import PayoutRepository
from app.repositories.user import UserRepository
from app.repositories.adjustment import AdjustmentRepository
from app.core.exceptions import (
    SaleNotFoundError,
    InvalidSaleStatusError,
    PayoutAlreadyExistsError
)


class TestAdvancePayout:
    """Tests for advance payout processing."""
    
    def test_process_advance_payout_success(
        self, 
        db_session, 
        user_factory, 
        sale_factory
    ):
        """Test successful advance payout processing."""
        # Setup
        user = user_factory()
        sale = sale_factory(user_id=user.id, earning=100.0)
        
        # Execute
        payout_service = PayoutService(
            SaleRepository(),
            PayoutRepository(),
            UserRepository(),
            AdjustmentRepository()
        )
        payout = payout_service.process_advance_payout(db_session, sale.id)
        
        # Assert
        assert payout.sale_id == sale.id
        assert payout.user_id == user.id
        assert payout.type == PayoutType.ADVANCE.value
        assert payout.amount == 10.0  # 10% of 100
        assert payout.status == PayoutStatus.COMPLETED.value
        
        # Check user balance updated
        db_session.refresh(user)
        assert user.withdrawable_balance == 10.0
    
    def test_process_advance_payout_idempotent(
        self, 
        db_session, 
        user_factory, 
        sale_factory
    ):
        """Test that advance payout is idempotent."""
        # Setup
        user = user_factory()
        sale = sale_factory(user_id=user.id, earning=100.0)
        
        # Execute first time
        payout_service = PayoutService(
            SaleRepository(),
            PayoutRepository(),
            UserRepository(),
            AdjustmentRepository()
        )
        payout1 = payout_service.process_advance_payout(db_session, sale.id)
        
        # Execute second time - should raise error
        with pytest.raises(PayoutAlreadyExistsError):
            payout_service.process_advance_payout(db_session, sale.id)
        
        # Verify only one payout exists
        payout_repo = PayoutRepository()
        payouts = payout_repo.get_by_sale(db_session, sale.id)
        assert len(payouts) == 1
    
    def test_process_advance_payout_sale_not_found(self, db_session):
        """Test advance payout with non-existent sale."""
        payout_service = PayoutService(
            SaleRepository(),
            PayoutRepository(),
            UserRepository(),
            AdjustmentRepository()
        )
        
        with pytest.raises(SaleNotFoundError):
            payout_service.process_advance_payout(db_session, 999)
    
    def test_process_advance_payout_invalid_status(
        self, 
        db_session, 
        user_factory, 
        sale_factory
    ):
        """Test advance payout with non-pending sale."""
        user = user_factory()
        sale = sale_factory(user_id=user.id, earning=100.0)
        
        # Change sale status to approved
        sale_repo = SaleRepository()
        sale_repo.update_status(db_session, sale, SaleStatus.APPROVED)
        
        payout_service = PayoutService(
            SaleRepository(),
            PayoutRepository(),
            UserRepository(),
            AdjustmentRepository()
        )
        
        with pytest.raises(InvalidSaleStatusError):
            payout_service.process_advance_payout(db_session, sale.id)
    
    def test_process_all_pending_advances(
        self, 
        db_session, 
        user_factory, 
        sale_factory
    ):
        """Test processing all pending sales for advance payout."""
        user = user_factory()
        sale1 = sale_factory(user_id=user.id, earning=100.0)
        sale2 = sale_factory(user_id=user.id, earning=200.0)
        
        payout_service = PayoutService(
            SaleRepository(),
            PayoutRepository(),
            UserRepository(),
            AdjustmentRepository()
        )
        
        payouts = payout_service.process_all_pending_advances(db_session)
        
        assert len(payouts) == 2
        assert payouts[0].amount == 10.0
        assert payouts[1].amount == 20.0


class TestPayoutRecovery:
    """Tests for payout recovery."""
    
    def test_recover_failed_payout(
        self, 
        db_session, 
        user_factory, 
        sale_factory,
        payout_factory
    ):
        """Test recovery of failed payout."""
        user = user_factory()
        sale = sale_factory(user_id=user.id, earning=100.0)
        payout = payout_factory(
            sale_id=sale.id, 
            user_id=user.id, 
            amount=10.0,
            payout_type="advance"
        )
        
        # Mark as failed
        payout_repo = PayoutRepository()
        payout_repo.update_status(db_session, payout, PayoutStatus.FAILED)
        
        # Recover
        payout_service = PayoutService(
            SaleRepository(),
            PayoutRepository(),
            UserRepository(),
            AdjustmentRepository()
        )
        payout_service.recover_failed_payout(db_session, payout.id)
        
        # Check balance restored
        db_session.refresh(user)
        assert user.withdrawable_balance == 10.0
        
        # Check adjustment created
        adjustment_repo = AdjustmentRepository()
        adjustments = adjustment_repo.get_by_payout(db_session, payout.id)
        assert len(adjustments) == 1
        assert adjustments[0].amount == -10.0
