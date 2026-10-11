import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.storage.repository import repository

client = TestClient(app)

def test_api_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "healthy"}

def test_text_ingestion_and_analysis_flow(synthetic_paper_text):
    # 1. Ingest valid healthcare paper text
    payload = {
        "text": synthetic_paper_text,
        "title": "Cardiovascular Outcomes of Semaglutide in Diabetes"
    }
    resp = client.post("/api/documents/text", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data
    doc_id = data["id"]
    assert data["domain_validation"]["is_healthcare"] is True

    # 2. Status check
    stat_resp = client.get(f"/api/documents/{doc_id}/status")
    assert stat_resp.status_code == 200
    assert stat_resp.json()["status"] == "ingested"

    # 3. Trigger analyze with custom instructions
    analyze_payload = {
        "instructions": "Summarize key findings, statistical results, and limitations",
        "detail_level": "balanced",
        "topic_of_interest": "cardiovascular safety"
    }
    an_resp = client.post(f"/api/documents/{doc_id}/analyze", json=analyze_payload)
    assert an_resp.status_code == 200
    res_data = an_resp.json()
    assert res_data["document_id"] == doc_id
    assert len(res_data["structured_sections"]) > 0
    assert len(res_data["key_findings"]) > 0
    assert len(res_data["citations"]) > 0
    assert "Disease" in res_data["entities_by_category"]

    # 4. Fetch summary endpoint
    sum_resp = client.get(f"/api/documents/{doc_id}/summary")
    assert sum_resp.status_code == 200
    assert sum_resp.json()["title"] == res_data["title"]

def test_non_healthcare_paper_rejection(non_healthcare_text):
    payload = {
        "text": non_healthcare_text,
        "title": "Bitcoin Compiler Optimization"
    }
    resp = client.post("/api/documents/text", json=payload)
    assert resp.status_code == 200
    doc_data = resp.json()
    assert doc_data["domain_validation"]["is_healthcare"] is False

    # Attempting to analyze non-healthcare paper without confirmation override
    analyze_payload = {
        "instructions": "Summarize this paper",
        "confirm_healthcare_override": False
    }
    an_resp = client.post(f"/api/documents/{doc_data['id']}/analyze", json=analyze_payload)
    assert an_resp.status_code == 422
    assert "rejected" in an_resp.json()["detail"].lower()

def test_empty_or_too_short_text():
    payload = {"text": "Too short text"}
    resp = client.post("/api/documents/text", json=payload)
    assert resp.status_code == 422  # Pydantic min_length validation

def test_ssrf_blocked_url():
    payload = {"url": "http://127.0.0.1:8000/secret"}
    resp = client.post("/api/documents/url", json=payload)
    assert resp.status_code == 400
    assert "restricted" in resp.json()["detail"].lower()
