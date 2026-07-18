"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.base import Base
from app.api.deps import get_db
from app.models import user, sale, payout, withdrawal, adjustment  # noqa: F401

TEST_DATABASE_URL = "sqlite:///./test_api.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(bind=engine)   # clean slate each run
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


class TestUserAPI:
    """Tests for user API endpoints."""
    
    def test_create_user(self):
        """Test creating a user."""
        response = client.post(
            "/api/v1/users",
            json={
                "email": "test@example.com",
                "username": "testuser"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"
        assert data["withdrawable_balance"] == 0.0
    
    def test_create_duplicate_email(self):
        """Test creating user with duplicate email."""
        # First user
        client.post(
            "/api/v1/users",
            json={
                "email": "test@example.com",
                "username": "testuser1"
            }
        )
        
        # Second user with same email
        response = client.post(
            "/api/v1/users",
            json={
                "email": "test@example.com",
                "username": "testuser2"
            }
        )
        assert response.status_code == 400
    
    def test_get_users(self):
        """Test getting all users."""
        # Create users
        client.post("/api/v1/users", json={"email": "user1@example.com", "username": "user1"})
        client.post("/api/v1/users", json={"email": "user2@example.com", "username": "user2"})
        
        response = client.get("/api/v1/users")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
    
    def test_get_balance(self):
        """Test getting user balance."""
        # Create user
        user_response = client.post(
            "/api/v1/users",
            json={"email": "balance@example.com", "username": "balanceuser"}
        )
        user_id = user_response.json()["id"]
        
        response = client.get(f"/api/v1/balance?user_id={user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user_id
        assert data["withdrawable_balance"] == 0.0


class TestSalesAPI:
    """Tests for sales API endpoints."""
    
    def test_create_sale(self):
        """Test creating a sale."""
        # Create user first
        user_response = client.post(
            "/api/v1/users",
            json={"email": "seller@example.com", "username": "seller"}
        )
        user_id = user_response.json()["id"]
        
        response = client.post(
            "/api/v1/sales",
            json={
                "user_id": user_id,
                "brand": "Nike",
                "earning": 100.0
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["brand"] == "Nike"
        assert data["earning"] == 100.0
        assert data["status"] == "pending"
    
    def test_get_sales(self):
        """Test getting all sales."""
        response = client.get("/api/v1/sales")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_advance_payout(self):
        """Test advance payout creation."""
        # Create user and sale
        user_response = client.post(
            "/api/v1/users",
            json={"email": "payout@example.com", "username": "payoutuser"}
        )
        user_id = user_response.json()["id"]
        
        sale_response = client.post(
            "/api/v1/sales",
            json={
                "user_id": user_id,
                "brand": "Adidas",
                "earning": 100.0
            }
        )
        sale_id = sale_response.json()["id"]
        
        response = client.post(
            "/api/v1/advance-payout",
            json={"sale_id": sale_id}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["amount"] == 10.0  # 10% of 100
        assert data["type"] == "advance"
    
    def test_reconcile_sale(self):
        """Test sale reconciliation."""
        # Create user and sale
        user_response = client.post(
            "/api/v1/users",
            json={"email": "reconcile@example.com", "username": "reconcileuser"}
        )
        user_id = user_response.json()["id"]
        
        sale_response = client.post(
            "/api/v1/sales",
            json={
                "user_id": user_id,
                "brand": "Puma",
                "earning": 100.0
            }
        )
        sale_id = sale_response.json()["id"]
        
        response = client.post(
            "/api/v1/admin/reconcile",
            json={
                "sale_id": sale_id,
                "status": "approved"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "approved"


class TestWithdrawalAPI:
    """Tests for withdrawal API endpoints."""
    
    def test_create_withdrawal(self):
        """Test creating a withdrawal."""
        # Create user with balance
        user_response = client.post(
            "/api/v1/users",
            json={"email": "withdraw@example.com", "username": "withdrawuser"}
        )
        user_id = user_response.json()["id"]
        
        # Create sale and reconcile to add balance
        sale_response = client.post(
            "/api/v1/sales",
            json={
                "user_id": user_id,
                "brand": "Reebok",
                "earning": 100.0
            }
        )
        sale_id = sale_response.json()["id"]
        
        client.post(
            "/api/v1/admin/reconcile",
            json={"sale_id": sale_id, "status": "approved"}
        )
        
        response = client.post(
            "/api/v1/withdraw",
            json={
                "user_id": user_id,
                "amount": 50.0
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["amount"] == 50.0
        assert data["status"] == "pending"
    
    def test_get_withdrawals(self):
        """Test getting withdrawals."""
        response = client.get("/api/v1/withdrawals")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestPayoutsAPI:
    """Tests for payouts API endpoints."""
    
    def test_get_payouts(self):
        """Test getting payouts."""
        response = client.get("/api/v1/payouts")
        assert response.status_code == 200
        assert isinstance(response.json(), list)