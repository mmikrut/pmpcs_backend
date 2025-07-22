from fastapi import APIRouter, HTTPException
from .models import PaymentRequest, PaymentSent, PaymentReceived
from .database import create_session, get_session, get_db_connection
from .utils import encode_message, decode_message
import uuid

router = APIRouter()

@router.post("/paymentRequest")
def payment_request(request: PaymentRequest):
    session_id = create_session(request.dict())
    payload = {
        "session_id": session_id,
        "message_id": str(uuid.uuid4()),
        "type": "request",
        "amount": request.amount,
        "currency": request.currency,
        "preferences": request.preferences,
        "expiry": request.expiry.isoformat()
    }
    encoded = encode_message(payload)
    return {"encoded_message": encoded, "session_id": session_id}

@router.post("/paymentSent")
def payment_sent(sent: PaymentSent):
    session = get_session(sent.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    # Update paid_amount and status (simplified for MVP)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE sessions SET paid_amount = ?, status = 'sent' WHERE session_id = ?",
                       (sent.paid_amount, sent.session_id))
        conn.commit()
    payload = {"session_id": sent.session_id, "type": "sent", "paid_amount": sent.paid_amount}
    encoded = encode_message(payload)
    return {"confirmation_message": encoded}

@router.post("/paymentReceived")
def payment_received(received: PaymentReceived):
    try:
        payload = decode_message(received.encoded_message)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid message")
    session = get_session(payload["session_id"])
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    # Update status (simplified for MVP)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE sessions SET status = 'received' WHERE session_id = ?",
                       (payload["session_id"],))
        conn.commit()
    return {"validation_result": True, "updated_status": "received"}

@router.get("/session/{session_id}")
def get_session_status(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
