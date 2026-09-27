import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Ensure 05_Project_Development is at the top of sys.path
DEV_DIR = Path(__file__).resolve().parent.parent.parent / "05_Project_Development"
if str(DEV_DIR) not in sys.path:
    sys.path.insert(0, str(DEV_DIR))

from app.main import app

@pytest.fixture(scope="session")
def client():
    """Provides a reusable FastAPI TestClient instance."""
    return TestClient(app)

