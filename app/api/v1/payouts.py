"""Payouts API endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.payout import PayoutResponse
from app.repositories.payout import PayoutRepository

router = APIRouter()


def get_payout_repository() -> PayoutRepository:
    """Get payout repository."""
    return PayoutRepository()


@router.get("/payouts", response_model=List[PayoutResponse])
def get_payouts(
    user_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    payout_repo: PayoutRepository = Depends(get_payout_repository)
) -> List[PayoutResponse]:
    """
    Get payouts with optional user filter.
    
    Args:
        user_id: Optional user ID to filter by
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        payout_repo: Payout repository
        
    Returns:
        List of payouts
    """
    if user_id:
        return payout_repo.get_by_user(db, user_id, skip=skip, limit=limit)
    return payout_repo.get_all(db, skip=skip, limit=limit)


@router.get("/payouts/{payout_id}", response_model=PayoutResponse)
def get_payout(
    payout_id: int,
    db: Session = Depends(get_db),
    payout_repo: PayoutRepository = Depends(get_payout_repository)
) -> PayoutResponse:
    """
    Get a payout by ID.
    
    Args:
        payout_id: Payout ID
        db: Database session
        payout_repo: Payout repository
        
    Returns:
        Payout
        
    Raises:
        HTTPException: If payout not found
    """
    payout = payout_repo.get(db, payout_id)
    if not payout:
        raise HTTPException(status_code=404, detail=f"Payout with id {payout_id} not found")
    return payout
