from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_page_loads():
    response = client.get("/")
    assert response.status_code == 200
    assert "<form" in response.text


def test_analyze_returns_declared_fields():
    response = client.post(
        "/analyze",
        files={"audio": ("example.wav", b"test", "audio/wav")},
    )
    assert response.status_code == 200
    assert set(response.json()) == {
        "transcript",
        "prosodic_features",
        "as_unit_annotation",
    }
