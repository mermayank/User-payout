"""Exception handling middleware."""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.core.exceptions import AppError


async def app_exception_handler(request: Request, exc: AppError) -> JSONResponse:
    """
    Handle application exceptions.
    
    Args:
        request: FastAPI request
        exc: Application exception
        
    Returns:
        JSON response with error details
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "status_code": exc.status_code
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle generic exceptions.
    
    Args:
        request: FastAPI request
        exc: Generic exception
        
    Returns:
        JSON response with error details
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc) if isinstance(exc, Exception) else None
        }
    )
