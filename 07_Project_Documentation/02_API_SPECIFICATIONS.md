# Phase 7: Project Documentation
## Document 02: REST API Specifications (OpenAPI 3.1)

---

### 1. API Architecture Overview

ComicCraft exposes both a dynamic HTML frontend and a headless REST API. Interactive Swagger UI is available at `/docs` and ReDoc at `/redoc`.

- **Base URL**: `http://127.0.0.1:8000`
- **Protocol**: HTTP/1.1
- **Content Types**: `application/json`, `application/x-www-form-urlencoded`, `multipart/form-data`, `application/pdf`

---

### 2. Endpoints Catalog

```mermaid
graph LR
    API[ComicCraft API Gateway]
    API --> E1[GET / : Homepage HTML]
    API --> E2[POST /generate : Form Comic Generation]
    API --> E3[POST /generate-comic/json : Headless REST Comic Generation]
    API --> E4[POST /test-image : Image AI Diagnostic]
    API --> E5[GET /export-success/{comic_id} : Export Dashboard]
    API --> E6[GET /download-pdf/{filename} : Binary PDF Stream]
```

---

### 3. Detailed Endpoint Specifications

#### 3.1 `POST /generate-comic/json`
Accepts a structured JSON narrative payload and executes the end-to-end comic generation pipeline.

- **Request Headers**:
  - `Content-Type: application/json`
- **Request Body**:
```json
{
  "story_prompt": "A time traveler accidentally drops a modern smartphone in ancient Rome.",
  "character_name": "Dr. Clara Oswald",
  "setting": "Roman Forum, 80 AD",
  "tone": "Humorous Sci-Fi",
  "art_style": "Classic Comic Book",
  "panel_count": 5
}
```

- **Response Body (HTTP 200 OK)**:
```json
{
  "status": "success",
  "comic_id": "comic_9a7f31c2",
  "title": "A Phone in the Forum",
  "character_name": "Dr. Clara Oswald",
  "setting": "Roman Forum, 80 AD",
  "tone": "Humorous Sci-Fi",
  "art_style": "Classic Comic Book",
  "panels": [
    {
      "panel_number": 1,
      "title": "A Slip Through Time",
      "scene_description": "Dr. Clara stumbling through a golden portal onto Roman paving stones.",
      "visual_prompt": "Classic Comic Book style, wide shot, female time traveler in steampunk coat...",
      "narration": "Rome, 80 AD. The glory of the empire... and temporal disaster.",
      "dialogue": "Dr. Clara: 'Hold on tight, the landing is always the roughest—'",
      "sound_effect": "WHOOSH!",
      "image_url": "/static/panels/comic_9a7f31c2_panel_1.png"
    }
  ],
  "pdf_path": "/static/exports/comic_9a7f31c2.pdf",
  "download_url": "/download-pdf/comic_9a7f31c2.pdf",
  "created_at": "2026-09-26 16:30:00 UTC"
}
```

- **Error Codes**:
  - `422 Unprocessable Entity`: Input schema validation failure (e.g. missing `story_prompt`).
  - `500 Internal Server Error`: Internal generation pipeline exception.

---

#### 3.2 `POST /test-image`
Diagnostic endpoint for testing image diffusion prompts directly.

- **Request Body (JSON or Form)**:
```json
{
  "prompt": "Cyberpunk hovercar cruising over neon skyscrapers",
  "art_style": "Dark Cyberpunk"
}
```

- **Response (HTTP 200 OK)**:
```json
{
  "status": "success",
  "image_url": "/static/panels/test_4a91b2.png",
  "local_path": "D:\\coding\\ComicCraft\\05_Project_Development\\static\\panels\\test_4a91b2.png",
  "prompt_used": "Cyberpunk hovercar cruising over neon skyscrapers",
  "generation_mode": "Hugging Face Diffusion"
}
```

---

#### 3.3 `GET /download-pdf/{filename}`
Streams the compiled vector comic PDF document.

- **Path Parameter**: `filename` (e.g. `comic_9a7f31c2.pdf`)
- **Response Headers**:
  - `Content-Type: application/pdf`
  - `Content-Disposition: attachment; filename="comic_9a7f31c2.pdf"`
- **Response (HTTP 200 OK)**: Binary PDF file stream.
- **Response (HTTP 404 Not Found)**: If the requested PDF does not exist on disk.

