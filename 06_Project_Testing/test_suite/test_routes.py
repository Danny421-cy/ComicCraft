import os
from fastapi.testclient import TestClient

def test_get_homepage(client: TestClient):
    """TC-01: Verify GET / returns HTML with creation form."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "ComicCraft" in response.text
    assert "Story Premise" in response.text

def test_post_generate_form(client: TestClient):
    """TC-13: Verify POST /generate handles form data and renders preview."""
    form_data = {
        "story_prompt": "A young inventor builds a pocket portal to another dimension.",
        "character_name": "Oliver Twist 2099",
        "setting": "Neo Victorian Workshop",
        "tone": "Sci-Fi / Cyberpunk",
        "art_style": "Classic Comic Book",
        "panel_count": 3
    }
    response = client.post("/generate", data=form_data)
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Oliver Twist 2099" in response.text
    assert "Direct PDF Download" in response.text or "View PDF Export Page" in response.text

def test_post_generate_comic_json(client: TestClient):
    """TC-14: Verify POST /generate-comic/json returns JSON with comic metadata and PDF."""
    payload = {
        "story_prompt": "An AI satellite becomes self-aware and begins writing poetry.",
        "character_name": "Sputnik-9",
        "setting": "Low Earth Orbit",
        "tone": "Humorous / Whimsical",
        "art_style": "Dark Cyberpunk",
        "panel_count": 2
    }
    response = client.post("/generate-comic/json", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "comic_id" in data
    assert len(data["panels"]) == 2
    assert "pdf_path" in data
    assert data["character_name"] == "Sputnik-9"

def test_post_generate_json_invalid(client: TestClient):
    """TC-15: Verify POST /generate-comic/json rejects missing prompt."""
    payload = {
        "character_name": "NoPromptHero"
    }
    response = client.post("/generate-comic/json", json=payload)
    assert response.status_code == 422  # Pydantic validation error

def test_post_test_image_route(client: TestClient):
    """TC-16: Verify POST /test-image endpoint."""
    response = client.post(
        "/test-image",
        data={"prompt": "Samurai warrior battling robotic dragon", "art_style": "Manga / Anime"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["image_url"].startswith("/static/panels/")

def test_export_success_and_download(client: TestClient):
    """TC-17 & TC-19: Verify export-success page and PDF file streaming."""
    # First generate a small comic via JSON
    gen_res = client.post("/generate-comic/json", json={
        "story_prompt": "Quick export test story",
        "character_name": "Flashy",
        "setting": "Lab",
        "tone": "Superhero",
        "art_style": "Classic Comic Book",
        "panel_count": 1
    })
    comic_id = gen_res.json()["comic_id"]
    pdf_filename = f"{comic_id}.pdf"

    # Test export-success page
    success_page = client.get(f"/export-success/{comic_id}")
    assert success_page.status_code == 200
    assert "COMIC PDF EXPORTED SUCCESSFULLY" in success_page.text

    # Test download-pdf route
    download_res = client.get(f"/download-pdf/{pdf_filename}")
    assert download_res.status_code == 200
    assert download_res.headers["content-type"] == "application/pdf"
    assert len(download_res.content) > 1000

def test_export_success_not_found(client: TestClient):
    """TC-18: Verify 404 for invalid comic ID on export page."""
    response = client.get("/export-success/non_existent_comic_id_9999")
    assert response.status_code == 404

def test_configuration_directories():
    """TC-20: Verify static directories existence."""
    from app.config import PANELS_DIR, EXPORTS_DIR, FONTS_DIR
    assert os.path.isdir(PANELS_DIR)
    assert os.path.isdir(EXPORTS_DIR)
    assert os.path.isdir(FONTS_DIR)

def test_download_pdf_not_found(client: TestClient):
    """TC-19B: Verify 404 for downloading nonexistent PDF file."""
    response = client.get("/download-pdf/does_not_exist_999.pdf")
    assert response.status_code == 404

