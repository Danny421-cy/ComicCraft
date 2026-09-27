import pytest
from pydantic import ValidationError
from app.models import ComicStoryRequest, PanelOutline, EnrichedPanel, ComicLayout

def test_comic_story_request_valid():
    """TC-02: Valid ComicStoryRequest instantiation."""
    req = ComicStoryRequest(
        story_prompt="A courageous archaeologist uncovers an ancient alien artifact in the Sahara.",
        character_name="Dr. Jack Stone",
        setting="Sahara Desert",
        tone="Adventurous",
        art_style="Classic Comic Book",
        panel_count=5
    )
    assert req.character_name == "Dr. Jack Stone"
    assert req.panel_count == 5
    assert "archaeologist" in req.story_prompt

def test_comic_story_request_invalid_panel_count():
    """TC-03: Invalid panel count should raise ValidationError."""
    with pytest.raises(ValidationError):
        ComicStoryRequest(
            story_prompt="Sample story",
            panel_count=25  # Exceeds max 10
        )

