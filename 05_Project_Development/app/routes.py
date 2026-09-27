import os
import time
import uuid
import logging
from typing import Optional, Dict
from fastapi import APIRouter, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.config import (
    TEMPLATES_DIR,
    EXPORTS_DIR,
    has_gemini_key,
    has_hf_key
)
from app.models import (
    ComicStoryRequest,
    ComicLayout
)
from app.gemini_flash import generate_panel_outline
from app.gemini_pro import expand_narration_and_dialogue
from app.image_generator import generate_panel_image, test_image_generation
from app.layout_builder import assemble_comic_layout
from app.exporters import export_comic_to_pdf

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# In-memory store for generated comic layouts during the application session
COMIC_STORE: Dict[str, ComicLayout] = {}


@router.get("/", response_class=HTMLResponse)
async def index_page(request: Request):
    """Renders the primary comic creation input form."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "has_gemini": has_gemini_key(),
            "has_hf": has_hf_key()
        }
    )


@router.post("/generate", response_class=HTMLResponse)
async def generate_comic_form(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form("Max Blaze"),
    setting: str = Form("Neo Metropolis"),
    tone: str = Form("Superhero / Action"),
    art_style: str = Form("Classic Comic Book"),
    panel_count: int = Form(5)
):
    """
    Handles form submission from index.html:
    1. Validates inputs
    2. Runs Gemini Flash -> Outlines
    3. Runs Gemini Pro -> Dialogue & Narration
    4. Generates illustrations for each panel
    5. Assembles layout and pre-compiles PDF
    6. Renders comic_preview.html
    """
    story_req = ComicStoryRequest(
        story_prompt=story_prompt.strip(),
        character_name=character_name.strip() or "Hero",
        setting=setting.strip() or "Metropolis",
        tone=tone.strip() or "Action",
        art_style=art_style.strip() or "Classic Comic Book",
        panel_count=max(1, min(10, panel_count))
    )

    try:
        # Step 1: Panel Outline (Gemini Flash)
        outlines = generate_panel_outline(story_req)

        # Step 2: Narration and Dialogue Expansion (Gemini Pro)
        enriched_panels = expand_narration_and_dialogue(
            outlines=outlines,
            character_name=story_req.character_name,
            setting=story_req.setting,
            tone=story_req.tone
        )

        # Step 3: Panel Illustration Diffusion
        comic_uid = uuid.uuid4().hex[:8]
        for p in enriched_panels:
            filename = f"comic_{comic_uid}_panel_{p.panel_number}.png"
            web_url, local_path = generate_panel_image(
                prompt=p.visual_prompt,
                art_style=story_req.art_style,
                filename=filename,
                panel_number=p.panel_number,
                title=p.title,
                sound_effect=p.sound_effect,
                narration=p.narration,
                dialogue=p.dialogue,
                character_name=story_req.character_name,
                setting=story_req.setting
            )
            p.image_url = web_url
            p.local_image_path = local_path
            time.sleep(0.4)

        # Step 4: Assemble Layout
        layout = assemble_comic_layout(story_req, enriched_panels, comic_id=f"comic_{comic_uid}")

        # Step 5: Pre-compile PDF
        pdf_web_url, pdf_local_path = export_comic_to_pdf(layout)
        layout.pdf_path = pdf_web_url
        layout.download_url = f"/download-pdf/{os.path.basename(pdf_local_path)}"

        # Save to session store
        COMIC_STORE[layout.comic_id] = layout

        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "comic": layout,
                "has_gemini": has_gemini_key(),
                "has_hf": has_hf_key()
            }
        )
    except Exception as e:
        logger.error(f"Error generating comic: {e}", exc_info=True)
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error_message": f"Generation encountered an issue: {str(e)}",
                "has_gemini": has_gemini_key(),
                "has_hf": has_hf_key()
            },
            status_code=500
        )


@router.post("/generate-comic/json", response_class=JSONResponse)
async def generate_comic_json(payload: ComicStoryRequest):
    """
    Headless API endpoint: Accepts JSON input and returns structured
    comic layout data along with the generated PDF path.
    """
    try:
        outlines = generate_panel_outline(payload)
        enriched_panels = expand_narration_and_dialogue(
            outlines=outlines,
            character_name=payload.character_name,
            setting=payload.setting,
            tone=payload.tone
        )

        comic_uid = uuid.uuid4().hex[:8]
        for p in enriched_panels:
            filename = f"comic_{comic_uid}_panel_{p.panel_number}.png"
            web_url, local_path = generate_panel_image(
                prompt=p.visual_prompt,
                art_style=payload.art_style,
                filename=filename,
                panel_number=p.panel_number,
                title=p.title,
                sound_effect=p.sound_effect
            )
            p.image_url = web_url
            p.local_image_path = local_path

        layout = assemble_comic_layout(payload, enriched_panels, comic_id=f"comic_{comic_uid}")
        pdf_web_url, pdf_local_path = export_comic_to_pdf(layout)
        layout.pdf_path = pdf_web_url
        layout.download_url = f"/download-pdf/{os.path.basename(pdf_local_path)}"

        COMIC_STORE[layout.comic_id] = layout

        return {
            "status": "success",
            "comic_id": layout.comic_id,
            "title": layout.title,
            "character_name": layout.character_name,
            "setting": layout.setting,
            "tone": layout.tone,
            "art_style": layout.art_style,
            "panels": [p.model_dump() for p in layout.panels],
            "pdf_path": layout.pdf_path,
            "download_url": layout.download_url,
            "created_at": layout.created_at
        }
    except Exception as e:
        logger.error(f"JSON comic generation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Comic synthesis failed: {str(e)}"
        )


@router.get("/export-success/{comic_id}", response_class=HTMLResponse)
async def export_success_page(request: Request, comic_id: str):
    """Displays confirmation that the PDF has been compiled and is ready to download."""
    comic = COMIC_STORE.get(comic_id)
    if not comic:
        # Fallback check on disk
        pdf_path = EXPORTS_DIR / f"{comic_id}.pdf"
        if pdf_path.exists():
            return templates.TemplateResponse(
                request=request,
                name="export_success.html",
                context={
                    "comic_id": comic_id,
                    "title": "Your Comic Book",
                    "download_url": f"/download-pdf/{comic_id}.pdf",
                    "file_size": f"{pdf_path.stat().st_size // 1024} KB"
                }
            )
        raise HTTPException(status_code=404, detail="Comic export not found.")

    pdf_path = EXPORTS_DIR / f"{comic_id}.pdf"
    file_size_kb = f"{pdf_path.stat().st_size // 1024} KB" if pdf_path.exists() else "Ready"

    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "comic_id": comic.comic_id,
            "title": comic.title,
            "comic": comic,
            "download_url": comic.download_url or f"/download-pdf/{comic.comic_id}.pdf",
            "file_size": file_size_kb
        }
    )


@router.get("/download-pdf/{filename}")
async def download_pdf_file(filename: str):
    """Safely streams the exported PDF file for user download."""
    safe_filename = os.path.basename(filename)
    file_path = EXPORTS_DIR / safe_filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Exported PDF not found.")

    return FileResponse(
        path=str(file_path),
        filename=safe_filename,
        media_type="application/pdf"
    )


@router.get("/test-image", response_class=HTMLResponse)
async def test_image_page(request: Request):
    """Interactive testing interface for image generation."""
    return templates.TemplateResponse(
        request=request,
        name="test_image.html",
        context={
            "has_hf": has_hf_key()
        }
    )


@router.post("/test-image", response_class=JSONResponse)
async def test_image_endpoint(
    request: Request,
    prompt: Optional[str] = Form(None),
    art_style: Optional[str] = Form("Classic Comic Book")
):
    """
    Accepts Form or JSON to test image generation with a custom prompt.
    """
    if request.headers.get("content-type", "").startswith("application/json"):
        try:
            body = await request.json()
            prompt = body.get("prompt", "")
            art_style = body.get("art_style", "Classic Comic Book")
        except Exception:
            pass

    if not prompt or not prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt must not be empty.")

    result = test_image_generation(prompt=prompt.strip(), art_style=art_style.strip())
    return result

