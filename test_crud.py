from database import create_session, get_session

# Test data
test_data = {
    "amount": 100.0,
    "currency": "USD",
    "recipient_id": "user1",
    "description": "Test payment",
    "preferences": [{"method": "BTC", "wallet": "test_address"}],
    "expiry": "2025-07-30T00:00:00"
}

# Create a session
session_id = create_session(test_data)
print(f"Created session ID: {session_id}")

# Retrieve the session
session = get_session(session_id)
print(f"Retrieved session: {session}")
