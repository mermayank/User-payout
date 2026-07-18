"""Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "User Payout Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./payout_system.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # Payout
    ADVANCE_PAYOUT_PERCENTAGE: float = 0.10  # 10%
    
    # Withdrawal
    WITHDRAWAL_COOLDOWN_HOURS: int = 24
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = True


settings = Settings()
