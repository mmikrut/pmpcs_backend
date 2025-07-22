from models import PaymentRequest, PaymentSent, PaymentReceived
from datetime import datetime

# Test valid data
valid_request = PaymentRequest(
    amount=100.0,
    currency="USD",
    recipient_id="user1",
    description="Test payment",
    preferences=[{"method": "BTC", "wallet": "test_address"}],
    expiry=datetime(2025, 7, 30)
)
print(f"Valid request: {valid_request}")

valid_sent = PaymentSent(
    session_id="test_session",
    paid_amount=100.0
)
print(f"Valid sent: {valid_sent}")

valid_received = PaymentReceived(
    encoded_message="test_encoded_message"
)
print(f"Valid received: {valid_received}")

# Test invalid data (optional, to check validation)
try:
    invalid_request = PaymentRequest(
        amount="invalid",  # Should raise validation error
        currency="USD",
        recipient_id="user1",
        description="Test payment",
        preferences=[{"method": "BTC", "wallet": "test_address"}],
        expiry=datetime(2025, 7, 30)
    )
except ValueError as e:
    print(f"Validation error: {e}")
