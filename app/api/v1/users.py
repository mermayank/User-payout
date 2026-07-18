"""Users API endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.user import UserCreate, UserResponse, BalanceResponse
from app.repositories.user import UserRepository

router = APIRouter()


def get_user_repository() -> UserRepository:
    """Get user repository."""
    return UserRepository()


@router.post("/users", response_model=UserResponse, status_code=201)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    user_repo: UserRepository = Depends(get_user_repository)
) -> UserResponse:
    """
    Create a new user.
    
    Args:
        user: User data
        db: Database session
        user_repo: User repository
        
    Returns:
        Created user
        
    Raises:
        HTTPException: If email or username already exists
    """
    # Check if email exists
    if user_repo.get_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if username exists
    if user_repo.get_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create user
    created_user = user_repo.create(
        db,
        email=user.email,
        username=user.username,
        withdrawable_balance=0.0,
        total_earnings=0.0
    )
    
    return created_user


@router.get("/users", response_model=List[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user_repo: UserRepository = Depends(get_user_repository)
) -> List[UserResponse]:
    """
    Get all users with pagination.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        user_repo: User repository
        
    Returns:
        List of users
    """
    return user_repo.get_all(db, skip=skip, limit=limit)


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    user_repo: UserRepository = Depends(get_user_repository)
) -> UserResponse:
    """
    Get a user by ID.
    
    Args:
        user_id: User ID
        db: Database session
        user_repo: User repository
        
    Returns:
        User
        
    Raises:
        HTTPException: If user not found
    """
    user = user_repo.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
    return user


@router.get("/balance", response_model=BalanceResponse)
def get_balance(
    user_id: int,
    db: Session = Depends(get_db),
    user_repo: UserRepository = Depends(get_user_repository)
) -> BalanceResponse:
    """
    Get user balance.
    
    Args:
        user_id: User ID
        db: Database session
        user_repo: User repository
        
    Returns:
        User balance
        
    Raises:
        HTTPException: If user not found
    """
    user = user_repo.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
    
    return BalanceResponse(
        user_id=user.id,
        withdrawable_balance=user.withdrawable_balance,
        total_earnings=user.total_earnings
    )
