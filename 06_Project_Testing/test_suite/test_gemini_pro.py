from app.models import PanelOutline
from app.gemini_pro import expand_narration_and_dialogue

def test_expand_dialogue_and_narration():
    """TC-06 & TC-07: Verify script enrichment adds narration, dialogue, and onomatopoeia."""
    outlines = [
        PanelOutline(
            panel_number=1,
            title="Introduction",
            scene_description="Hero stands on rooftop",
            visual_prompt="Hero standing tall at dusk"
        ),
        PanelOutline(
            panel_number=2,
            title="The Attack",
            scene_description="Laser beam strikes tower",
            visual_prompt="Explosion on antenna"
        )
    ]

    enriched = expand_narration_and_dialogue(
        outlines=outlines,
        character_name="Volt",
        setting="Apex City",
        tone="Action"
    )

    assert len(enriched) == 2
    for p in enriched:
        assert len(p.narration) > 0
        assert len(p.dialogue) > 0
        assert len(p.sound_effect) > 0

