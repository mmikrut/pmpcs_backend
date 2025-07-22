from utils import encode_message, decode_message

# Test data
test_payload = {
    "session_id": "test_session",
    "message_id": "test_message",
    "type": "request",
    "amount": 100.0,
    "currency": "USD",
    "preferences": [{"method": "BTC", "wallet": "test_address"}],
    "expiry": "2025-07-30T00:00:00"
}

# Encode and decode
encoded = encode_message(test_payload)
print(f"Encoded message: {encoded}")

decoded = decode_message(encoded)
print(f"Decoded message: {decoded}")
