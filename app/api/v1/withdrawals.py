"""Withdrawals API endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.withdrawal import WithdrawalCreate, WithdrawalResponse
from app.repositories.user import UserRepository
from app.repositories.withdrawal import WithdrawalRepository
from app.services.withdrawal_service import WithdrawalService
from app.core.exceptions import (
    UserNotFoundError,
    InsufficientBalanceError,
    WithdrawalCooldownError
)

router = APIRouter()


def get_user_repository() -> UserRepository:
    """Get user repository."""
    return UserRepository()


def get_withdrawal_repository() -> WithdrawalRepository:
    """Get withdrawal repository."""
    return WithdrawalRepository()


def get_withdrawal_service(
    user_repo: UserRepository = Depends(get_user_repository),
    withdrawal_repo: WithdrawalRepository = Depends(get_withdrawal_repository)
) -> WithdrawalService:
    """Get withdrawal service."""
    from app.repositories.adjustment import AdjustmentRepository
    return WithdrawalService(
        user_repo=user_repo,
        withdrawal_repo=withdrawal_repo,
        adjustment_repo=AdjustmentRepository()
    )


@router.post("/withdraw", response_model=WithdrawalResponse, status_code=201)
def create_withdrawal(
    request: dict,
    db: Session = Depends(get_db),
    withdrawal_service: WithdrawalService = Depends(get_withdrawal_service)
) -> WithdrawalResponse:
    """
    Create a withdrawal request.
    
    Users can only withdraw once every 24 hours.
    
    Args:
        request: Request with user_id and amount
        db: Database session
        withdrawal_service: Withdrawal service
        
    Returns:
        Created withdrawal
        
    Raises:
        HTTPException: If user not found, insufficient balance, or in cooldown
    """
    try:
        withdrawal = withdrawal_service.create_withdrawal(
            db,
            request["user_id"],
            request["amount"]
        )
        return withdrawal
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InsufficientBalanceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except WithdrawalCooldownError as e:
        raise HTTPException(status_code=429, detail=str(e))


@router.get("/withdrawals", response_model=List[WithdrawalResponse])
def get_withdrawals(
    user_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    withdrawal_repo: WithdrawalRepository = Depends(get_withdrawal_repository)
) -> List[WithdrawalResponse]:
    """
    Get withdrawals with optional user filter.
    
    Args:
        user_id: Optional user ID to filter by
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        withdrawal_repo: Withdrawal repository
        
    Returns:
        List of withdrawals
    """
    if user_id:
        return withdrawal_repo.get_by_user(db, user_id, skip=skip, limit=limit)
    return withdrawal_repo.get_all(db, skip=skip, limit=limit)


@router.get("/withdrawals/{withdrawal_id}", response_model=WithdrawalResponse)
def get_withdrawal(
    withdrawal_id: int,
    db: Session = Depends(get_db),
    withdrawal_repo: WithdrawalRepository = Depends(get_withdrawal_repository)
) -> WithdrawalResponse:
    """
    Get a withdrawal by ID.
    
    Args:
        withdrawal_id: Withdrawal ID
        db: Database session
        withdrawal_repo: Withdrawal repository
        
    Returns:
        Withdrawal
        
    Raises:
        HTTPException: If withdrawal not found
    """
    withdrawal = withdrawal_repo.get(db, withdrawal_id)
    if not withdrawal:
        raise HTTPException(status_code=404, detail=f"Withdrawal with id {withdrawal_id} not found")
    return withdrawal
