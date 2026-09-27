# Phase 3: Project Design
## Document 01: System Architecture & C4 Model

---

### 1. High-Level Architectural Vision

ComicCraft adopts a modular, service-oriented monolithic architecture built atop **FastAPI**. It decouples the narrative generation intelligence (Google Gemini LLMs), visual diffusion engines (Hugging Face / Fallback Canvas), layout positioning logic, and the PDF publication compiler into distinct, testable layers.

```mermaid
graph TB
    subgraph Client Tier
        Browser[Modern Web Browser]
        ThirdParty[External REST API Client]
    end

    subgraph Presentation Tier
        Templates[Jinja2 Template Engine]
        StaticAssets[Static CSS / JS / Fonts]
    end

    subgraph Application Tier [FastAPI Gateway - app.main]
        Router[Router & Request Validator: routes.py]
        Config[Environment & Credentials: config.py]
    end

    subgraph Service Tier
        FlashService[Gemini Flash Service: gemini_flash.py]
        ProService[Gemini Pro Service: gemini_pro.py]
        ImageEngine[Diffusion Image Engine: image_generator.py]
        LayoutBuilder[Layout Assembly Engine: layout_builder.py]
        Exporter[FPDF2 Vector Exporter: exporters.py]
    end

    subgraph Persistence & File Storage
        PanelsDir[(static/panels/)]
        ExportsDir[(static/exports/)]
        FontsDir[(static/fonts/)]
    end

    Browser -->|HTTP GET/POST| Router
    ThirdParty -->|JSON REST| Router
    Router --> Templates
    Templates --> StaticAssets
    Router --> FlashService
    Router --> ProService
    Router --> ImageEngine
    Router --> LayoutBuilder
    Router --> Exporter

    ImageEngine --> PanelsDir
    Exporter --> ExportsDir
    Exporter --> FontsDir
```

---

### 2. C4 Model Specifications

#### 2.1 Level 1: System Context Diagram

```mermaid
C4Context
    title System Context diagram for ComicCraft

    Person(user, "Comic Creator", "User submitting story ideas to generate visual comics.")
    Person(admin, "Developer / Evaluator", "Evaluates system performance, tests models, runs test suites.")

    System(comiccraft, "ComicCraft Platform", "Generates panel outlines, dialogue, AI images, and publishes PDF comics.")

    System_Ext(gemini, "Google Gemini API", "Provides 1.5 Flash for outlines and 1.5 Pro for dialogue.")
    System_Ext(hf, "Hugging Face Inference API", "Runs Diffusion models (Stable Diffusion v1.5 / SDXL) for imagery.")

    Rel(user, comiccraft, "Inputs story premise, previews comic, downloads PDF", "HTTPS")
    Rel(admin, comiccraft, "Runs diagnostics and automated tests", "Local CLI / REST")
    Rel(comiccraft, gemini, "Generates structured narrative and script", "JSON over HTTPS")
    Rel(comiccraft, hf, "Sends visual prompts to generate panel images", "REST over HTTPS")
```

#### 2.2 Level 2: Container Diagram

```mermaid
C4Container
    title Container diagram for ComicCraft

    Container(web_app, "Web Application", "Python, FastAPI, Jinja2", "Delivers HTML views and handles form / REST requests.")
    Container(layout_eng, "Layout Builder", "Python, Pydantic", "Pairs panel metadata, text, and image assets into consistent schema.")
    Container(pdf_comp, "PDF Compiler", "FPDF2", "Renders vector PDF document with typography and multi-panel grids.")
    ContainerDb(file_store, "File System Storage", "Local Disk Directory", "Stores generated PNG panels and compiled PDF artifacts.")

    Rel(web_app, layout_eng, "Passes narrative and image outputs")
    Rel(layout_eng, pdf_comp, "Passes layout payload")
    Rel(pdf_comp, file_store, "Writes PDF")
```

#### 2.3 Level 3: Component Diagram (Backend Modules)

| Component Name | Module File | Core Responsibility | Key Inbound / Outbound Types |
| :--- | :--- | :--- | :--- |
| `FastAPI App` | `app/main.py` | App lifecycle, static mount, router registration | HTTP Request / Response |
| `Route Handlers` | `app/routes.py` | `/`, `/generate`, `/generate-comic/json`, `/test-image` | Form Data, JSON payloads |
| `Gemini Flash Client`| `app/gemini_flash.py`| Prompts Gemini Flash to construct 5-panel narrative arc | `ComicStoryRequest` $\to$ `List[PanelOutline]` |
| `Gemini Pro Client` | `app/gemini_pro.py` | Expands outline into character dialogue & captions | `List[PanelOutline]` $\to$ `List[EnrichedPanel]` |
| `Image Generator` | `app/image_generator.py`| Queries HF API or procedural fallback for PNGs | `EnrichedPanel` $\to$ PNG file path |
| `Layout Builder` | `app/layout_builder.py`| Merges story text, dialogue, onomatopoeia & image paths | Enriched panels $\to$ `ComicLayout` |
| `PDF Exporter` | `app/exporters.py` | Arranges comic panels onto A4 PDF grid via FPDF2 | `ComicLayout` $\to$ PDF file path |
| `Settings & Config` | `app/config.py` | Reads `.env`, validates keys, sets defaults | Environment variables |

---

### 3. Deployment Architecture

```mermaid
graph LR
    subgraph Host Machine [Windows / Linux / macOS Environment]
        Venv[Python 3.11 Virtual Environment: .venv]
        Uvicorn[Uvicorn ASGI Server: Port 8000]
        FastAPIInstance[FastAPI Application Instance]
        FileSystem[Local File System]
    end

    subgraph Cloud AI Providers
        GoogleAI[Google AI Studio: Gemini API]
        HuggingFaceCloud[Hugging Face Hub: Inference Endpoints]
    end

    Venv --> Uvicorn
    Uvicorn --> FastAPIInstance
    FastAPIInstance --> FileSystem
    FastAPIInstance --> GoogleAI
    FastAPIInstance --> HuggingFaceCloud
```

