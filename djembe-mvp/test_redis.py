import redis

# Connect to Redis
redis_client = redis.Redis(
    host='localhost',
    port=6379,
    decode_responses=True
)

# Test the connection
try:
    response = redis_client.ping()
    print("Redis connection successful! Response:", response)
except redis.ConnectionError as e:
    print("Failed to connect to Redis:", e)