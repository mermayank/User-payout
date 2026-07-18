# User Payout Management System

A production-ready system for managing user sales, advance payouts, reconciliations, and withdrawals with idempotent operations and comprehensive balance tracking.

## Features

- **Sales Management**: Create and track sales with different statuses (pending, approved, rejected)
- **Advance Payouts**: Idempotent 10% advance payout for pending sales
- **Reconciliation**: Admin approval/rejection with automatic balance adjustments
- **Withdrawals**: User withdrawals with 24-hour cooldown enforcement
- **Failed Recovery**: Automatic recovery of failed transactions
- **Adjustment Tracking**: Complete audit trail of all balance adjustments

## Tech Stack

- **Python 3.12**
- **FastAPI** - Web framework
- **SQLAlchemy ORM** - Database ORM
- **SQLite** - Database (easily switchable to PostgreSQL)
- **Alembic** - Database migrations
- **Pydantic V2** - Data validation
- **Pytest** - Testing framework
- **Docker** - Containerization

## Architecture

The system follows Clean Architecture principles with clear separation of concerns:

```
app/
├── api/              # API layer (FastAPI routers)
├── core/             # Core configuration and utilities
├── database/         # Database configuration
├── models/           # SQLAlchemy models
├── repositories/     # Repository pattern (data access)
├── services/         # Business logic layer
├── schemas/          # Pydantic schemas
├── utils/            # Utility functions
└── middleware/       # Custom middleware
```

### Design Patterns

- **Repository Pattern**: Abstract data access logic
- **Service Layer**: Business logic encapsulation
- **Dependency Injection**: Loose coupling between components
- **Transaction Management**: Database integrity

## Installation

### Prerequisites

- Python 3.12+
- pip

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd user-payout-system
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run database migrations:
```bash
alembic upgrade head
```

4. Start the server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Docker Setup

1. Build and run with Docker Compose:
```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Users

- `POST /api/v1/users` - Create a new user
- `GET /api/v1/users` - Get all users (paginated)
- `GET /api/v1/users/{user_id}` - Get user by ID
- `GET /api/v1/balance?user_id={id}` - Get user balance

### Sales

- `POST /api/v1/sales` - Create a new sale
- `GET /api/v1/sales` - Get all sales (paginated)
- `GET /api/v1/sales/{sale_id}` - Get sale by ID
- `POST /api/v1/advance-payout` - Create advance payout for a sale
- `POST /api/v1/admin/reconcile` - Reconcile a sale (admin)

### Withdrawals

- `POST /api/v1/withdraw` - Create a withdrawal request
- `GET /api/v1/withdrawals` - Get所有 withdrawals (paginated)
- `GET /api/v1/withdrawals/{withdrawal_id}` - Get withdrawal by ID

### Payouts

- `GET /api/v1/payouts` - Get all payouts (paginated)
- `GET /api/v1/payouts/{payout_id}` - Get payout by ID

## Business Logic

### Advance Payout

- Every pending sale is eligible for a 10% advance payout
- Advance payout必须是idempotent的 - running multiple times won't duplicate
- Unique constraint on (sale_id, payout_type) prevents duplicates

### Reconciliation

**Approved Sale:**
- Remaining payout = earning - advance_paid
- Remaining amount credited to user's withdrawable balance
- Total earnings updated

**Rejected Sale:**
- Previously paid advance is recovered via negative adjustment
- User's withdrawable balance debited by advance amount
- Adjustment history records the recovery

### Withdrawals

- Users can withdraw once every 24 hours
- Withdrawal amount must not exceed withdrawable balance
- Failed/cancelled/rejected withdrawals are automatically recovered

### Failed Recovery

- Failed payouts credit amount back to user
- Failed withdrawals credit amount back to user
- Adjustment history tracks all recoveries

## Database Schema

### Tables

**users**
- id (PK)
- email (unique)
- username (unique)
- withdrawable_balance
- total_earnings
- created_at
- updated_at

**sales**
- id (PK)
- user_id (FK)
- brand
- earning
- status (pending/approved/rejected)
- created_at
- updated_at

**payouts**
- id (PK)
- sale_id (FK)
- user_id (FK)
- type (advance/reconciliation)
- amount
- status (pending/completed/failed/cancelled/rejected)
- created_at
- updated_at

**withdrawals**
- id (PK)
- user_id (FK)
- amount
- status (pending/completed/failed/cancelled/rejected)
- created_at
- updated_at

**adjustment_history**
- id (PK)
- user_id (FK)
- sale_id (FK, nullable)
- withdrawal_id (FK, nullable)
- payout_id (FK, nullable)
- type (recovery/refund/credit/debit)
- amount (negative for debits)
- reason
- created_at

### Indexes

- Unique constraints on email, username
- Composite index on (user_id, status) for sales
- Unique constraint on (sale_id, type) for payouts
- Indexes on foreign keys for performance
- Time-based indexes for withdrawal cooldown checks

## Testing

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_payout_service.py
```

### Test Coverage

- Advance payout processing
- Idempotency verification
- Reconciliation (approved/rejected)
- Withdrawal cooldown enforcement
- Failed transaction recovery
- API endpoint testing
- Edge cases and error handling

## Configuration

Environment variables can be set in `.env` file:

```env
DATABASE_URL=sqlite:///./payout_system.db
DEBUG=True
SECRET_KEY=your-secret-key
ADVANCE_PAYOUT_PERCENTAGE=0.10
WITHDRAWAL_COOLDOWN_HOURS=24
```

## Design Decisions

### SQLite vs PostgreSQL
- **Chosen**: SQLite for development/simplicity
- **Trade-off**: SQLite is file-based, not suitable for high-concurrency production
- **Future**: Easy switch to PostgreSQL via DATABASE_URL

### Idempotency Strategy
- **Chosen**: Unique constraint on (sale_id, payout_type)
- **Trade-off**: Database-level constraint adds slight overhead
- **Benefit**: Guarantees no duplicates even under race conditions

### Withdrawal Cooldown
- **Chosen**: Application-level check with database query
- **Trade-off**: Requires database read on each withdrawal
- **Benefit**: Simple implementation, accurate enforcement

### Balance Updates
- **Chosen**: Direct updates in service layer with transactions
- **Trade-off**: Requires careful transaction management
- **Benefit**: Immediate consistency, no eventual consistency issues

## Trade-offs

1. **Synchronous Processing**: Payouts and withdrawals are processed synchronously
   - *Benefit*: Simpler implementation, immediate feedback
   - *Trade-off*: Not suitable for high-volume scenarios
   
2. **SQLite Database**: Used for simplicity
   - *Benefit*: No external dependencies, easy setup
   - *Trade-off*: Limited concurrency, not production-ready for scale
   
3. **No Authentication**: API is open for simplicity
   - *Benefit*: Easy testing and development
   - *Trade-off*: Not secure for production deployment

## Future Enhancements

- Add JWT authentication
- Implement async task queue (Celery/RQ) for background processing
- Switch to PostgreSQL for production
- Add rate limiting
- Implement webhook notifications
- Add admin dashboard
- Support multiple currencies
- Add analytics and reporting

## Folder Structure

```
user-payout-system/
├── app/
│   ├── api/
│   │   ├── deps.py
│   │   └── v1/
│   │       ├── sales.py
│   │       ├── withdrawals.py
│   │       ├── users.py
│   │       └── payouts.py
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py
│   │   ├── security.py
│   │   └── exceptions.py
│   ├── database/
│   │   ├── base.py
│   │   └── session.py
│   ├── models/
│   │   ├── user.py
│   │   ├── sale.py
│   │   ├── payout.py
│   │   ├── withdrawal.py
│   │   └── adjustment.py
│   ├── repositories/
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── sale.py
│   │   ├── payout.py
│   │   ├── withdrawal.py
│   │   └── adjustment.py
│   ├── services/
│   │   ├── payout_service.py
│   │   ├── reconciliation_service.py
│   │   ├── withdrawal_service.py
│   │   └── recovery_service.py
│   ├── schemas/
│   │   ├── user.py
│   │   ├── sale.py
│   │   ├── payout.py
│   │   ├── withdrawal.py
│   │   └── adjustment.py
│   ├── utils/
│   │   └── validators.py
│   ├── middleware/
│   │   └── exception_handler.py
│   └── main.py
├── alembic/
│   ├── versions/
│   │   └── 001_initial_schema.py
│   ├── env.py
│   └── script.py.mako
├── tests/
│   ├── conftest.py
│   ├── test_payout_service.py
│   ├── test_reconciliation_service.py
│   ├── test_withdrawal_service.py
│   └── test_api.py
├── logs/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── alembic.ini
├── pytest.ini
└── README.md
```

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request
