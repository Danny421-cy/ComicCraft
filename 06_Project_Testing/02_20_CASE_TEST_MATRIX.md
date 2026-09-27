# Phase 6: Project Testing
## Document 02: 20-Case Test Verification Matrix

---

### 1. Master Test Case Matrix

| TC ID | Module Tested | Test Category | Scenario / Objective | Input Data / Precondition | Expected Output | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-01** | `routes.py` | UI / Integration | GET Homepage (`/`) | HTTP GET request to `/` | HTTP 200 OK; renders form fields & title | **PASS** |
| **TC-02** | `models.py` | Unit / Validation | Valid `ComicStoryRequest` validation | Valid JSON with all 6 fields | Pydantic model instantiates without error | **PASS** |
| **TC-03** | `models.py` | Unit / Validation | Invalid panel count out of bounds | `panel_count: 25` (>10) | Pydantic ValidationError raised | **PASS** |
| **TC-04** | `gemini_flash.py`| Unit / Generation | Generate 5-panel outline (standard) | Request with 5 panels requested | Returns exactly 5 `PanelOutline` objects | **PASS** |
| **TC-05** | `gemini_flash.py`| Fault-Tolerance | Outline generation with missing API key | `GEMINI_API_KEY=""` | Seamless procedural fallback returns 5 outlines | **PASS** |
| **TC-06** | `gemini_pro.py` | Unit / Generation | Expand script into narration & dialogue | 5 `PanelOutline` inputs | Returns 5 `EnrichedPanel` with dialogue & SFX | **PASS** |
| **TC-07** | `gemini_pro.py` | Fault-Tolerance | Script expansion with missing API key | `GEMINI_API_KEY=""` | Procedural enrichment fills captions & speech | **PASS** |
| **TC-08** | `image_generator.py`| Unit / Synthesis | Procedural comic panel image generation | Prompt: "Hero leaps", Style: "Classic" | Generates valid 600x600 PNG in `static/panels/` | **PASS** |
| **TC-09** | `image_generator.py`| Unit / Styling | Distinct art style theme verification | Style: "Dark Cyberpunk" | Generates PNG with cyberpunk neon palette | **PASS** |
| **TC-10** | `layout_builder.py`| Unit / Assembly | Assemble layout with unique comic ID | Enriched panels & story request | Returns `ComicLayout` with UUID & timestamp | **PASS** |
| **TC-11** | `exporters.py` | Unit / PDF | Vector PDF compilation via FPDF2 | Complete `ComicLayout` | Writes valid `.pdf` to `static/exports/` | **PASS** |
| **TC-12** | `exporters.py` | Robustness | Special unicode punctuation sanitization | Text with curled quotes `“hello”` & em-dash `—`| Successfully sanitized without latin-1 crash | **PASS** |
| **TC-13** | `routes.py` | Integration / Form | Complete Form POST `/generate` | Valid form data submitted | HTTP 200; renders `comic_preview.html` | **PASS** |
| **TC-14** | `routes.py` | Integration / REST | Headless JSON POST `/generate-comic/json` | Valid JSON payload | HTTP 200; returns JSON with comic_id & pdf_path | **PASS** |
| **TC-15** | `routes.py` | Validation / REST | Empty story prompt rejection | `story_prompt: ""` | HTTP 422 Unprocessable Entity | **PASS** |
| **TC-16** | `routes.py` | Integration / Diag | POST `/test-image` diagnostic endpoint | `prompt: "Space warrior"` | HTTP 200; returns `image_url` and mode | **PASS** |
| **TC-17** | `routes.py` | Integration / Export | GET `/export-success/{comic_id}` | Valid generated `comic_id` | HTTP 200; renders `export_success.html` | **PASS** |
| **TC-18** | `routes.py` | Error Handling | GET `/export-success/{invalid_id}` | Non-existent ID `comic_xyz999` | HTTP 404 Not Found error | **PASS** |
| **TC-19** | `routes.py` | Streaming / PDF | GET `/download-pdf/{filename}` | Valid existing PDF file | HTTP 200; streams with `application/pdf` | **PASS** |
| **TC-20** | `config.py` | Environment | Environment variable & directory validation | Startup directory check | All directories (`panels`, `exports`, `fonts`) exist | **PASS** |

---

### 2. Matrix Verification Summary
- Total Cases: **20**
- Passed: **20**
- Failed: **0**
- Verification Rate: **100.0%**

