"""Integration tests for document upload API."""

import asyncio

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_upload_txt_document(client: AsyncClient, auth_headers) -> None:
    """Authenticated users can upload TXT files."""
    headers = await auth_headers(email="upload@example.com")
    files = {"file": ("policy.txt", b"Our PTO policy grants 20 days annually.", "text/plain")}
    response = await client.post("/api/v1/upload", headers=headers, files=files)
    assert response.status_code == 201
    data = response.json()
    assert data["original_filename"] == "policy.txt"
    assert data["file_type"] == "txt"
    assert data["status"] == "pending"

    await asyncio.sleep(0.1)

    doc_id = data["id"]
    detail = await client.get(f"/api/v1/documents/{doc_id}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["status"] in {"processing", "completed"}


@pytest.mark.asyncio
async def test_upload_requires_authentication(client: AsyncClient) -> None:
    """Upload without JWT returns 401."""
    files = {"file": ("notes.txt", b"hello", "text/plain")}
    response = await client.post("/api/v1/upload", files=files)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_upload_rejects_invalid_extension(client: AsyncClient, auth_headers) -> None:
    """Unsupported file types return 422."""
    headers = await auth_headers(email="badext@example.com")
    files = {"file": ("malware.exe", b"MZ", "application/octet-stream")}
    response = await client.post("/api/v1/upload", headers=headers, files=files)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_documents(client: AsyncClient, auth_headers) -> None:
    """GET /documents returns uploaded files."""
    headers = await auth_headers(email="list@example.com")
    files = {"file": ("guide.txt", b"User guide content.", "text/plain")}
    await client.post("/api/v1/upload", headers=headers, files=files)

    response = await client.get("/api/v1/documents", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert data["documents"][0]["original_filename"] == "guide.txt"


@pytest.mark.asyncio
async def test_get_document_not_found(client: AsyncClient, auth_headers) -> None:
    """Unknown document ID returns 404."""
    headers = await auth_headers(email="notfound@example.com")
    response = await client.get(
        "/api/v1/documents/00000000-0000-0000-0000-000000000099",
        headers=headers,
    )
    assert response.status_code == 404
