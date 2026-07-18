# API Examples

## Base URL
```
http://localhost:8000/api/v1
```

## 1. Create a User

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "username": "johndoe"
  }'
```

**Response:**
```json
{
  "id": 1,
  "email": "john.doe@example.com",
  "username": "johndoe",
  "withdrawable_balance": 0.0,
  "total_earnings": 0.0,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

## 2. Get User Balance

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/balance?user_id=1"
```

**Response:**
```json
{
  "user_id": 1,
  "withdrawable_balance": 100.0,
  "total_earnings": 200.0
}
```

## 3. Create a Sale

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/sales" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "brand": "Nike",
    "earning": 100.0
  }'
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "brand": "Nike",
  "earning": 100.0,
  "status": "pending",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

## 4. Get All Sales

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/sales?skip=0&limit=100"
```

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "brand": "Nike",
    "earning": 100.0,
    "status": "pending",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
]
```

## 5. Create Advance Payout

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/advance-payout" \
  -H "Content-Type: application/json" \
  -d '{
    "sale_id": 1
  }'
```

**Response:**
```json
{
  "id": 1,
  "sale_id": 1,
  "user_id": 1,
  "type": "advance",
  "amount": 10.0,
  "status": "completed",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

## 6. Reconcile Sale (Admin)

**Approve a sale:**
```bash
curl -X POST "http://localhost:8000/api/v1/admin/reconcile" \
  -H "Content-Type: application/json" \
  -d '{
    "sale_id": 1,
    "status": "approved"
  }'
```

**Reject a sale:**
```bash
curl -X POST "http://localhost:8000/api/v1/admin/reconcile" \
  -H "Content-Type: application/json" \
  -d '{
    "sale_id": 2,
    "status": "rejected"
  }'
```

**Response (Approved):**
```json
{
  "id": 1,
  "user_id": 1,
  "brand": "Nike",
  "earning": 100.0,
  "status": "approved",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:01"
}
```

## 7. Create Withdrawal

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/withdraw" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "amount": 50.0
  }'
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "amount": 50.0,
  "status": "pending",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

## 8. Get User Withdrawals

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/withdrawals?user_id=1&skip=0&limit=100"
```

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "amount": 50.0,
    "status": "pending",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
]
```

## 9. Get All Payouts

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/payouts?skip=0&limit=100"
```

**Response:**
```json
[
  {
    "id": 1,
    "sale_id": 1,
    "user_id": 1,
    "type": "advance",
    "amount": 10.0,
    "status": "completed",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  },
  {
    "id": 2,
    "sale_id": 1,
    "user_id": 1,
    "type": "reconciliation",
    "amount": 90.0,
    "status": "completed",
    "created_at": "2024-01-01T00:00:01",
    "updated_at": "2024-01-01T00:00:01"
  }
]
```

## 10. Get User Payouts

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/payouts?user_id=1&skip=0&limit=100"
```

## Complete Workflow Example

### Step 1: Create a user
```bash
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "username": "testuser"}'
```

### Step 2: Create a sale
```bash
curl -X POST "http://localhost:8000/api/v1/sales" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "brand": "Nike", "earning": 100.0}'
```

### Step 3: Request advance payout (10%)
```bash
curl -X POST "http://localhost:8000/api/v1/advance-payout" \
  -H "Content-Type: application/json" \
  -d '{"sale_id": 1}'
```

### Step 4: Check balance
```bash
curl -X GET "http://localhost:8000/api/v1/balance?user_id=1"
```
Expected: withdrawable_balance = 10.0

### Step 5: Approve the sale
```bash
curl -X POST "http://localhost:8000/api/v1/admin/reconcile" \
  -H "Content-Type: application/json" \
  -d '{"sale_id": 1, "status": "approved"}'
```

### Step 6: Check balance again
```bash
curl -X GET "http://localhost:8000/api/v1/balance?user_id=1"
```
Expected: withdrawable_balance = 100.0, total_earnings = 100.0

### Step 7: Create a withdrawal
```bash
curl -X POST "http://localhost:8000/api/v1/withdraw" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "amount": 50.0}'
```

### Step 8: Check final balance
```bash
curl -X GET "http://localhost:8000/api/v1/balance?user_id=1"
```
Expected: withdrawable_balance = 50.0

## Error Responses

### 404 Not Found
```json
{
  "detail": "User with id 999 not found"
}
```

### 400 Bad Request
```json
{
  "detail": "Insufficient balance. Available: 10.0, Requested: 50.0"
}
```

### 409 Conflict (Idempotency)
```json
{
  "detail": "Advance payout already exists for sale 1"
}
```

### 429 Too Many Requests (Cooldown)
```json
{
  "detail": "User can only withdraw once every 24 hours"
}
```

## Using Swagger UI

Visit `http://localhost:8000/docs` for interactive API documentation with:
- Try it out buttons
- Request/response examples
- Schema validation
- Authentication (when implemented)
