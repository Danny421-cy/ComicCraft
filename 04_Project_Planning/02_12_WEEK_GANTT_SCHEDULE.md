# Phase 4: Project Planning
## Document 02: 12-Week Gantt Schedule & Milestones

---

### 1. 12-Week Implementation Timeline

The project follows a 12-week Agile schedule partitioned into 6 two-week sprints.

```mermaid
gantt
    title ComicCraft 12-Week Development Schedule
    dateFormat  YYYY-MM-DD
    section Phase 1 & 2: Inception & SRS
    Problem Statement & Feasibility   :done, s1, 2026-07-06, 7d
    SRS (IEEE 830) & Agile Stories    :done, s2, after s1, 7d
    section Phase 3: Architecture & Design
    C4 Architecture & DFDs            :done, s3, 2026-07-20, 7d
    Data Contracts & UI/UX System     :done, s4, after s3, 7d
    section Phase 4: Project Planning
    WBS, Gantt, Risk & Cost Models    :done, s5, 2026-08-03, 7d
    section Phase 5: Core Development
    FastAPI Core & Router Gateway     :active, s6, 2026-08-10, 7d
    Gemini Flash & Pro Integrations   :active, s7, after s6, 10d
    Diffusion & Resilient Fallback    :active, s8, after s6, 10d
    Layout Assembly & FPDF2 Exporter  :active, s9, after s7, 7d
    Jinja2 UI & Interactive Frontend  :active, s10, after s8, 7d
    section Phase 6: QA & Testing
    Unit & Integration Test Suite     :s11, 2026-09-07, 7d
    20-Case Test Matrix Execution     :s12, after s11, 7d
    section Phase 7 & 8: Documentation & Viva
    Final Academic Report & API Docs  :s13, 2026-09-14, 7d
    Viva Presentation & Demo Package  :s14, after s13, 7d
```

---

### 2. Major Project Milestones

| Milestone | Target Week | Deliverable / Success Criteria | Verification Mode |
| :--- | :--- | :--- | :--- |
| **M1: Baseline Approval** | Week 2 | Approved SRS & Project Charter | Peer review signoff |
| **M2: Architecture Lock** | Week 4 | Approved C4 diagrams, DFDs, Pydantic schemas | Architecture review |
| **M3: Narrative Engine Alpha** | Week 7 | Dual-LLM generating coherent 5-panel scripts | CLI integration test |
| **M4: Visual Pipeline Beta** | Week 9 | Diffusion & fallback canvas rendering panels | Isolated image test |
| **M5: Full System Integration**| Week 10| Web UI end-to-end comic generation & PDF download| End-to-end manual pass |
| **M6: QA Verification** | Week 11| 20/20 test cases passing in automated suite | Pytest automated run |
| **M7: Viva Defense Ready** | Week 12| Final academic report, slide deck & live demo | Committee presentation |

---

### 3. Critical Path Analysis (CPM)
1. **Critical Path**: `SRS` $\to$ `C4 Design` $\to$ `FastAPI Core` $\to$ `Gemini Flash/Pro` $\to$ `Diffusion Engine` $\to$ `Layout Builder` $\to$ `FPDF2 Exporter` $\to$ `Integration Testing` $\to$ `Academic Report`.
2. **Slack Activities**: UI Halftone styling, Presets library generation, and Diagnostic `/test-image` route have positive float (slack of 3 to 5 days).

