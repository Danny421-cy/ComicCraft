# Phase 5: Project Development — Source Codebase

---

### 1. Module Architecture Overview

This directory contains the complete, production-ready, runnable source code for **ComicCraft**:

```
05_Project_Development/
├── app/
│   ├── __init__.py           # Application package initializer
│   ├── main.py               # FastAPI instance, static mount, CORS, startup events
│   ├── routes.py             # Route definitions: /, /generate, /generate-comic/json, /test-image, /export-success
│   ├── gemini_flash.py       # Macro narrative: 5-panel outline via Gemini 1.5 Flash
│   ├── gemini_pro.py         # Micro narrative: dialogue & narration script via Gemini 1.5 Pro
│   ├── image_generator.py    # Diffusion visual synthesis via Hugging Face API + procedural canvas fallback
│   ├── layout_builder.py     # Aggregates panels, images, text, and metadata into ComicLayout
│   ├── exporters.py          # Vector PDF desktop publishing via FPDF2
│   ├── config.py             # Environment configurations, directory management, key checks
│   └── models.py             # Pydantic v2 schemas and validation models
├── templates/
│   ├── base.html             # Master Jinja2 template with comic header & status pills
│   ├── index.html            # User input form with presets & animated progress overlay
│   ├── comic_preview.html    # Interactive comic reader with speech bubbles & panels
│   ├── export_success.html   # PDF export confirmation & direct download
│   └── test_image.html       # Diagnostic lab for testing image generation prompts
├── static/
│   ├── css/style.css         # Authentic graphic novel responsive stylesheet
│   ├── js/main.js            # Client-side form handlers & progress state ticker
│   ├── panels/               # Generated PNG panel image storage
│   ├── exports/              # Generated PDF comic book storage
│   └── fonts/                # PDF typography directory
├── requirements.txt          # Python dependencies
├── .env.example              # Environment configuration template
└── .env                      # Active environment configuration
```

---

### 2. Quick CLI Run (Within Phase 5)

Activate your virtual environment and run Uvicorn:

```bash
# From d:\coding\ComicCraft\05_Project_Development
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

