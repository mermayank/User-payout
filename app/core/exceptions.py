"""Custom exceptions for the application."""


class AppError(Exception):
    """Base application error."""
    
    def __init__(self, message: str, status_code: int = 400) -> None:
        """
        Initialize error.
        
        Args:
            message: Error message
            status_code: HTTP status code
        """
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class UserNotFoundError(AppError):
    """User not found error."""
    
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=404)


class SaleNotFoundError(AppError):
    """Sale not found error."""
    
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=404)


class PayoutNotFoundError(AppError):
    """Payout not found error."""
    
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=404)


class WithdrawalNotFoundError(AppError):
    """Withdrawal not found error."""
    
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=404)


class InvalidSaleStatusError(AppError):
    """Invalid sale status error."""
    
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=400)


class PayoutAlreadyExistsError(AppError):
    """Payout already exists error."""
    
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=409)


class InsufficientBalanceError(AppError):
    """Insufficient balance error."""
    
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=400)


class WithdrawalCooldownError(AppError):
    """Withdrawal cooldown error."""
    
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=429)
