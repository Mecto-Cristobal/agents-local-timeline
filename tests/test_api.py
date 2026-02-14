from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import get_db
from app.main import app
from app.models.base import Base


def test_post_lifecycle():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    account_resp = client.post(
        "/api/agents/accounts",
        json={"name": "Alpha", "color": "#111111", "settings_json": {}},
    )
    assert account_resp.status_code == 200
    account_id = account_resp.json()["id"]

    get_resp = client.get(f"/api/agents/accounts/{account_id}")
    assert get_resp.status_code == 200

    post_resp = client.post(
        "/api/agents/posts",
        json={"account_id": account_id, "job_name": "Job", "status": "OK"},
    )
    assert post_resp.status_code == 200
    post_id = post_resp.json()["id"]

    patch_resp = client.patch(
        f"/api/agents/posts/{post_id}", json={"status": "WARN"}
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "WARN"

    delete_resp = client.delete(f"/api/agents/accounts/{account_id}")
    assert delete_resp.status_code == 200

    list_resp = client.get("/api/agents/posts")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1
    assert list_resp.json()[0]["account_id"] is None
