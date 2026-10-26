
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api.routes import knowledge_base as knowledge_base_routes
from backend.app.db.session import SessionLocal
from backend.app.models.brand import Brand
from backend.app.models.knowledge_base import KnowledgeBaseEntry


def test_create_policy_persists_embedding(monkeypatch):
    fake_embedding = [0.0] * 768
    fake_embedding[0] = 1.0

    monkeypatch.setattr(
        knowledge_base_routes,
        "generate_embedding",
        lambda text, task_type: fake_embedding,
    )

    db = SessionLocal()
    policy_id = None

    try:
        brand = db.query(Brand).filter(Brand.id == 1).first()
        assert brand is not None
        brand_id = brand.id
    finally:
        db.close()

    client = TestClient(app)

    response = client.post(
        "/knowledge-base/",
        json={
            "brand_id": brand_id,
            "title": "Temporary embedding test policy",
            "category": "testing",
            "content": "This temporary policy verifies embedding persistence.",
        },
    )

    assert response.status_code == 201, response.text
    policy_id = response.json()["id"]

    db = SessionLocal()
    try:
        saved_policy = (
            db.query(KnowledgeBaseEntry)
            .filter(KnowledgeBaseEntry.id == policy_id)
            .first()
        )

        assert saved_policy is not None
        assert saved_policy.embedding is not None
        assert len(saved_policy.embedding) == 768
        assert saved_policy.embedding[0] == 1.0
    finally:
        if policy_id is not None:
            db.query(KnowledgeBaseEntry).filter(
                KnowledgeBaseEntry.id == policy_id
            ).delete(synchronize_session=False)
            db.commit()
        db.close()



def test_update_policy_refreshes_embedding(monkeypatch):
    first_embedding = [0.0] * 768
    first_embedding[0] = 1.0

    updated_embedding = [0.0] * 768
    updated_embedding[1] = 1.0

    monkeypatch.setattr(
        knowledge_base_routes,
        "generate_embedding",
        lambda text, task_type: (
            updated_embedding
            if "Updated content" in text
            else first_embedding
        ),
    )

    db = SessionLocal()
    policy_id = None

    try:
        brand = db.query(Brand).filter(Brand.id == 1).first()
        assert brand is not None
        brand_id = brand.id
    finally:
        db.close()

    client = TestClient(app)

    create_response = client.post(
        "/knowledge-base/",
        json={
            "brand_id": brand_id,
            "title": "Temporary update embedding test",
            "category": "testing",
            "content": "This policy tests embedding updates.",
        },
    )

    assert create_response.status_code == 201, create_response.text
    policy_id = create_response.json()["id"]

    try:
        update_response = client.put(
            f"/knowledge-base/{policy_id}",
            json={
                "title": "Temporary update embedding test",
                "category": "testing",
                "content": "Updated content for the embedding test.",
            },
        )

        assert update_response.status_code == 200, update_response.text

        db = SessionLocal()
        try:
            saved_policy = (
                db.query(KnowledgeBaseEntry)
                .filter(KnowledgeBaseEntry.id == policy_id)
                .first()
            )

            assert saved_policy is not None
            assert saved_policy.content == "Updated content for the embedding test."
            assert saved_policy.embedding is not None
            assert len(saved_policy.embedding) == 768
            assert saved_policy.embedding[1] == 1.0
            assert saved_policy.embedding[0] == 0.0
        finally:
            db.close()
    finally:
        db = SessionLocal()
        try:
            db.query(KnowledgeBaseEntry).filter(
                KnowledgeBaseEntry.id == policy_id
            ).delete(synchronize_session=False)
            db.commit()
        finally:
            db.close()
