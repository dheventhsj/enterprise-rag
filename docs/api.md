# API Reference

Base URL: `/api/v1`

Interactive docs: `/api/v1/docs`

## Authentication

All protected endpoints require:

```
Authorization: Bearer <access_token>
```

### POST /auth/register

Create account and receive JWT.

**Body:**
```json
{
  "email": "user@company.com",
  "password": "securepass123",
  "full_name": "Jane Doe"
}
```

### POST /auth/login

**Body:**
```json
{
  "email": "user@company.com",
  "password": "securepass123"
}
```

**Response:**
```json
{
  "access_token": "...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### GET /auth/me

Returns authenticated user profile.

---

## Documents

### POST /upload

Multipart form upload. Field name: `file`.

Supported: PDF, DOCX, TXT (max 25 MB default).

### GET /documents

List all documents for the authenticated user.

### GET /documents/{document_id}

Get document metadata and ingestion status.

### DELETE /document/{document_id}

Delete document, chunks, vectors, and stored file.

---

## Chat

### POST /chat

RAG-powered Q&A with source citations.

**Body:**
```json
{
  "message": "What is the PTO policy?",
  "conversation_id": null,
  "document_ids": null,
  "stream": false
}
```

**Response:**
```json
{
  "conversation_id": "...",
  "message": {
    "id": "...",
    "role": "assistant",
    "content": "...",
    "citations": [
      {
        "document_id": "...",
        "filename": "policy.pdf",
        "page_number": 3,
        "excerpt": "..."
      }
    ]
  }
}
```

Set `"stream": true` for Server-Sent Events token streaming.

### GET /history

List all conversations.

### GET /history/{conversation_id}

Get conversation with full message history.

---

## System

### GET /health

Liveness probe.

### GET /metrics

Prometheus metrics (request count, latency, RAG timings).
