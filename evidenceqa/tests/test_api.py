from pathlib import Path

from fastapi.testclient import TestClient

from app.database import init_db
from app.main import app


def make_client(tmp_path: Path) -> TestClient:
    app.state.db_path = tmp_path / "test.db"
    init_db(app.state.db_path)
    return TestClient(app)


def test_health_check(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "evidenceqa-api"}


def test_upload_and_list_documents(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    upload_response = client.post(
        "/documents/upload",
        files={"file": ("security-policy.md", b"# Security policy\nUse MFA.", "text/markdown")},
    )
    list_response = client.get("/documents")

    assert upload_response.status_code == 201
    assert upload_response.json()["title"] == "security-policy"
    assert upload_response.json()["content_length"] == 26
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1


def test_document_metadata_and_deletion(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    document = client.post(
        "/documents/upload",
        files={"file": ("handbook.txt", b"Engineering handbook", "text/plain")},
    ).json()

    get_response = client.get(f"/documents/{document['id']}")
    delete_response = client.delete(f"/documents/{document['id']}")

    assert get_response.status_code == 200
    assert get_response.json()["source_name"] == "handbook.txt"
    assert delete_response.status_code == 204


def test_reject_unsupported_document_type(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    response = client.post(
        "/documents/upload",
        files={"file": ("report.pdf", b"not a real PDF", "application/pdf")},
    )

    assert response.status_code == 415
