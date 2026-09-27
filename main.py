"""
ComicCraft - Master Deployment & Development Entrypoint
Delegates execution to the Phase 5 FastAPI core in 05_Project_Development.
Allows seamless hosting on Render, Railway, fly.io, Heroku, or direct local execution.
"""
import os
import sys
from pathlib import Path

# Resolve Phase 5 source directory
BASE_DIR = Path(__file__).resolve().parent
DEV_DIR = BASE_DIR / "05_Project_Development"

if str(DEV_DIR) not in sys.path:
    sys.path.insert(0, str(DEV_DIR))

# Import the core FastAPI instance
from app.main import app

if __name__ == "__main__":
    import uvicorn
    # Render and cloud platforms supply PORT dynamically in the environment
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    uvicorn.run("main:app", host=host, port=port)
