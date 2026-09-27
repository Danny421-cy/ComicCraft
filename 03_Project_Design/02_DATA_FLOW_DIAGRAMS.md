# Phase 3: Project Design
## Document 02: Data Flow Diagrams (DFD Levels 0, 1, 2)

---

### 1. DFD Level 0: Context Level Diagram

```mermaid
flowchart TD
    User([End User / Storyteller])
    System((0.0<br/>ComicCraft System))
    ExternalGemini[[Google Gemini API]]
    ExternalHF[[Hugging Face Diffusion API]]
    DiskStorage[(Local File Storage)]

    User -->|1. Story Premise & Parameters| System
    System -->|2. Narrative Outline & Script Prompt| ExternalGemini
    ExternalGemini -->|3. Structured Outlines & Dialogue| System
    System -->|4. Visual Image Prompts| ExternalHF
    ExternalHF -->|5. Raw Image Bytes| System
    System -->|6. Persist Panels & PDF| DiskStorage
    System -->|7. Interactive Comic Preview & PDF Download| User
```

---

### 2. DFD Level 1: System Decomposition

```mermaid
flowchart TD
    User([End User]) -->|Form / JSON Data| P1[1.0 Input Validation & Request Normalization]
    P1 -->|Validated ComicStoryRequest| P2[2.0 Macro Outline Generation - Gemini Flash]
    P2 -->|Structured Panel Outlines| P3[3.0 Script & Dialogue Expansion - Gemini Pro]
    P3 -->|Enriched Panel Data| P4[4.0 Panel Illustration Diffusion Engine]
    P4 -->|Generated Image Paths| P5[5.0 Comic Layout Assembly Engine]
    P3 -->|Story Text & Dialogue| P5
    P5 -->|Complete ComicLayout Object| P6[6.0 Vector PDF Document Exporter]
    P6 -->|Binary PDF Stream| D1[(static/exports/)]
    P4 -->|PNG Panel Files| D2[(static/panels/)]
    P5 -->|Render Data| P7[7.0 HTML Preview Generator]
    P7 -->|Interactive Comic Webpage| User
```

---

### 3. DFD Level 2: Detailed Generation Subsystem (Processes 2.0 to 5.0)

```mermaid
sequenceDiagram
    autonumber
    actor User as User Browser
    participant Router as routes.py
    participant Flash as gemini_flash.py
    participant Pro as gemini_pro.py
    participant Diff as image_generator.py
    participant Layout as layout_builder.py
    participant Exporter as exporters.py

    User->>Router: POST /generate (title, prompt, character, tone, style)
    Router->>Flash: generate_outline(prompt, character, setting, tone, style, panels)
    Note over Flash: Prompts Gemini 1.5 Flash (or mock fallback)
    Flash-->>Router: List of 5 PanelOutlines (title, scene, visual_prompt)
    
    Router->>Pro: expand_dialogue(panels, character, tone)
    Note over Pro: Prompts Gemini 1.5 Pro (or mock fallback)
    Pro-->>Router: List of 5 EnrichedPanels (narration, dialogue, sound_effect)
    
    Router->>Diff: generate_panel_images(enriched_panels, style)
    loop For each panel 1 to 5
        Diff->>Diff: Query HF API (or synthesize stylized fallback canvas)
        Diff->>Diff: Save image to static/panels/comic_{id}_p{i}.png
    end
    Diff-->>Router: List of local image URLs
    
    Router->>Layout: build_comic_layout(story_meta, enriched_panels, image_paths)
    Layout-->>Router: ComicLayout schema
    
    Router->>Exporter: export_to_pdf(comic_layout)
    Exporter-->>Router: pdf_filename & download_url
    
    Router-->>User: Render comic_preview.html with live panels & export links
```

