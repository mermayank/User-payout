"""Seed data script for the User Payout Management System."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.models.user import User
from app.models.sale import Sale, SaleStatus
from app.models.payout import Payout, PayoutStatus, PayoutType
from app.models.withdrawal import Withdrawal, WithdrawalStatus
from app.models.adjustment import AdjustmentHistory, AdjustmentType


def seed_users(db: Session) -> None:
    """Seed users."""
    users_data = [
        {
            "email": "john.doe@example.com",
            "username": "johndoe",
            "withdrawable_balance": 0.0,
            "total_earnings": 0.0
        },
        {
            "email": "jane.smith@example.com",
            "username": "janesmith",
            "withdrawable_balance": 0.0,
            "total_earnings": 0.0
        },
        {
            "email": "bob.wilson@example.com",
            "username": "bobwilson",
            "withdrawable_balance": 0.0,
            "total_earnings": 0.0
        },
        {
            "email": "alice.brown@example.com",
            "username": "alicebrown",
            "withdrawable_balance": 0.0,
            "total_earnings": 0.0
        },
        {
            "email": "charlie.davis@example.com",
            "username": "charliedavis",
            "withdrawable_balance": 0.0,
            "total_earnings": 0.0
        }
    ]
    
    for user_data in users_data:
        user = User(**user_data)
        db.add(user)
    
    db.commit()
    print(f"✓ Seeded {len(users_data)} users")


def seed_sales(db: Session) -> None:
    """Seed sales."""
    users = db.query(User).all()
    
    sales_data = [
        # John's sales
        {"user_id": users[0].id, "brand": "Nike", "earning": 100.0, "status": SaleStatus.PENDING.value},
        {"user_id": users[0].id, "brand": "Adidas", "earning": 150.0, "status": SaleStatus.PENDING.value},
        {"user_id": users[0].id, "brand": "Puma", "earning": 75.0, "status": SaleStatus.APPROVED.value},
        
        # Jane's sales
        {"user_id": users[1].id, "brand": "Reebok", "earning": 200.0, "status": SaleStatus.PENDING.value},
        {"user_id": users[1].id, "brand": "Under Armour", "earning": 120.0, "status": SaleStatus.REJECTED.value},
        
        # Bob's sales
        {"user_id": users[2].id, "brand": "New Balance", "earning": 80.0, "status": SaleStatus.PENDING.value},
        {"user_id": users[2].id, "brand": "Converse", "earning": 95.0, "status": SaleStatus.APPROVED.value},
        
        # Alice's sales
        {"user_id": users[3].id, "brand": "Vans", "earning": 110.0, "status": SaleStatus.PENDING.value},
        {"user_id": users[3].id, "brand": "Fila", "earning": 85.0, "status": SaleStatus.PENDING.value},
        
        # Charlie's sales
        {"user_id": users[4].id, "brand": "ASICS", "earning": 130.0, "status": SaleStatus.APPROVED.value},
        {"user_id": users[4].id, "brand": "Skechers", "earning": 90.0, "status": SaleStatus.REJECTED.value},
    ]
    
    for sale_data in sales_data:
        sale = Sale(**sale_data)
        db.add(sale)
    
    db.commit()
    print(f"✓ Seeded {len(sales_data)} sales")


def seed_payouts(db: Session) -> None:
    """Seed payouts."""
    sales = db.query(Sale).all()
    
    payouts_data = []
    
    # Advance payouts for pending sales
    pending_sales = [s for s in sales if s.status == SaleStatus.PENDING.value]
    for sale in pending_sales[:3]:  # First 3 pending sales get advance payouts
        payouts_data.append({
            "sale_id": sale.id,
            "user_id": sale.user_id,
            "type": PayoutType.ADVANCE.value,
            "amount": sale.earning * 0.10,
            "status": PayoutStatus.COMPLETED.value
        })
    
    # Reconciliation payouts for approved sales
    approved_sales = [s for s in sales if s.status == SaleStatus.APPROVED.value]
    for sale in approved_sales:
        advance_amount = sale.earning * 0.10
        remaining = sale.earning - advance_amount
        payouts_data.append({
            "sale_id": sale.id,
            "user_id": sale.user_id,
            "type": PayoutType.ADVANCE.value,
            "amount": advance_amount,
            "status": PayoutStatus.COMPLETED.value
        })
        payouts_data.append({
            "sale_id": sale.id,
            "user_id": sale.user_id,
            "type": PayoutType.RECONCILIATION.value,
            "amount": remaining,
            "status": PayoutStatus.COMPLETED.value
        })
    
    for payout_data in payouts_data:
        payout = Payout(**payout_data)
        db.add(payout)
    
    db.commit()
    print(f"✓ Seeded {len(payouts_data)} payouts")


def seed_withdrawals(db: Session) -> None:
    """Seed withdrawals."""
    users = db.query(User).all()
    
    withdrawals_data = [
        {"user_id": users[0].id, "amount": 50.0, "status": WithdrawalStatus.COMPLETED.value},
        {"user_id": users[1].id, "amount": 75.0, "status": WithdrawalStatus.PENDING.value},
        {"user_id": users[2].id, "amount": 30.0, "status": WithdrawalStatus.FAILED.value},
        {"user_id": users[3].id, "amount": 40.0, "status": WithdrawalStatus.COMPLETED.value},
    ]
    
    for withdrawal_data in withdrawals_data:
        withdrawal = Withdrawal(**withdrawal_data)
        db.add(withdrawal)
    
    db.commit()
    print(f"✓ Seeded {len(withdrawals_data)} withdrawals")


def seed_adjustments(db: Session) -> None:
    """Seed adjustments."""
    withdrawals = db.query(Withdrawal).filter(Withdrawal.status == WithdrawalStatus.FAILED.value).all()
    
    adjustments_data = []
    
    # Recovery for failed withdrawal
    for withdrawal in withdrawals:
        adjustments_data.append({
            "user_id": withdrawal.user_id,
            "withdrawal_id": withdrawal.id,
            "type": AdjustmentType.RECOVERY.value,
            "amount": -withdrawal.amount,
            "reason": f"Recovery for failed withdrawal {withdrawal.id}"
        })
    
    # Recovery for rejected sales
    rejected_sales = db.query(Sale).filter(Sale.status == SaleStatus.REJECTED.value).all()
    for sale in rejected_sales:
        adjustments_data.append({
            "user_id": sale.user_id,
            "sale_id": sale.id,
            "type": AdjustmentType.RECOVERY.value,
            "amount": -(sale.earning * 0.10),
            "reason": f"Recovery for rejected sale {sale.id}"
        })
    
    for adjustment_data in adjustments_data:
        adjustment = AdjustmentHistory(**adjustment_data)
        db.add(adjustment)
    
    db.commit()
    print(f"✓ Seeded {len(adjustments_data)} adjustments")


def update_balances(db: Session) -> None:
    """Update user balances based on payouts and withdrawals."""
    users = db.query(User).all()
    
    for user in users:
        # Calculate total payouts
        payouts = db.query(Payout).filter(
            Payout.user_id == user.id,
            Payout.status == PayoutStatus.COMPLETED.value
        ).all()
        total_payouts = sum(p.amount for p in payouts)
        
        # Calculate total withdrawals
        withdrawals = db.query(Withdrawal).filter(
            Withdrawal.user_id == user.id,
            Withdrawal.status == WithdrawalStatus.COMPLETED.value
        ).all()
        total_withdrawals = sum(w.amount for w in withdrawals)
        
        # Calculate total adjustments
        adjustments = db.query(AdjustmentHistory).filter(
            AdjustmentHistory.user_id == user.id
        ).all()
        total_adjustments = sum(a.amount for a in adjustments)
        
        # Update balances
        user.withdrawable_balance = total_payouts - total_withdrawals + total_adjustments
        
        # Calculate total earnings from approved sales
        approved_sales = db.query(Sale).filter(
            Sale.user_id == user.id,
            Sale.status == SaleStatus.APPROVED.value
        ).all()
        user.total_earnings = sum(s.earning for s in approved_sales)
    
    db.commit()
    print("✓ Updated user balances")


def seed_all() -> None:
    """Seed all data."""
    db = SessionLocal()
    
    try:
        print("Starting data seeding...")
        print("-" * 40)
        
        # Clear existing data
        print("Clearing existing data...")
        db.query(AdjustmentHistory).delete()
        db.query(Withdrawal).delete()
        db.query(Payout).delete()
        db.query(Sale).delete()
        db.query(User).delete()
        db.commit()
        print("✓ Cleared existing data")
        
        # Seed new data
        seed_users(db)
        seed_sales(db)
        seed_payouts(db)
        seed_withdrawals(db)
        seed_adjustments(db)
        update_balances(db)
        
        print("-" * 40)
        print("✓ Data seeding completed successfully!")
        
        # Print summary
        print("\nSummary:")
        print(f"  Users: {db.query(User).count()}")
        print(f"  Sales: {db.query(Sale).count()}")
        print(f"  Payouts: {db.query(Payout).count()}")
        print(f"  Withdrawals: {db.query(Withdrawal).count()}")
        print(f"  Adjustments: {db.query(AdjustmentHistory).count()}")
        
    except Exception as e:
        print(f"✗ Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_all()
