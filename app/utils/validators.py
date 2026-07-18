"""Validation utilities."""

from typing import Optional
from decimal import Decimal


def validate_positive_amount(amount: float) -> bool:
    """
    Validate that an amount is positive.
    
    Args:
        amount: Amount to validate
        
    Returns:
        True if valid, False otherwise
    """
    return amount > 0


def validate_non_negative_amount(amount: float) -> bool:
    """
    Validate that an amount is non-negative.
    
    Args:
        amount: Amount to validate
        
    Returns:
        True if valid, False otherwise
    """
    return amount >= 0


def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email to validate
        
    Returns:
        True if valid, False otherwise
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_username(username: str) -> bool:
    """
    Validate username format.
    
    Args:
        username: Username to validate
        
    Returns:
        True if valid, False otherwise
    """
    import re
    # Username: 3-100 characters, alphanumeric and underscores
    pattern = r'^[a-zA-Z0-9_]{3,100}$'
    return re.match(pattern, username) is not None


def round_to_decimals(amount: float, decimals: int = 2) -> float:
    """
    Round amount to specified decimals.
    
    Args:
        amount: Amount to round
        decimals: Number of decimal places
        
    Returns:
        Rounded amount
    """
    return round(amount, decimals)
