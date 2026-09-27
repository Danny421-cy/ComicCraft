# Phase 8: Project Demonstration
## Document 02: Live Demonstration Protocol & Viva Script

---

### 1. Pre-Demo Checklist (T-Minus 5 Minutes)
- [ ] Confirm Python virtual environment is active (`.venv`).
- [ ] Verify server starts cleanly via `run.bat` or `run.ps1`.
- [ ] Verify browser loads `http://127.0.0.1:8000`.
- [ ] Ensure terminal is visible alongside browser for live request logging.

---

### 2. Live Demo Script (Step-by-Step)

#### Demonstration 1: Standard Comic Story Generation (Form Flow)
1. **Show the Homepage**:
   - Open `http://127.0.0.1:8000`.
   - Point out the comic header, brand logo, and real-time API status pills in the top right.
2. **Apply Preset or Enter Custom Narrative**:
   - Click the **`🦸 Cyberpunk Hero`** preset button.
   - Show how the form fields populate with:
     - Story Premise: *Cybernetically enhanced detective defends Neo-Tokyo...*
     - Protagonist: *Cipher Knight*
     - Setting: *Neon Neo-Tokyo, 2099*
     - Tone: *Superhero / Action*
     - Art Style: *Classic Comic Book*
     - Panels: *5 Panels*
3. **Trigger Generation**:
   - Click **`POW! GENERATE FULL COMIC STRIP & PDF`**.
   - Direct examiner attention to the animated modal showing the real-time agent progression:
     1. Gemini Flash structuring outline...
     2. Gemini Pro scripting dialogue...
     3. Diffusion AI rendering illustrations...
     4. Layout engine assembling PDF...
4. **Inspect Generated Comic Preview**:
   - Walk through Panels 1 through 5.
   - Highlight:
     - Narrative caption boxes along top margins.
     - Graphic illustration panels.
     - Character dialogue speech balloons.
     - Dynamic sound effect badges (`POW!`, `WHOOSH!`, `KRAK!`).
     - Expand the "Scene Prompt & Camera Notes" accordion on any panel to demonstrate prompt decomposition.
5. **Demonstrate PDF Export & Download**:
   - Click **`View PDF Export Page ➔`** (or **`Direct PDF Download`**).
   - Display the `export_success.html` confirmation screen.
   - Click **`DOWNLOAD COMIC BOOK (PDF)`**.
   - Open the downloaded PDF in Adobe Reader or browser PDF viewer to display the print-ready vector layout with cover header and issue typography!

---

#### Demonstration 2: Headless REST API Verification
1. Open `http://127.0.0.1:8000/docs` to show the OpenAPI interactive Swagger documentation.
2. Locate `POST /generate-comic/json`.
3. Click "Try it out" and execute a JSON payload.
4. Show the JSON response containing `comic_id`, `panels`, and `pdf_path`.

---

#### Demonstration 3: Diagnostic Image AI Lab
1. Navigate to `http://127.0.0.1:8000/test-image`.
2. Enter prompt: *"Steampunk airship soaring above Victorian clouds, golden sunset"*.
3. Click "Render Test Image" and show instant illustration synthesis.

---

#### Demonstration 4: Fault Tolerance & Resilience Proof
1. Explain to examiners: *"If remote AI credentials are absent or if Google/HF rate limits hit, ComicCraft never crashes."*
2. Demonstrate how the procedural fallback seamlessly handles inputs and renders valid comic art.

