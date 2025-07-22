from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict

class PaymentRequest(BaseModel):
    amount: float
    currency: str
    recipient_id: str
    description: str
    preferences: List[Dict[str, str]]
    expiry: datetime

class PaymentSent(BaseModel):
    session_id: str
    paid_amount: float
    transaction_proof: str = None

class PaymentReceived(BaseModel):
    encoded_message: str
