"""Base repository with common CRUD operations."""

from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Base repository with common CRUD operations.
    
    Provides generic CRUD operations that can be inherited by specific repositories.
    
    Attributes:
        model: The SQLAlchemy model class
    """
    
    def __init__(self, model: Type[ModelType]) -> None:
        """
        Initialize repository.
        
        Args:
            model: The SQLAlchemy model class
        """
        self.model = model
    
    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """
        Get a single record by ID.
        
        Args:
            db: Database session
            id: Record ID
            
        Returns:
            The record if found, None otherwise
        """
        return db.get(self.model, id)
    
    def get_all(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[ModelType]:
        """
        Get all records with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of records
        """
        stmt = select(self.model).offset(skip).limit(limit)
        result = db.execute(stmt)
        return list(result.scalars().all())
    
    def create(self, db: Session, **kwargs) -> ModelType:
        """
        Create a new record.
        
        Args:
            db: Database session
            **kwargs: Field values for the record
            
        Returns:
            Created record
        """
        db_obj = self.model(**kwargs)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self, 
        db: Session, 
        db_obj: ModelType, 
        **kwargs
    ) -> ModelType:
        """
        Update a record.
        
        Args:
            db: Database session
            db_obj: Record to update
            **kwargs: Field values to update
            
        Returns:
            Updated record
        """
        for field, value in kwargs.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, db_obj: ModelType) -> None:
        """
        Delete a record.
        
        Args:
            db: Database session
            db_obj: Record to delete
        """
        db.delete(db_obj)
        db.commit()
    
    def count(self, db: Session) -> int:
        """
        Count all records.
        
        Args:
            db: Database session
            
        Returns:
            Number of records
        """
        stmt = select(self.model)
        result = db.execute(stmt)
        return len(result.scalars().all())
