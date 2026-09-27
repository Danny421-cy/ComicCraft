import uuid
from datetime import datetime
from typing import List
from app.models import ComicStoryRequest, EnrichedPanel, ComicLayout

def assemble_comic_layout(
    request: ComicStoryRequest,
    panels: List[EnrichedPanel],
    comic_id: str = None
) -> ComicLayout:
    """
    Pairs enriched panel text, dialogue, onomatopoeia, and image references
    into a unified ComicLayout schema.
    """
    if not comic_id:
        comic_id = f"comic_{uuid.uuid4().hex[:8]}"

    # Derive a punchy story title from prompt or protagonist
    title_words = [w.capitalize() for w in request.story_prompt.split()[:4]]
    story_title = " ".join(title_words)
    if len(story_title) < 5:
        story_title = f"{request.character_name}'s Adventure"

    layout = ComicLayout(
        comic_id=comic_id,
        title=story_title,
        character_name=request.character_name,
        setting=request.setting,
        tone=request.tone,
        art_style=request.art_style,
        panels=panels,
        created_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    )

    return layout

