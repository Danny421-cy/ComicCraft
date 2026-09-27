import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.config import STATIC_DIR
from app.routes import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("comiccraft")

# Initialize FastAPI Application
app = FastAPI(
    title="ComicCraft — AI Comic Story Creator",
    description=(
        "Autonomous generative AI web application that turns narrative story prompts "
        "into multi-panel illustrated comics with dialogue, captions, and printable PDF exports."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for cross-origin client usage
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files Directory
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Register Application Routes
app.include_router(router)

@app.on_event("startup")
async def startup_event():
    logger.info("==================================================")
    logger.info(" ComicCraft Server Initialized & Ready!")
    logger.info(" Web Application: http://127.0.0.1:8000")
    logger.info(" Swagger API Docs: http://127.0.0.1:8000/docs")
    logger.info("==================================================")

