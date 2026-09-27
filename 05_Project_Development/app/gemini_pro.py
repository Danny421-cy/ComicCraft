import json
import logging
import re
from typing import List
from app.config import GEMINI_API_KEY, GEMINI_PRO_MODEL, has_gemini_key
from app.models import PanelOutline, EnrichedPanel
from app.gemini_flash import detect_genre

logger = logging.getLogger(__name__)

GENRE_SCRIPTS = {
    "victorian": {
        "dialogues": [
            '{character}: "By the Queen\'s crown... the great clockwork escapement has stopped dead!"',
            '{character}: "Look at these coal-dust tracks! The golden chronos gear was pried free within the hour!"',
            '{character}: "Halt, scoundrel! You have no conception of the temporal disaster you court!"',
            '{character}: "For London, for time itself--I shall never surrender our world to chaos!"',
            '{character}: "Right on time. Another catastrophe averted before the morning kettle whistles."'
        ],
        "narrations": [
            "London, 1888. The chimes of Big Ben reverberate through the damp gaslit fog, but a sinister stillness grips the heart of the tower.",
            "Deep within the brass clockwork chamber, the missing golden gear threatens to freeze the very march of hours.",
            "Leaping across wet slate rooftops and smoking brick chimneys, {character} races against the ticking countdown.",
            "High above the misty Thames, steel clashes with steam as lightning cuts through the foggy spire in a climactic duel!",
            "Golden dawn pierces the river mist as the rhythmic ticking resumes. History marches forward once more."
        ],
        "sfx": ["CLANG!", "KRAK!", "WHOOSH!", "SHATTER!", "CHIME!"]
    },
    "scifi": {
        "dialogues": [
            '{character}: "Scanner telemetry confirms it: an anomalous transmission pulsing from outside the station hull."',
            '{character}: "Warning sirens! The alien monolith is resonating with our main reactor!"',
            '{character}: "Thrusters at maximum! If I don\'t reach the obelisk manual override, the whole sector collapses!"',
            '{character}: "Containment field synchronized! Channeling the pulse directly into the warp capacitor!"',
            '{character}: "Telemetry stable. The stars aren\'t just distant lights anymore--they\'re our next destination."'
        ],
        "narrations": [
            "Floating in the eternal dark of {setting}, instruments detect an ancient frequency older than the galaxy itself.",
            "Without warning, an alien monolith drops from hyperspace, enveloping the base in cascading rings of cyan energy.",
            "Suiting up for zero-gravity transit, {character} jets across the void as laser fire sparks along the exterior hull.",
            "Inside the alien core, antimatter and plasma fuse into a blinding tempest as the final showdown peaks!",
            "Silence reclaims the void of {setting}, leaving behind a luminous gateway pointing toward uncharted galaxies."
        ],
        "sfx": ["PULSE!", "WARNING!", "ZAP!", "KRAKOOM!", "WARP!"]
    },
    "fantasy": {
        "dialogues": [
            '{character}: "The winds from the high crags carry the scent of sulfur... the beast stirs."',
            '{character}: "Draw your bows! The Wyrm of the Peak has awakened from its thousand-year slumber!"',
            '{character}: "Hold the bridge! By the oath of {setting}, not a single talon shall cross!"',
            '{character}: "Shield of Light, turn aside this inferno! Give it everything you\'ve got!"',
            '{character}: "The realm is safe. The ancient pact of the mountain is honored once more."'
        ],
        "narrations": [
            "High upon the mist-wreathed crags of {setting}, ancient stone towers stand watch over the shadowed valleys.",
            "A deafening roar shatters the mountain calm as crimson dragon-fire illuminates the twilight clouds.",
            "Charging across the precarious rope-bridge, {character} draws runic steel amidst a blizzard of burning embers.",
            "Flames crash against glowing magic shields in an earth-shaking duel of courage against primordial fury!",
            "Morning sunbeams pierce through the departing smoke, bathing the peaceful kingdom in golden victory."
        ],
        "sfx": ["ROAR!", "KRAK!", "SLASH!", "BOOM!", "VICTORY!"]
    },
    "superhero": {
        "dialogues": [
            '{character}: "City police dispatch is overwhelmed. Neo Metropolis needs an answer right now."',
            '{character}: "A synchronized blackout? They\'re targeting the subterranean fusion grid!"',
            '{character}: "You thought you could outrun the grid? Not on my watch!"',
            '{character}: "Power surge or not, this city isn\'t yours to conquer! Stand down!"',
            '{character}: "Reactor safely cooled down. Just another night keeping the city bright."'
        ],
        "narrations": [
            "Perched high on the eagle-head gargoyle above {setting}, {character} watches the neon grid pulse below.",
            "Suddenly, sirens wail as three square miles of skyscrapers plunge into unnatural, pitch-black silence.",
            "Sprinting and vaulting across suspension cables at supersonic velocity, {character} closes in on the convoy.",
            "Sparks erupt like supernova flares as hero meets villain in a shattering, ground-level showdown!",
            "The dawn sun reflects across thousands of mirrored skyscrapers as peace returns to {setting}."
        ],
        "sfx": ["POW!", "KRAKOOM!", "WHOOSH!", "BAM!", "CHEER!"]
    },
    "noir": {
        "dialogues": [
            '{character}: "The dame said it was a simple job. In this town, nothing is ever simple."',
            '{character}: "Broken lock, wet mud on the carpet... our thief left in a hurry."',
            '{character}: "Step out from behind the crates! Your little monopoly ends tonight!"',
            '{character}: "Drop the piece! You won\'t get another warning!"',
            '{character}: "The morning papers will have their front page. I just want my coffee."'
        ],
        "narrations": [
            "Rain poured down like cold lead over the dark alleys of {setting}, washing away everything except the truth.",
            "Inside the dimly lit office, overturned files pointed toward a conspiracy reaching the highest towers.",
            "Shadows lengthened along the waterfront docks as {character} tracked the hurried splash of footsteps.",
            "Muzzle flashes split the midnight fog in a sharp, thunderous exchange of lead and nerve!",
            "The first cold rays of sunrise filtered through the mist, illuminating another case laid to rest."
        ],
        "sfx": ["CLICK!", "KRAK!", "RUN!", "BANG!", "EXHALE!"]
    }
}

def expand_narration_and_dialogue(
    outlines: List[PanelOutline],
    character_name: str,
    setting: str,
    tone: str
) -> List[EnrichedPanel]:
    """
    Expands a list of PanelOutline objects into EnrichedPanel objects containing
    panel-specific narration, character dialogue, and sound effects using Gemini Pro.
    """
    if has_gemini_key():
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)

            outline_payload = [
                {
                    "panel_number": p.panel_number,
                    "title": p.title,
                    "scene_description": p.scene_description,
                    "visual_prompt": p.visual_prompt
                }
                for p in outlines
            ]

            prompt = f"""
You are an award-winning comic book writer and dialogue specialist.
Expand the following {len(outlines)}-panel outline into full comic book script panels:
- Protagonist: "{character_name}"
- Setting: "{setting}"
- Tone / Mood: "{tone}"

Panels outline:
{json.dumps(outline_payload, indent=2)}

For EACH panel, generate:
1. "narration": A vivid, atmospheric comic caption box text (1-2 sentences setting the scene or internal monologue).
2. "dialogue": An authentic character dialogue line formatted as Character: "Speech" (or intense banter).
3. "sound_effect": A classic, punchy comic onomatopoeia sound effect in all caps (e.g. "KRAK!", "WHOOSH!", "ZAP!", "BOOM!").

Output ONLY valid JSON as a list of enriched panel objects:
[
  {{
    "panel_number": 1,
    "title": "...",
    "scene_description": "...",
    "visual_prompt": "...",
    "narration": "...",
    "dialogue": "{character_name}: '...'",
    "sound_effect": "WHOOSH!"
  }}
]
"""
            candidate_models = [GEMINI_PRO_MODEL]
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
                    enriched_panels = [EnrichedPanel(**item) for item in data]
                    if len(enriched_panels) == len(outlines):
                        return enriched_panels
                except Exception as m_err:
                    logger.warning(f"Gemini Pro model '{model_name}' failed: {m_err}. Trying next candidate...")
        except Exception as e:
            logger.warning(f"Gemini Pro API call failed or timed out: {e}. Falling back to procedural script enrichment.")

    # Dynamic procedural script enrichment
    return _generate_dynamic_fallback_script(outlines, character_name, setting, tone)

def _generate_dynamic_fallback_script(
    outlines: List[PanelOutline],
    character_name: str,
    setting: str,
    tone: str
) -> List[EnrichedPanel]:
    """Procedurally synthesizes narration, dialogue, and sound effects tailored to the genre and scene."""
    all_context = f"{setting} {tone} {' '.join(p.title for p in outlines)}"
    genre = detect_genre(all_context)

    script_data = GENRE_SCRIPTS.get(genre, GENRE_SCRIPTS["superhero"])
    dialogue_templates = script_data["dialogues"]
    narration_templates = script_data["narrations"]
    sfx_templates = script_data["sfx"]

    enriched: List[EnrichedPanel] = []

    for i, outline in enumerate(outlines):
        idx = min(i, len(dialogue_templates) - 1)
        raw_dlg = dialogue_templates[idx].format(character=character_name, setting=setting)
        raw_narr = narration_templates[idx].format(character=character_name, setting=setting)
        sfx = sfx_templates[idx % len(sfx_templates)]

        enriched.append(EnrichedPanel(
            panel_number=outline.panel_number,
            title=outline.title,
            scene_description=outline.scene_description,
            visual_prompt=outline.visual_prompt,
            narration=raw_narr,
            dialogue=raw_dlg,
            sound_effect=sfx
        ))

    return enriched
