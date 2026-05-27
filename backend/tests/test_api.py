import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["ENVIRONMENT"] = "test"

from fastapi.testclient import TestClient

from app.db.session import Base, SessionLocal, engine
from app.main import app
from app.services.seed import seed_database


def _client() -> TestClient:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    return TestClient(app)


def _auth_headers(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@inventory-nexus.example.com", "password": "ChangeMe123!"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health() -> None:
    client = _client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_dashboard_and_products_are_seeded() -> None:
    client = _client()
    headers = _auth_headers(client)
    dashboard = client.get("/api/v1/analytics/dashboard", headers=headers)
    products = client.get("/api/v1/inventory/products", headers=headers)
    assert dashboard.status_code == 200
    assert products.status_code == 200
    assert dashboard.json()["total_skus"] == 5
    assert len(products.json()) == 5


def test_reorder_recommendations_include_low_stock() -> None:
    client = _client()
    headers = _auth_headers(client)
    response = client.get("/api/v1/analytics/reorder-recommendations", headers=headers)
    assert response.status_code == 200
    assert any(item["urgency"] in {"critical", "watch"} for item in response.json())
