import json
import logging
import re
from typing import List
from app.config import GEMINI_API_KEY, GEMINI_FLASH_MODEL, has_gemini_key
from app.models import PanelOutline, ComicStoryRequest

logger = logging.getLogger(__name__)

# Genre-Specific Narrative Beats
STORY_GENRE_BEATS = {
    "victorian": [
        ("The Foggy Spires", "Investigating a subtle disturbance in the gaslit streets of London as mist rolls across the cobblestones.", "Victorian London gaslit cobblestone street at night, detective in coat and top hat observing glowing gas lamp in heavy fog"),
        ("The Shattered Chamber", "Entering the clockwork chamber to discover broken glass and the missing golden chronos gear.", "Interior of Victorian clock tower with massive interlocking brass cogs and gears, broken glass on floor, mysterious shadow fleeing"),
        ("Rooftop Pursuit", "Racing across wet slate roofs and smoking chimneys in frantic pursuit of the hooded saboteur.", "Victorian slate rooftops and smoking brick chimneys in London fog, detective leaping across alleyway in dramatic action silhouette"),
        ("Showdown on the Spire", "High-wire confrontation high above the Thames as the saboteur wields the stolen gear against lightning-streaked skies.", "Showdown atop clock tower spire above foggy London, lightning flash illuminating dramatic battle between detective and hooded thief"),
        ("Time Restored", "The golden gear is locked back into the escapement, church bells ringing over the river at dawn.", "Golden sunrise breaking over London and River Thames, clock hands ticking smoothly, detective standing tall with walking cane")
    ],
    "scifi": [
        ("The Quantum Signal", "Deep in the orbital research facility, an anomalous transmission pulses on the holographic scanners.", "Futuristic sci-fi orbital space station interior, glowing holographic screens and starry cosmos outside viewport"),
        ("The Anomaly Awakens", "A massive crystalline alien obelisk materializes outside the station, radiating intense cyan energy waves.", "Massive alien monolith floating silently in space near ringed planet, glowing with brilliant cyan light arcs"),
        ("Zero-G Infiltration", "Suiting up and jetting across the zero-gravity void toward the pulsating alien structure.", "Astronaut in sleek high-tech cyber suit maneuvering with thrusters across starfield toward alien monolith"),
        ("Core Resonance", "Reaching the central chamber to synchronize the containment field before the antimatter core overloads.", "Explosive energy climax inside alien core, brilliant white and magenta laser beams, character raising energy barrier"),
        ("New Horizons", "The alien drive is harmonized, opening a luminous hyperspace gateway toward uncharted stars.", "Starship warping through kaleidoscope starlight portal into a breathtaking colorful nebula, new dawn of exploration")
    ],
    "fantasy": [
        ("The Citadel of Spires", "Standing before the towering battlements of the mountain fortress as storm clouds gather.", "Epic fantasy castle fortress atop jagged mountain peak at twilight, banners fluttering in the wind, dramatic clouds"),
        ("Awakening of the Wyrm", "An earth-shattering tremor splits the stone as an ancient dragon unleashes a plume of crimson flame.", "Colossal horned dragon bursting from mountain cavern, glowing fiery breath lighting up castle battlements"),
        ("The High-Pass Charge", "Drawing the runic blade and charging across the precarious rope bridge through swirling embers.", "Hero in knight armor wielding glowing sword charging across stone bridge, dragon flying overhead in crimson sky"),
        ("Clash of Steel and Flame", "Deflecting the dragon's inferno with a crystalline magic shield in an explosive showdown.", "Epic showdown, knight raising radiant shield deflecting torrent of dragon fire, brilliant orange and blue light clash"),
        ("The Realm at Peace", "The dragon bows in ancient kinship as dawn breaks over the blooming valleys below.", "Peaceful sunrise over fantasy kingdom, knight resting hand on friendly dragon, golden sunbeams piercing morning clouds")
    ],
    "superhero": [
        ("The Watcher on the Ledge", "Perched atop the tallest skyscraper, surveying the neon grid as alarms echo through the canyons.", "Superhero standing heroic on skyscraper ledge overlooking neon city at dusk, cape billowing in the wind, searchlights"),
        ("The Grid Under Attack", "A massive electromagnetic surge disables power to three city blocks as villains initiate their heist.", "Dramatic city blackout, lightning crackling across electrical towers, villainous hover-drones swarming neon avenue"),
        ("Speedline Pursuit", "Leaping across rooftops and swinging between cranes at supersonic speed to cut off the getaway vehicle.", "Dynamic comic action shot, hero sprinting and leaping between suspension cables, motion blur and speed lines"),
        ("The Final Showdown", "Confronting the syndicate leader atop the power plant reactor, trading blows amidst electric arcs.", "Showdown panel, hero exchanging energy punch with armored villain, explosive lightning shockwave and impact stars"),
        ("Dawn Over the City", "The reactor is safely stabilized and the stolen power core secured as the sun rises over Metropolis.", "Hero standing victorious in morning sunlight giving thumbs up, citizens cheering below, sirens flashing peacefully")
    ],
    "noir": [
        ("The Rain-Slicked Alley", "Waiting in the shadow of a flickering neon sign as rain drums against the rusted fire escapes.", "Gritty noir detective with trench coat and fedora standing in dark rainy alley, neon light reflecting in puddles"),
        ("The Tipped Glass", "Discovering the ransacked office and a cryptic clue written on a cocktail napkin.", "Ransacked private eye office, overturned desk, Venetian blinds casting stripe shadows, magnifying glass on clue"),
        ("Footsteps in the Dark", "Pursuing the trench-coated suspect through the labyrinth of the waterfront docks.", "Shadowy waterfront docks at midnight, fog rolling in, silhouette of suspect fleeing between shipping containers"),
        ("Cornered at Pier 9", "The suspect draws a weapon, muzzle flash cutting through the darkness as bullets ricochet.", "High drama noir confrontation, muzzle flash illuminating startled faces, bullets sparking off steel cranes"),
        ("Case Closed", "Handing over the stolen ledger to the commissioner as the morning mist clears over the harbor.", "Detective lighting cigarette under streetlamp as police cars arrive, cold morning light breaking over the bay")
    ]
}

def detect_genre(text: str) -> str:
    """Categorizes narrative prompt into a genre key."""
    t = text.lower()
    if any(k in t for k in ["london", "victorian", "steampunk", "gaslit", "clock", "gear", "cog", "1888", "barnaby", "sherlock"]):
        return "victorian"
    elif any(k in t for k in ["cyber", "neon", "tokyo", "hacker", "synth", "matrix", "android", "chip", "grid"]):
        return "cyberpunk"
    elif any(k in t for k in ["space", "europa", "alien", "orbit", "robot", "satellite", "star", "station", "quantum", "galaxy"]):
        return "scifi"
    elif any(k in t for k in ["dragon", "castle", "knight", "sword", "magic", "wizard", "spire", "realm", "kingdom", "elf"]):
        return "fantasy"
    elif any(k in t for k in ["noir", "detective", "crime", "rain", "alley", "puddle", "dock", "clue", "shadow", "mobster"]):
        return "noir"
    elif any(k in t for k in ["pirate", "ship", "ocean", "sea", "island", "skull", "treasure", "captain", "sailing", "cannon"]):
        return "pirate"
    elif any(k in t for k in ["western", "cowboy", "desert", "outlaw", "sheriff", "saloon", "horse", "canyon", "mesa"]):
        return "western"
    elif any(k in t for k in ["horror", "ghost", "zombie", "haunted", "vampire", "monster", "cemetery", "graveyard", "creepy"]):
        return "horror"
    elif any(k in t for k in ["superhero", "hero", "villain", "super", "cape", "powers", "metropolis", "syndicate"]):
        return "superhero"
    return "general"

def generate_panel_outline(request: ComicStoryRequest) -> List[PanelOutline]:
    """
    Generates a structured comic outline using Google Gemini Flash.
    Returns a list of PanelOutline objects containing panel_number, title,
    scene_description, and visual_prompt.
    """
    if has_gemini_key():
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)

            prompt = f"""
You are an expert comic book editor and storyboard architect.
Create a structured {request.panel_count}-panel comic strip outline based on:
- Story Idea: "{request.story_prompt}"
- Protagonist / Main Character: "{request.character_name}"
- Setting / World: "{request.setting}"
- Tone / Mood: "{request.tone}"
- Visual Art Style: "{request.art_style}"

For each panel (from 1 to {request.panel_count}), provide:
1. "panel_number": sequential integer (1, 2, 3...)
2. "title": a punchy 2-4 word comic panel title tailored to this specific story
3. "scene_description": concise narrative description of what occurs in the scene
4. "visual_prompt": detailed visual illustration prompt tailored for Stable Diffusion in the art style '{request.art_style}', including camera angle, lighting, and character appearance.

Output ONLY valid JSON formatted as a list of objects:
[
  {{
    "panel_number": 1,
    "title": "Panel Title",
    "scene_description": "What happens here",
    "visual_prompt": "{request.art_style} style, camera angle, action description, crisp ink lines, comic colors"
  }}
]
"""
            candidate_models = [GEMINI_FLASH_MODEL]
            for fallback in ["gemini-flash-latest", "gemini-2.5-flash", "gemini-pro-latest"]:
                if fallback not in candidate_models:
                    candidate_models.append(fallback)

            for model_name in candidate_models:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    text = response.text.strip()

                    match = re.search(r"\[\s*\{.*\}\s*\]", text, re.DOTALL)
                    if match:
                        raw_json = match.group(0)
                    else:
                        raw_json = text

                    data = json.loads(raw_json)
                    panels = [PanelOutline(**item) for item in data]
                    if len(panels) >= request.panel_count:
                        panels = panels[:request.panel_count]
                    if len(panels) > 0:
                        for p in panels:
                            if request.character_name and request.character_name.lower() not in (p.visual_prompt + " " + p.scene_description).lower():
                                p.visual_prompt = f"{p.visual_prompt}, featuring {request.character_name}"
                        return panels
                except Exception as m_err:
                    logger.warning(f"Gemini Flash model '{model_name}' failed: {m_err}. Trying next candidate...")
        except Exception as e:
            logger.warning(f"Gemini Flash API call failed or timed out: {e}. Falling back to dynamic outline generator.")

    # Dynamic fallback outline synthesis
    return _generate_dynamic_fallback_outline(request)

def _generate_dynamic_fallback_outline(request: ComicStoryRequest) -> List[PanelOutline]:
    """Procedurally synthesizes a 5-panel outline uniquely tailored to the story prompt."""
    combined_text = f"{request.story_prompt} {request.setting} {request.tone} {request.character_name}"
    genre = detect_genre(combined_text)
    
    if genre in STORY_GENRE_BEATS:
        beats = STORY_GENRE_BEATS[genre]
    else:
        # Construct custom beats directly from user prompt keywords
        words = [w.strip(".,!?;:\"'") for w in request.story_prompt.split() if len(w) > 3]
        action_keyword = words[0] if words else "Adventure"
        target_keyword = words[-1] if len(words) > 1 else "Discovery"

        beats = [
            (f"The Journey Begins: {request.character_name}", f"In {request.setting}, {request.character_name} prepares for the task ahead: {request.story_prompt[:60]}.", f"{request.art_style} style, establishing wide shot of {request.character_name} in {request.setting}, vibrant comic line art"),
            (f"The {action_keyword.capitalize()} Disruption", f"An unexpected twist shatters the normal rhythm: a sudden threat regarding {target_keyword} emerges.", f"{request.art_style} style, dramatic Dutch tilt angle, {request.character_name} reacting to sudden anomaly in {request.setting}"),
            (f"Racing for {target_keyword.capitalize()}", f"{request.character_name} rushes into action, navigating dangerous obstacles across {request.setting}.", f"{request.art_style} style, fast action shot, {request.character_name} sprinting forward with speed lines"),
            (f"The Ultimate Climax", f"A high-stakes showdown where everything hinges on {request.character_name}'s quick thinking.", f"{request.art_style} style, explosive splash confrontation, high contrast dramatic lighting, energy clash"),
            (f"Dawn Over {request.setting.split()[0]}", f"With the crisis resolved, {request.character_name} surveys {request.setting} as calm returns.", f"{request.art_style} style, triumphant closing shot, {request.character_name} looking at dawn horizon")
        ]

    panels: List[PanelOutline] = []
    count = min(request.panel_count, len(beats))

    for i in range(count):
        title_tmpl, scene_tmpl, visual_tmpl = beats[i]
        title = f"{title_tmpl}: {request.character_name}" if i == 0 and ":" not in title_tmpl else title_tmpl
        scene = f"{scene_tmpl} ({request.character_name} in {request.setting})"
        visual = f"{request.art_style} style, {visual_tmpl}, featuring {request.character_name}, dramatic comic illustration, clean comic line art, vibrant palette"
        
        panels.append(PanelOutline(
            panel_number=i + 1,
            title=title,
            scene_description=scene,
            visual_prompt=visual
        ))

    return panels
