import redis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import time
from datetime import datetime

app = FastAPI()
redis_client = redis.Redis(
    host='localhost',
    port=6379,
    decode_responses=True
)

# Note: Update these connection details for your local PostgreSQL setup (we'll set this up in the next steps if needed)
conn = psycopg2.connect(
    database="djembe_db",
    user="djembe_user",
    password="DjembeMVP2025!",  # Replace with the password you set for djembe_user
    host="localhost",
    port="5432"
)

class TransactionRequest(BaseModel):
    qr_code: str
    user_id: str

class TransactionResponse(BaseModel):
    transaction_id: str
    amount: float
    fee: float
    status: str

@app.post("/api/transactions")
async def process_transaction(request: TransactionRequest):
    start_time = time.time()
    
    try:
        # Parse QR code (simplified for MVP – assume it contains merchant_id and amount)
        merchant_id, amount = parse_qr_code(request.qr_code)  # Implement parsing logic
        amount = float(amount)
        
        # Calculate fee (1% + $0.10)
        fee = amount * 0.01 + 0.10
        
        # Check user and merchant balances in Redis (for real-time)
        user_balance = float(redis_client.get(f"user:{request.user_id}:balance") or 0)
        merchant_balance = float(redis_client.get(f"merchant:{merchant_id}:balance") or 0)
        
        if user_balance < (amount + fee):
            raise HTTPException(status_code=400, detail="Insufficient funds")
        
        # Update balances (atomic in Redis)
        redis_client.decrby(f"user:{request.user_id}:balance", int((amount + fee) * 100))  # Cents for precision
        redis_client.incrby(f"merchant:{merchant_id}:balance", int(amount * 100))
        
        # Store transaction in PostgreSQL
        cursor = conn.cursor()
        transaction_id = f"txn_{datetime.now().strftime('%Y%m%d%H%M%S')}_{request.user_id}"
        cursor.execute("""
            INSERT INTO transactions (transaction_id, user_id, merchant_id, amount, fee, timestamp, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (transaction_id, request.user_id, merchant_id, amount, fee, datetime.now(), "completed"))
        conn.commit()
        cursor.close()
        
        # Ensure <1-second processing
        processing_time = time.time() - start_time
        if processing_time > 1:
            print(f"Warning: Transaction took {processing_time} seconds")
        
        return TransactionResponse(
            transaction_id=transaction_id,
            amount=amount,
            fee=fee,
            status="completed"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def parse_qr_code(qr_code: str) -> tuple:
    # Implement QR code parsing logic (e.g., JSON or custom format)
    # For MVP, assume format: "merchant001:10.00"
    parts = qr_code.split(':')
    return parts[0], parts[1]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)