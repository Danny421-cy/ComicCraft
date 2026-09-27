# Phase 4: Project Planning
## Document 03: Risk Management & Mitigation Framework

---

### 1. Risk Matrix (Probability vs. Consequence)

```mermaid
quadrantChart
    title Risk Priority Classification Matrix
    x-axis Low Probability --> High Probability
    y-axis Low Consequence --> High Consequence
    quadrant-1 Immediate Mitigation & Contingency
    quadrant-2 Active Monitoring
    quadrant-3 Low Concern
    quadrant-4 Precautionary Standards
    "Remote AI Rate Limits (429)": [0.82, 0.88]
    "Hugging Face Cold Starts": [0.75, 0.65]
    "Model Output Schema Drift": [0.45, 0.70]
    "Missing User API Keys": [0.90, 0.85]
    "PDF Font Unicode Encoding": [0.35, 0.50]
    "Local VRAM Insufficiency": [0.60, 0.30]
```

---

### 2. Comprehensive Risk Registry & Mitigation Strategies

| Risk ID | Risk Description | Prob. | Impact | Severity | Mitigation & Contingency Strategy |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **RSK-01** | **Third-party API rate limits (Google AI / Hugging Face 429)** | High | High | Critical | **Mitigation**: Implement exponential backoff retry logic. **Contingency**: Autonomous fallback to deterministic procedural narrative synthesis and styled local fallback panel generation. |
| **RSK-02** | **First-time user runs app without API keys configured** | High | High | Critical | **Mitigation**: Detect missing `.env` keys gracefully. Render helpful banner in UI explaining where to get keys. Run in intelligent offline preview mode instead of crashing. |
| **RSK-03** | **LLM JSON Schema Drift (hallucinated formatting)** | Medium | High | High | **Mitigation**: Enforce strict system instructions and Pydantic validation with regex repair routines on markdown code blocks (`json ... `). |
| **RSK-04** | **HF Inference API latency / cold-starts (>30s)** | High | Med | High | **Mitigation**: Configure 20s timeout per panel with immediate failover to procedural canvas synthesizer. |
| **RSK-05** | **FPDF character encoding errors on special characters** | Low | Med | Medium | **Mitigation**: Clean unicode strings (transliterate curved quotes, em-dashes, and accented characters to standard ASCII/Latin-1 compatible strings) prior to cell insertion. |
| **RSK-06** | **Large panel images exhausting server memory** | Low | Low | Low | **Mitigation**: Pillow automatically normalizes image sizes to 512x512 with 85% JPEG/PNG compression before storage. |

