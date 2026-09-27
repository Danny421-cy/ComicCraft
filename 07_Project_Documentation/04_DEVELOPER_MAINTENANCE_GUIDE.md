# Phase 7: Project Documentation
## Document 04: Developer & Maintenance Architecture Guide

---

### 1. Developer Onboarding & Architecture Principles

ComicCraft follows clean, decoupled modular design:
- `app.config`: Centralized configuration.
- `app.models`: Pydantic data contracts enforcing internal interfaces.
- `app.gemini_flash`: Macro narrative pacing.
- `app.gemini_pro`: Micro dialogue & scripting.
- `app.image_generator`: Image diffusion & procedural fallback.
- `app.layout_builder`: Layout aggregation.
- `app.exporters`: FPDF2 PDF rendering.
- `app.routes`: FastAPI route handlers.

---

### 2. Extending the System

#### 2.1 Swapping the Image Diffusion Model
To change the Hugging Face model (e.g. to SDXL Turbo or Flux):
1. Open `.env`
2. Update `HF_MODEL_ID`:
```env
HF_MODEL_ID=stabilityai/sdxl-turbo
```
3. Or modify `image_generator.py` to target specialized endpoints.

#### 2.2 Adding Custom Comic Art Styles
In `app/image_generator.py`, add a new color palette to `STYLE_THEMES`:
```python
"Retro Sci-Fi 1950s": {
    "bg_top": (255, 140, 0),
    "bg_bottom": (0, 70, 140),
    "accent": (255, 255, 0),
    "burst": (255, 255, 255),
    "text": (20, 20, 20)
}
```
And add the option in `templates/index.html`.

#### 2.3 Customizing PDF Page Geometry
In `app/exporters.py`, customize `ComicPDF` margins, font sizes, or cell rectangles to change panel dimensions, paper sizes (Letter vs A4), or multi-column grids.

---

### 3. Cloud Deployment (Render.com)

ComicCraft is cloud-ready and includes native Render configuration files (`render.yaml`, `.python-version`, `main.py`).

#### 3.1 Quick Render Deployment Settings
- **Service Type**: Web Service
- **Environment**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables**:
  - `GEMINI_API_KEY`: *(Your Google AI Studio API key)*
  - `GEMINI_FLASH_MODEL`: `gemini-flash-lite-latest`
  - `GEMINI_PRO_MODEL`: `gemini-flash-lite-latest`
  - `HF_API_KEY`: *(Optional Hugging Face token)*

---

### 4. Production Deployment with Docker (Optional)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```


