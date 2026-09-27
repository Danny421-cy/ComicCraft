import os
from app.models import ComicStoryRequest, EnrichedPanel
from app.layout_builder import assemble_comic_layout
from app.exporters import export_comic_to_pdf, _clean_text

def test_assemble_comic_layout():
    """TC-10: Verify layout assembler creates valid ComicLayout."""
    req = ComicStoryRequest(
        story_prompt="Detective Fox investigates the vanished museum jewel.",
        character_name="Detective Fox",
        setting="Museum",
        tone="Mystery",
        art_style="Classic Comic Book",
        panel_count=2
    )
    panels = [
        EnrichedPanel(
            panel_number=1,
            title="The Vault",
            scene_description="Empty pedestal",
            visual_prompt="Empty velvet pedestal with broken glass",
            narration="The midnight bell tolled just as the glass shattered.",
            dialogue="Fox: 'A clean cut. Only one thief could pull this off.'",
            sound_effect="SHATTER!"
        ),
        EnrichedPanel(
            panel_number=2,
            title="The Clue",
            scene_description="Feather on the floor",
            visual_prompt="Magnifying glass focusing on purple raven feather",
            narration="In the dust lay a calling card impossible to mistake.",
            dialogue="Fox: 'The Raven is back.'",
            sound_effect="GASP!"
        )
    ]

    layout = assemble_comic_layout(req, panels, comic_id="test_comic_101")
    assert layout.comic_id == "test_comic_101"
    assert layout.character_name == "Detective Fox"
    assert len(layout.panels) == 2

def test_export_comic_to_pdf():
    """TC-11: Verify FPDF2 compiles layout into printable PDF."""
    req = ComicStoryRequest(
        story_prompt="Test PDF story",
        character_name="TestHero",
        setting="TestCity",
        tone="Action",
        art_style="Classic Comic Book",
        panel_count=1
    )
    panels = [
        EnrichedPanel(
            panel_number=1,
            title="Test Panel",
            scene_description="Hero flying",
            visual_prompt="Hero in blue cape soaring above skyscrapers",
            narration="A new dawn begins over the test metropolis.",
            dialogue="TestHero: 'Testing PDF generation!'",
            sound_effect="ZOOM!"
        )
    ]
    layout = assemble_comic_layout(req, panels, comic_id="test_pdf_export_99")
    pdf_url, pdf_path = export_comic_to_pdf(layout)

    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 1000  # Valid non-empty PDF file
    assert pdf_url.startswith("/static/exports/")

def test_clean_text_unicode_sanitizer():
    """TC-12: Verify text sanitizer converts curly quotes and dashes without failing."""
    dirty_text = "‘Hello’ “World” — and… dashes"
    cleaned = _clean_text(dirty_text)
    assert "‘" not in cleaned
    assert "“" not in cleaned
    assert "—" not in cleaned
    assert "Hello" in cleaned

