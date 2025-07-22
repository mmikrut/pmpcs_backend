# System Design Document: Lightweight P2P Message-Based Payment Confirmation Backend (Decentralized Update)

## 1. Introduction

### 1.1 Purpose
This System Design Document (SDD), updated as of July 22, 2025, provides a detailed blueprint for the development of a lightweight peer-to-peer (P2P) backend system focused on message-based payment confirmations. Derived from the updated project proposal, this document outlines the system's architecture, components, data flows, and implementation considerations to ensure secure, efficient, and extensible functionality. The system enables users to generate and process payment-related messages or QR code images via a RESTful API, facilitating verifiable confirmations without handling actual payments.

This update incorporates a decentralized architecture using Decentralized Identifiers (DIDs) and W3C Verifiable Credentials (VCs) to eliminate reliance on central sessions, allowing peer verification via cryptographic proofs. It also adds user validation features, including a new endpoint for decoding messages to JSON and confirming validity, enhancing transparency in Phase 1. Additionally, this revision addresses a flow correction in confirmation processing, ensuring that payment updates occur only upon payee acknowledgment.

### 1.2 Scope
The system will include core API endpoints for payment requests, confirmations, status queries, and message validation; support for compact messages and QR codes; verifiable credentials; and basic session management. It excludes payment execution, regulatory compliance, and advanced fraud detection, delegating these to external systems. The design emphasizes minimalism, security, and compatibility with arbitrary messaging platforms, with a shift to decentralization for future phases.

### 1.3 References
- Project Proposal: Development of a Lightweight P2P Message-Based Payment Confirmation Backend (Decentralized Update, dated July 22, 2025).

### 1.4 Assumptions and Constraints
- Development and deployment will occur on Linux environments.
- Users interact via RESTful API calls; no frontend is included in the initial scope.
- Messages and QR codes must be compact for copy-paste or image sharing in limited-character or low-connectivity settings.
- The system assumes reliable timestamp synchronization and basic cryptographic libraries.
- Decentralization assumes user-managed DIDs and local verification tools in later phases.

## 2. System Architecture

### 2.1 High-Level Overview
The system adopts a monolithic backend architecture for simplicity in Phase 1, built on FastAPI for API exposure and SQLite for data persistence. It operates as a stateless service where possible, with session state stored in the database. Key components include:
- **API Layer**: Handles incoming requests and orchestrates business logic.
- **Message Processor**: Encodes/decodes messages and QR codes, including compression and verification.
- **Credential Manager**: Generates and validates W3C Verifiable Credentials (VCs).
- **Storage Layer**: Manages session data, message IDs, and certificates (used in hybrid mode; phased out for full decentralization).
- **QR Handler**: Generates and decodes QR codes using dedicated libraries.
- **Validation Module**: Decodes messages to JSON and performs validity checks (new in Phase 1).

The architecture supports extensibility through modular components, allowing future migrations to decentralized models (e.g., DID/VC-based P2P verification without central storage).

### 2.2 Component Diagram
The system comprises the following interconnected components:

- **Client Interface**: External clients (e.g., users or applications) interact via HTTP requests to the API endpoints.
- **FastAPI Server**: Routes requests to handlers, performs input validation using Pydantic, and returns responses.
- **Business Logic Modules**:
  - Payment Request Handler: Generates messages/QR codes with session details.
  - Confirmation Handlers: Processes sent/received confirmations, updates sessions, and issues certificates.
  - Session Query Handler: Retrieves status from storage.
  - Message Validation Handler: Decodes to JSON and checks validity (new).
- **Utility Modules**:
  - Compression/Decompression: Uses zlib for message compactness.
  - Cryptography: Employs the cryptography library for signatures and proofs.
  - QR Code Generator/Decoder: Utilizes qrcode for generation and pyzbar with Pillow for decoding.
- **Database (SQLite)**: Stores sessions, message IDs, preferences, and certificates (used in hybrid mode; phased out for full decentralization).

Data flows unidirectionally from API to business logic, utilities, and storage, with responses flowing back. In decentralized mode, flows shift to local verification.

### 2.3 Deployment Architecture
- **Development**: Local Linux laptop with direct execution.
- **Testing/Production**: Dockerized containers on Linux cloud instances for portability and scalability.
- **Scaling Considerations**: Initial single-instance deployment; horizontal scaling via load balancers if session volume increases, with potential migration to PostgreSQL for distributed storage. For decentralization, deploy as client-side libraries or P2P nodes.

## 3. Data Models

### 3.1 Database Schema
The system uses SQLite with the following tables (legacy mode):

- **Sessions**:
  - session_id (PRIMARY KEY, UUID): Unique identifier.
  - requested_amount (DECIMAL): Payment amount.
  - currency (STRING): Currency code (e.g., USD, BTC).
  - recipient_id (STRING): Payee identifier.
  - description (STRING): Transaction details.
  - preferences (JSON): Array of payment method objects (e.g., {"method": "BTC", "wallet": "address"}).
  - status (ENUM: pending, sent, received): Current state.
  - paid_amount (DECIMAL, DEFAULT 0): Cumulative paid amount for partial payments.
  - expiry_timestamp (DATETIME): Invalidation time.
  - created_at (DATETIME DEFAULT CURRENT_TIMESTAMP): Creation timestamp.

- **Messages**:
  - message_id (PRIMARY KEY, UUID): Unique ID for duplicate prevention.
  - session_id (FOREIGN KEY): Linked session.
  - type (ENUM: request, sent, received): Message category.
  - payload (BLOB): Compressed JSON data.
  - transaction_proof (STRING, OPTIONAL): Sender-provided proof.

- **Certificates**:
  - certificate_id (PRIMARY KEY, UUID): Unique ID.
  - session_id (FOREIGN KEY): Linked session.
  - vc_data (JSON): W3C VC structure with claims, proofs, and timestamps.

Indexes will be applied on session_id and message_id for efficient queries. In decentralized mode, schemas shift to local VC storage.

### 3.2 Message Format
Messages are JSON objects compressed with zlib and Base64-encoded:
- Structure: {"session_id": UUID, "message_id": UUID, "type": STRING, "amount": DECIMAL, "currency": STRING, "preferences": ARRAY, "expiry": TIMESTAMP, "proof": STRING (optional), "vc": OBJECT (optional)}.
QR codes embed the same encoded payload for alternative transmission.

### 3.3 Verifiable Credentials
Follow W3C VC Data Model:
- Issuer: System backend or user DID.
- Claims: Payment details (e.g., amount, parties, partial status).
- Proof: Cryptographic signature using ECDSA or similar.

## 4. API Design

### 4.1 Endpoints
- **POST /paymentRequest**:
  - Request Body: JSON with amount, currency, recipient_id, description, preferences (array).
  - Response: JSON with encoded_message (Base64), qr_code (Base64 image, optional), session_id.
  
- **POST /paymentSent**:
  - Request Body: JSON with session_id, paid_amount, transaction_proof, custom_method (optional).
  - Response: JSON with confirmation_message (Base64), qr_code (optional), certificate (VC JSON).
  
- **POST /paymentReceived**:
  - Request Body: JSON with encoded_message or qr_code (Base64 image).
  - Response: JSON with validation_result (BOOLEAN), certificate (if valid), updated_status.
  
- **POST /decodeMessage**:
  - Request Body: JSON with encoded_message or qr_code (Base64 image).
  - Response: JSON with decoded_data (OBJECT), valid (BOOLEAN), validation_details (STRING).
  
- **GET /session/{session_id}**:
  - Response: JSON with status, requested_amount, paid_amount, preferences, certificate.

### 4.2 Error Handling
Standard HTTP status codes (e.g., 400 for invalid input, 404 for expired sessions). Responses include descriptive error messages.

### 4.3 Security Features
- Input validation via Pydantic.
- Signature verification on credentials.
- Expiry and duplicate checks in business logic.
- Basic validity confirmation in /decodeMessage.

## 5. Functional Flows

### 5.1 Payment Request Flow
1. Client sends POST /paymentRequest.
2. System generates session, stores in DB, creates encoded message/QR.
3. Returns artifacts for sharing.

### 5.2 Confirmation Flow
1. Sender processes request, sends POST /paymentSent with claim of payment.
2. System validates session, issues VC for the claim, but does not update paid_amount or status (claim is pending payee confirmation).
3. Payee sends POST /paymentReceived with message/QR.
4. System decodes, validates, updates paid_amount and status upon payee acknowledgment, returns VC.

### 5.3 Message Validation Flow (New)
1. Client sends POST /decodeMessage with encoded_message or QR.
2. System decodes, checks validity (e.g., expiry), returns JSON and flag.

### 5.4 Query Flow
1. Client sends GET /session/{id}.
2. System retrieves and returns DB data.

## 6. Non-Functional Requirements

### 6.1 Performance
- Response time: <500ms for API calls.
- Throughput: Handle 100 concurrent sessions initially.

### 6.2 Security
- Use HTTPS for all communications.
- Cryptographic proofs prevent tampering.
- No sensitive data storage beyond sessions.

### 6.3 Reliability
- Database transactions ensure atomicity.
- Logging for audits.

### 6.4 Maintainability
- Modular code structure.
- Unit tests with pytest.

## 7. Risks and Mitigations
- Message/QR size: Mitigated by compression and testing.
- User errors: Addressed via validation and fallbacks.
- Scalability: Monitored with option for DB upgrade.
- Decentralization complexity: Introduced gradually in Phase 2.

## 8. Future Considerations
- Full DID/VC integration for P2P verification.
- UI integration.
- Wallet/gateway support.
- Direct P2P networking.
- Chatbot interfaces.

This document serves as a comprehensive guide for implementation. Feedback is welcomed to refine the design prior to prototyping.