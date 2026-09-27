from app.models import ComicStoryRequest
from app.gemini_flash import generate_panel_outline, _generate_dynamic_fallback_outline

def test_generate_panel_outline_count():
    """TC-04: Verify outline generator returns exactly the requested number of panels."""
    req = ComicStoryRequest(
        story_prompt="Detective Fox chases a master thief across skyscraper rooftops.",
        character_name="Detective Fox",
        setting="Midnight City",
        tone="Noir",
        art_style="Classic Comic Book",
        panel_count=5
    )
    panels = generate_panel_outline(req)
    assert len(panels) == 5
    for i, p in enumerate(panels):
        assert p.panel_number == i + 1
        assert len(p.title) > 0
        assert len(p.scene_description) > 0
        assert len(p.visual_prompt) > 0

def test_generate_panel_outline_fallback_integrity():
    """TC-05: Verify procedural fallback produces meaningful character-aligned panels."""
    req = ComicStoryRequest(
        story_prompt="Super Robot rescues civilians from a volcano eruption.",
        character_name="Titan-7",
        setting="Mount Magma",
        tone="Superhero",
        art_style="Manga / Anime",
        panel_count=3
    )
    panels = _generate_dynamic_fallback_outline(req)
    assert len(panels) == 3
    assert panels[0].panel_number == 1
    assert "Titan-7" in panels[0].visual_prompt or "Titan-7" in panels[0].scene_description

