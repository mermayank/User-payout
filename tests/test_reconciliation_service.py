"""Tests for reconciliation service."""

import pytest
from app.models.sale import SaleStatus
from app.models.payout import PayoutType
from app.services.reconciliation_service import ReconciliationService
from app.repositories.sale import SaleRepository
from app.repositories.payout import PayoutRepository
from app.repositories.user import UserRepository
from app.repositories.adjustment import AdjustmentRepository
from app.core.exceptions import SaleNotFoundError, InvalidSaleStatusError


class TestReconciliation:
    """Tests for sale reconciliation."""
    
    def test_reconcile_approved_sale_with_advance(
        self, 
        db_session, 
        user_factory, 
        sale_factory,
        payout_factory
    ):
        """Test approving a sale with existing advance payout."""
        user = user_factory()
        sale = sale_factory(user_id=user.id, earning=100.0)
        payout_factory(
            sale_id=sale.id, 
            user_id=user.id, 
            amount=10.0,
            payout_type="advance"
        )
        
        reconciliation_service = ReconciliationService(
            SaleRepository(),
            PayoutRepository(),
            UserRepository(),
            AdjustmentRepository()
        )
        
        updated_sale = reconciliation_service.reconcile_sale(
            db_session, 
            sale.id, 
            SaleStatus.APPROVED
        )
        
        # Check sale status
        assert updated_sale.status == SaleStatus.APPROVED.value
        
        # Check user balance - should have remaining 90 credited
        db_session.refresh(user)
        assert user.withdrawable_balance == 90.0
        assert user.total_earnings == 100.0
        
        # Check reconciliation payout created
        payout_repo = PayoutRepository()
        payouts = payout_repo.get_by_sale(db_session, sale.id)
        assert len(payouts) == 2  # advance + reconciliation
    
    def test_reconcile_approved_sale_without_advance(
        self, 
        db_session, 
        user_factory, 
        sale_factory
    ):
        """Test approving a sale without advance payout."""
        user = user_factory()
        sale = sale_factory(user_id=user.id, earning=100.0)
        
        reconciliation_service = ReconciliationService(
            SaleRepository(),
            PayoutRepository(),
            UserRepository(),
            AdjustmentRepository()
        )
        
        updated_sale = reconciliation_service.reconcile_sale(
            db_session, 
            sale.id, 
            SaleStatus.APPROVED
        )
        
        # Check sale status
        assert updated_sale.status == SaleStatus.APPROVED.value
        
        # Check user balance - should have full 100 credited
        db_session.refresh(user)
        assert user.withdrawable_balance == 100.0
        assert user.total_earnings == 100.0
    
    def test_reconcile_rejected_sale_with_advance(
        self, 
        db_session, 
        user_factory, 
        sale_factory,
        payout_factory
    ):
        """Test rejecting a sale with existing advance payout."""
        user = user_factory()
        sale = sale_factory(user_id=user.id, earning=100.0)
        payout_factory(
            sale_id=sale.id, 
            user_id=user.id, 
            amount=10.0,
            payout_type="advance"
        )
        
        # Give user the advance amount
        user_repo = UserRepository()
        user_repo.update_balance(db_session, user, 10.0, 0)
        
        reconciliation_service = ReconciliationService(
            SaleRepository(),
            PayoutRepository(),
            UserRepository(),
            AdjustmentRepository()
        )
        
        updated_sale = reconciliation_service.reconcile_sale(
            db_session, 
            sale.id, 
            SaleStatus.REJECTED
        )
        
        # Check sale status
        assert updated_sale.status == SaleStatus.REJECTED.value
        
        # Check user balance - advance should be recovered
        db_session.refresh(user)
        assert user.withdrawable_balance == 0.0
        assert user.total_earnings == 0.0
        
        # Check adjustment created for recovery
        adjustment_repo = AdjustmentRepository()
        adjustments = adjustment_repo.get_by_sale(db_session, sale.id)
        assert len(adjustments) == 1
        assert adjustments[0].amount == -10.0
    
    def test_reconcile_rejected_sale_without_advance(
        self, 
        db_session, 
        user_factory, 
        sale_factory
    ):
        """Test rejecting a sale without advance payout."""
        user = user_factory()
        sale = sale_factory(user_id=user.id, earning=100.0)
        
        reconciliation_service = ReconciliationService(
            SaleRepository(),
            PayoutRepository(),
            UserRepository(),
            AdjustmentRepository()
        )
        
        updated_sale = reconciliation_service.reconcile_sale(
            db_session, 
            sale.id, 
            SaleStatus.REJECTED
        )
        
        # Check sale status
        assert updated_sale.status == SaleStatus.REJECTED.value
        
        # Check user balance - should remain 0
        db_session.refresh(user)
        assert user.withdrawable_balance == 0.0
    
    def test_reconcile_sale_not_found(self, db_session):
        """Test reconciling non-existent sale."""
        reconciliation_service = ReconciliationService(
            SaleRepository(),
            PayoutRepository(),
            UserRepository(),
            AdjustmentRepository()
        )
        
        with pytest.raises(SaleNotFoundError):
            reconciliation_service.reconcile_sale(db_session, 999, SaleStatus.APPROVED)
    
    def test_reconcile_invalid_status_transition(
        self, 
        db_session, 
        user_factory, 
        sale_factory
    ):
        """Test reconciling a sale that's not pending."""
        user = user_factory()
        sale = sale_factory(user_id=user.id, earning=100.0)
        
        # Change to approved
        sale_repo = SaleRepository()
        sale_repo.update_status(db_session, sale, SaleStatus.APPROVED)
        
        reconciliation_service = ReconciliationService(
            SaleRepository(),
            PayoutRepository(),
            UserRepository(),
            AdjustmentRepository()
        )
        
        with pytest.raises(InvalidSaleStatusError):
            reconciliation_service.reconcile_sale(db_session, sale.id, SaleStatus.APPROVED)
