"""Pytest configuration and fixtures."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.models import user, sale, payout, withdrawal, adjustment  # noqa: F401


# Test database URL
TEST_DATABASE_URL = "sqlite:///./test_payout_system.db"


@pytest.fixture
def engine():
    """Create test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(engine):
    """Create test database session."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture
def user_factory(db_session):
    """Factory to create test users."""
    def create_user(email: str = "test@example.com", username: str = "testuser"):
        from app.models.user import User
        user = User(
            email=email,
            username=username,
            withdrawable_balance=0.0,
            total_earnings=0.0
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user
    return create_user


@pytest.fixture
def sale_factory(db_session, user_factory):
    """Factory to create test sales."""
    def create_sale(user_id: int = None, brand: str = "TestBrand", earning: float = 100.0):
        from app.models.sale import Sale, SaleStatus
        if user_id is None:
            user = user_factory()
            user_id = user.id
        sale = Sale(
            user_id=user_id,
            brand=brand,
            earning=earning,
            status=SaleStatus.PENDING.value
        )
        db_session.add(sale)
        db_session.commit()
        db_session.refresh(sale)
        return sale
    return create_sale


@pytest.fixture
def payout_factory(db_session):
    """Factory to create test payouts."""
    def create_payout(sale_id: int, user_id: int, amount: float, payout_type: str = "advance"):
        from app.models.payout import Payout, PayoutStatus
        payout = Payout(
            sale_id=sale_id,
            user_id=user_id,
            type=payout_type,
            amount=amount,
            status=PayoutStatus.COMPLETED.value
        )
        db_session.add(payout)
        db_session.commit()
        db_session.refresh(payout)
        return payout
    return create_payout


@pytest.fixture
def withdrawal_factory(db_session):
    """Factory to create test withdrawals."""
    def create_withdrawal(user_id: int, amount: float):
        from app.models.withdrawal import Withdrawal, WithdrawalStatus
        withdrawal = Withdrawal(
            user_id=user_id,
            amount=amount,
            status=WithdrawalStatus.PENDING.value
        )
        db_session.add(withdrawal)
        db_session.commit()
        db_session.refresh(withdrawal)
        return withdrawal
    return create_withdrawal
