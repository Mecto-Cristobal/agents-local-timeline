from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import get_db
from app.main import app
from app.models.base import Base


@contextmanager
def build_test_client() -> Iterator[TestClient]:
    # Shared in-memory DB across request sessions.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.pop(get_db, None)
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_post_lifecycle():
    with build_test_client() as client:
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


def test_system_progress_post():
    with build_test_client() as client:
        resp = client.post(
            "/api/agents/system/progress",
            json={
                "status": "OK",
                "job_name": "ops-bias-review",
                "human_text": "Bias incident reviewed and mitigation posted.",
                "result_summary": "Runbook updated",
                "tags_csv": "system,incident",
                "raw_payload": {"source": "test"},
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["job_name"] == "ops-bias-review"
        assert body["human_text"] == "Bias incident reviewed and mitigation posted."


def test_delete_post():
    with build_test_client() as client:
        account = client.post(
            "/api/agents/accounts",
            json={"name": "A", "color": "#111111", "settings_json": {}},
        ).json()

        post_a = client.post(
            "/api/agents/posts",
            json={"account_id": account["id"], "job_name": "Job-A1", "status": "OK"},
        ).json()
        post_b = client.post(
            "/api/agents/posts",
            json={"account_id": account["id"], "job_name": "Job-A2", "status": "OK"},
        ).json()

        delete_resp = client.delete(f"/api/agents/posts/{post_a['id']}")
        assert delete_resp.status_code == 200
        assert delete_resp.json()["post_id"] == post_a["id"]

        posts = client.get(f"/api/agents/posts?account_id={account['id']}").json()
        assert len(posts) == 1
        assert posts[0]["id"] == post_b["id"]


def test_large_human_text_post():
    with build_test_client() as client:
        long_text = "git update note " * 500
        resp = client.post(
            "/api/agents/posts",
            json={"status": "OK", "job_name": "long-note", "human_text": long_text},
        )
        assert resp.status_code == 200
        assert resp.json()["human_text"] == long_text


def test_large_system_progress_human_text():
    with build_test_client() as client:
        long_text = "deploy memo " * 400
        resp = client.post(
            "/api/agents/system/progress",
            json={
                "status": "OK",
                "job_name": "ops-long-note",
                "human_text": long_text,
                "result_summary": "accepted",
                "tags_csv": "system,progress",
            },
        )
        assert resp.status_code == 200
        assert resp.json()["human_text"] == long_text
