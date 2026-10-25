from fastapi.testclient import TestClient

from app.main import app


def test_home_serves_html_with_upload_form() -> None:
    response = TestClient(app).get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert '<form id="upload-form">' in response.text
