#!/bin/bash

# Check Redis
if redis-cli -h localhost ping > /dev/null 2>&1; 
then
    echo "Redis is running (PONG received)"
else
    echo "Redis is not running"
fi

# Check PostgreSQL (using correct psql syntax with 
password)
PGPASSWORD='DjembeMVP2025!' psql -U djembe_user -d 
djembe_db -h localhost -c "SELECT 1" > /dev/null 
2>&1
if [ $? -eq 0 ]; then
    echo "PostgreSQL is running"
else
    echo "PostgreSQL is not running"
fi

# Check FastAPI
if curl -s http://localhost:8000 > /dev/null 2>&1; 
then
    echo "FastAPI is running"
else
    echo "FastAPI is not running"
fi
