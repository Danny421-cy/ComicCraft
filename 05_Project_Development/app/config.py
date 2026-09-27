import os
from pathlib import Path
from dotenv import load_dotenv

# Resolve project directories
# config.py is in 05_Project_Development/app/
APP_DIR = Path(__file__).resolve().parent
PROJECT_DEV_DIR = APP_DIR.parent
ROOT_DIR = PROJECT_DEV_DIR.parent

# Load .env from 05_Project_Development or root
dotenv_path = PROJECT_DEV_DIR / ".env"
if not dotenv_path.exists():
    dotenv_path = ROOT_DIR / ".env"

load_dotenv(dotenv_path=dotenv_path, override=True)

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
HF_API_KEY = os.getenv("HF_API_KEY", "").strip()

# Gemini Models
GEMINI_FLASH_MODEL = os.getenv("GEMINI_FLASH_MODEL", "gemini-1.5-flash")
GEMINI_PRO_MODEL = os.getenv("GEMINI_PRO_MODEL", "gemini-1.5-pro")

# Hugging Face Model for Diffusion
HF_MODEL_ID = os.getenv("HF_MODEL_ID", "runwayml/stable-diffusion-v1-5")

# Static & Template Paths
STATIC_DIR = PROJECT_DEV_DIR / "static"
PANELS_DIR = STATIC_DIR / "panels"
EXPORTS_DIR = STATIC_DIR / "exports"
FONTS_DIR = STATIC_DIR / "fonts"
TEMPLATES_DIR = PROJECT_DEV_DIR / "templates"

# Auto-create necessary directories
for path in [STATIC_DIR, PANELS_DIR, EXPORTS_DIR, FONTS_DIR, TEMPLATES_DIR]:
    path.mkdir(parents=True, exist_ok=True)

def has_gemini_key() -> bool:
    """Returns True if a valid non-empty Gemini API key is present."""
    return bool(GEMINI_API_KEY and not GEMINI_API_KEY.startswith("your_"))

def has_hf_key() -> bool:
    """Returns True if a valid non-empty Hugging Face key is present."""
    return bool(HF_API_KEY and not HF_API_KEY.startswith("your_"))

