# Lightweight P2P Message-Based Payment Confirmation Backend

## Overview
This repository contains the prototype implementation of a lightweight peer-to-peer (P2P) backend system for message-based payment confirmations, as outlined in the Project Proposal and System Design Document (dated July 21, 2025). The system exposes a RESTful API for generating payment requests, processing confirmations, and querying session status. It emphasizes minimalism, security through verifiable messages, and compatibility with arbitrary messaging platforms via compact, encoded messages.

The Minimum Viable Product (MVP) focuses on core functionality: API endpoints, message encoding/decoding with compression, and basic session management using SQLite. It does not include verifiable credentials or QR code support, which are planned for future phases.

## Technology Stack
- **Language**: Python 3.12+
- **Framework**: FastAPI for API development
- **Database**: SQLite for session storage
- **Dependencies**: pydantic (validation), uvicorn (server), zlib (compression), base64 (encoding)
- **Environments**: Linux (development and production)

## Installation
1. **Clone the Repository** (if not already done):
   ```
   git clone <repository-url>
   cd pmpcs_backend
   ```

2. **Set Up Virtual Environment**:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```
   pip install fastapi uvicorn pydantic
   ```

## Running the Prototype
1. **Start the Server**:
   From the parent directory (`~/Dev`):
   ```
   cd ~/Dev
   source pmpcs_backend/venv/bin/activate
   python3 -m uvicorn pmpcs_backend.main:app --reload
   ```
   Alternatively, from within `pmpcs_backend`:
   ```
   PYTHONPATH=. python3 -m uvicorn pmpcs_backend.main:app --reload
   ```
   The server will run at `http://127.0.0.1:8000`. Use `--reload` for development to enable auto-restarting on code changes.

2. **Access API Documentation**:
   Open a web browser and navigate to `http://127.0.0.1:8000/docs` for interactive Swagger UI documentation of the endpoints.

## Usage
The API endpoints are as follows:

- **POST /paymentRequest**: Generates an encoded message and session ID for a payment request.
  - Example Body:
    ```json
    {
      "amount": 100.0,
      "currency": "USD",
      "recipient_id": "user1",
      "description": "Test payment",
      "preferences": [{"method": "BTC", "wallet": "test_address"}],
      "expiry": "2025-07-30T00:00:00"
    }
    ```
  - Response: Includes `encoded_message` (Base64 string) and `session_id` (UUID).

- **POST /paymentSent**: Processes sender confirmation and generates a confirmation message.
  - Example Body:
    ```json
    {
      "session_id": "<session_id_from_request>",
      "paid_amount": 100.0,
      "transaction_proof": "proof123"
    }
    ```
  - Response: Includes `confirmation_message` (Base64 string).

- **POST /paymentReceived**: Validates and processes the received confirmation message.
  - Example Body:
    ```json
    {
      "encoded_message": "<confirmation_message_from_sent>"
    }
    ```
  - Response: Includes `validation_result` (boolean) and `updated_status` (string).

- **GET /session/{session_id}**: Queries the session status.
  - Path Parameter: `session_id` (UUID from request).
  - Response: Full session details as JSON.

## Testing the Workflow
1. Use the Swagger UI to test endpoints sequentially, starting with `/paymentRequest`.
2. Verify updates in the SQLite database (`pmpcs.db`) using commands like:
   ```
   sqlite3 pmpcs.db "SELECT * FROM sessions;"
   ```

## Notes
- The MVP is designed for development and testing on Linux environments.
- No actual payments are processed; the system handles confirmations only.
- For production, consider Docker containerization and database migration to PostgreSQL.
- Future expansions include verifiable credentials, QR codes, and partial payments.

## License
This project is unlicensed for demonstration purposes. For production use, apply an appropriate open-source license.