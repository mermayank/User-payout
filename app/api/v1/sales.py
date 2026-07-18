"""Sales API endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.sale import SaleCreate, SaleResponse, ReconcileRequest
from app.schemas.payout import PayoutResponse
from app.repositories.sale import SaleRepository
from app.repositories.user import UserRepository
from app.services.reconciliation_service import ReconciliationService
from app.services.payout_service import PayoutService
from app.core.exceptions import (
    SaleNotFoundError,
    InvalidSaleStatusError,
    UserNotFoundError
)

router = APIRouter()


def get_sale_repository() -> SaleRepository:
    """Get sale repository."""
    return SaleRepository()


def get_user_repository() -> UserRepository:
    """Get user repository."""
    return UserRepository()


def get_reconciliation_service(
    sale_repo: SaleRepository = Depends(get_sale_repository),
    user_repo: UserRepository = Depends(get_user_repository)
) -> ReconciliationService:
    """Get reconciliation service."""
    from app.repositories.payout import PayoutRepository
    from app.repositories.adjustment import AdjustmentRepository
    return ReconciliationService(
        sale_repo=sale_repo,
        payout_repo=PayoutRepository(),
        user_repo=user_repo,
        adjustment_repo=AdjustmentRepository()
    )


def get_payout_service(
    sale_repo: SaleRepository = Depends(get_sale_repository),
    user_repo: UserRepository = Depends(get_user_repository)
) -> PayoutService:
    """Get payout service."""
    from app.repositories.payout import PayoutRepository
    from app.repositories.adjustment import AdjustmentRepository
    return PayoutService(
        sale_repo=sale_repo,
        payout_repo=PayoutRepository(),
        user_repo=user_repo,
        adjustment_repo=AdjustmentRepository()
    )


@router.post("/sales", response_model=SaleResponse, status_code=201)
def create_sale(
    sale: SaleCreate,
    db: Session = Depends(get_db),
    user_repo: UserRepository = Depends(get_user_repository),
    sale_repo: SaleRepository = Depends(get_sale_repository)
) -> SaleResponse:
    """
    Create a new sale.
    
    Args:
        sale: Sale data
        db: Database session
        user_repo: User repository
        sale_repo: Sale repository
        
    Returns:
        Created sale
        
    Raises:
        HTTPException: If user not found
    """
    # Verify user exists
    user = user_repo.get(db, sale.user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {sale.user_id} not found")
    
    # Create sale
    created_sale = sale_repo.create(
        db,
        user_id=sale.user_id,
        brand=sale.brand,
        earning=sale.earning,
        status="pending"
    )
    
    return created_sale


@router.get("/sales", response_model=List[SaleResponse])
def get_sales(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    sale_repo: SaleRepository = Depends(get_sale_repository)
) -> List[SaleResponse]:
    """
    Get all sales with pagination.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        sale_repo: Sale repository
        
    Returns:
        List of sales
    """
    return sale_repo.get_all(db, skip=skip, limit=limit)


@router.get("/sales/{sale_id}", response_model=SaleResponse)
def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    sale_repo: SaleRepository = Depends(get_sale_repository)
) -> SaleResponse:
    """
    Get a sale by ID.
    
    Args:
        sale_id: Sale ID
        db: Database session
        sale_repo: Sale repository
        
    Returns:
        Sale
        
    Raises:
        HTTPException: If sale not found
    """
    sale = sale_repo.get(db, sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail=f"Sale with id {sale_id} not found")
    return sale


@router.post("/advance-payout", response_model=PayoutResponse, status_code=201)
def create_advance_payout(
    request: dict,
    db: Session = Depends(get_db),
    payout_service: PayoutService = Depends(get_payout_service)
) -> PayoutResponse:
    """
    Create an advance payout for a pending sale.
    
    This endpoint is idempotent - calling it multiple times for the same sale
    will not create duplicate payouts.
    
    Args:
        request: Request with sale_id
        db: Database session
        payout_service: Payout service
        
    Returns:
        Created payout
        
    Raises:
        HTTPException: If sale not found, invalid status, or payout already exists
    """
    try:
        payout = payout_service.process_advance_payout(db, request["sale_id"])
        return payout
    except SaleNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidSaleStatusError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        if "already exists" in str(e):
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/reconcile", response_model=SaleResponse)
def reconcile_sale(
    request: ReconcileRequest,
    db: Session = Depends(get_db),
    reconciliation_service: ReconciliationService = Depends(get_reconciliation_service)
) -> SaleResponse:
    """
    Reconcile a sale (admin endpoint).
    
    Approves or rejects a pending sale with proper balance adjustments.
    
    Args:
        request: Reconciliation request with sale_id and status
        db: Database session
        reconciliation_service: Reconciliation service
        
    Returns:
        Updated sale
        
    Raises:
        HTTPException: If sale not found or invalid status
    """
    try:
        from app.models.sale import SaleStatus
        sale = reconciliation_service.reconcile_sale(
            db, 
            request.sale_id, 
            SaleStatus(request.status)
        )
        return sale
    except SaleNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidSaleStatusError as e:
        raise HTTPException(status_code=400, detail=str(e))
