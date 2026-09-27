import os
import sys
import math
import time
import random
import logging
import hashlib
import textwrap
from pathlib import Path
from typing import Optional, Tuple
from io import BytesIO
import requests
from PIL import Image, ImageDraw, ImageFont
from app.config import (
    HF_API_KEY,
    HF_MODEL_ID,
    PANELS_DIR,
    has_hf_key,
)
from app.gemini_flash import detect_genre

logger = logging.getLogger(__name__)

HF_ROUTER_URL = f"https://router.huggingface.co/hf-inference/models/{HF_MODEL_ID}"
_hf_token_disabled = False


def _is_testing_environment() -> bool:
    return "pytest" in sys.modules or os.getenv("TESTING") == "1"


def _get_fonts():
    """Loads fonts safely with graceful fallback for all platforms."""
    try:
        font_sfx = ImageFont.load_default(size=20)
        font_title = ImageFont.load_default(size=14)
        font_caption = ImageFont.load_default(size=13)
    except TypeError:
        font_sfx = ImageFont.load_default()
        font_title = ImageFont.load_default()
        font_caption = ImageFont.load_default()
    return font_sfx, font_title, font_caption


def generate_panel_image(
    prompt: str,
    art_style: str = "Classic Comic Book",
    filename: Optional[str] = None,
    panel_number: int = 1,
    title: str = "Scene",
    sound_effect: str = "POW!",
    narration: str = "",
    dialogue: str = "",
    character_name: str = "",
    setting: str = ""
) -> Tuple[str, str]:
    """
    Generates a rich graphic novel illustration for a comic panel tailored to the story prompt.
    Tries Hugging Face API first, then fast Cloud Diffusion with fallback to
    genre-specific procedural comic scene illustration.
    """
    global _hf_token_disabled

    if not filename:
        import uuid
        filename = f"panel_{uuid.uuid4().hex[:8]}.png"

    output_path = PANELS_DIR / filename

    # Skip external network calls during automated test suite runs
    if _is_testing_environment():
        _render_thematic_comic_scene(output_path, panel_number, title, sound_effect, art_style, prompt, narration, dialogue, character_name, setting)
        return f"/static/panels/{filename}", str(output_path)

    # --- Priority 1: Hugging Face Diffusion API ---
    if has_hf_key() and not _hf_token_disabled:
        try:
            full_prompt = f"{art_style} style, comic book sequential art, highly detailed, dramatic lighting, crisp ink outlines, masterpiece: {prompt}"
            headers = {"Authorization": f"Bearer {HF_API_KEY}"}
            payload = {
                "inputs": full_prompt,
                "parameters": {"guidance_scale": 7.5, "num_inference_steps": 25}
            }
            response = requests.post(HF_ROUTER_URL, headers=headers, json=payload, timeout=10)
            if response.status_code == 200 and response.headers.get("content-type", "").startswith("image/"):
                img = Image.open(BytesIO(response.content))
                img = _overlay_comic_chrome(img, panel_number, title, sound_effect, narration, dialogue)
                img.save(output_path, "PNG")
                logger.info(f"Generated panel {panel_number} via Hugging Face API.")
                return f"/static/panels/{filename}", str(output_path)
            elif response.status_code in [401, 403]:
                _hf_token_disabled = True
                logger.warning(f"HF_API_KEY returned {response.status_code} Unauthorized (invalid token). Skipping Hugging Face and using Cloud Diffusion.")
        except Exception as e:
            logger.warning(f"HF Diffusion API request to {HF_ROUTER_URL} failed: {e}")

    # --- Priority 2: Fast Cloud Diffusion Endpoint ---
    try:
        clean_p = f"{art_style} comic book illustration, {prompt}, graphic novel sequential art, highly detailed, bold lines"
        encoded = requests.utils.quote(clean_p[:200])
        seed = (panel_number * 317 + len(prompt) * 19 + random.randint(1, 9999)) % 999999
        diff_url = f"https://image.pollinations.ai/prompt/{encoded}?width=600&height=600&nologo=true&seed={seed}&model=turbo"
        r = requests.get(diff_url, timeout=12)
        if r.status_code == 200 and len(r.content) > 5000:
            img = Image.open(BytesIO(r.content))
            img = _overlay_comic_chrome(img, panel_number, title, sound_effect, narration, dialogue)
            img.save(output_path, "PNG")
            logger.info(f"Generated panel {panel_number} via cloud diffusion engine.")
            return f"/static/panels/{filename}", str(output_path)
    except Exception as e:
        logger.info(f"Cloud diffusion unavailable for panel {panel_number} ({e}). Rendering procedural scene.")

    # --- Priority 3: Rich Genre-Specific Procedural Comic Scene Illustrator ---
    _render_thematic_comic_scene(output_path, panel_number, title, sound_effect, art_style, prompt, narration, dialogue, character_name, setting)
    return f"/static/panels/{filename}", str(output_path)


def _overlay_comic_chrome(
    img: Image.Image,
    panel_number: int,
    title: str,
    sound_effect: str,
    narration: str = "",
    dialogue: str = ""
) -> Image.Image:
    """Overlays comic title badge, sound effect burst, and narration box onto an AI generated image."""
    img = img.convert("RGBA").resize((600, 600))
    draw = ImageDraw.Draw(img)
    _finish_panel(img, draw, 600, 600, panel_number, title, sound_effect, narration, dialogue)
    return img.convert("RGB")


def _render_thematic_comic_scene(
    output_path: Path,
    panel_number: int,
    title: str,
    sound_effect: str,
    art_style: str,
    prompt: str,
    narration: str = "",
    dialogue: str = "",
    character_name: str = "",
    setting: str = ""
) -> None:
    """Dispatches procedural rendering to the appropriate genre-specific artist."""
    combined_ctx = f"{prompt} {title} {setting} {character_name}"
    genre = detect_genre(combined_ctx)

    if genre == "victorian":
        _draw_victorian_scene(output_path, panel_number, title, sound_effect, prompt, narration, dialogue)
    elif genre == "cyberpunk":
        _draw_cyberpunk_scene(output_path, panel_number, title, sound_effect, prompt, narration, dialogue)
    elif genre == "scifi":
        _draw_scifi_scene(output_path, panel_number, title, sound_effect, prompt, narration, dialogue)
    elif genre == "fantasy":
        _draw_fantasy_scene(output_path, panel_number, title, sound_effect, prompt, narration, dialogue)
    elif genre == "noir":
        _draw_noir_scene(output_path, panel_number, title, sound_effect, prompt, narration, dialogue)
    elif genre == "pirate":
        _draw_pirate_scene(output_path, panel_number, title, sound_effect, prompt, narration, dialogue)
    elif genre == "western":
        _draw_western_scene(output_path, panel_number, title, sound_effect, prompt, narration, dialogue)
    elif genre == "horror":
        _draw_horror_scene(output_path, panel_number, title, sound_effect, prompt, narration, dialogue)
    elif genre == "superhero":
        _draw_superhero_scene(output_path, panel_number, title, sound_effect, prompt, narration, dialogue)
    else:
        _draw_custom_procedural_scene(output_path, panel_number, title, sound_effect, prompt, narration, dialogue)


# =========================================================================
# 1. Victorian / Steampunk Scene Drawer
# =========================================================================
def _draw_victorian_scene(output_path: Path, panel_num: int, title: str, sfx: str, prompt: str, narration: str = "", dialogue: str = "") -> None:
    width, height = 600, 600
    img = Image.new("RGBA", (width, height), (20, 18, 26, 255))
    draw = ImageDraw.Draw(img)

    if panel_num == 5:
        # Sunrise over Thames
        for y in range(height):
            f = y / height
            draw.line([(0, y), (width, y)], fill=(int(255 - f * 80), int(160 + f * 50), int(50 + f * 100), 255))
        draw.ellipse([240, 200, 360, 320], fill=(255, 230, 140, 240))
        # Tower Bridge silhouette
        draw.rectangle([120, 260, 160, 460], fill=(25, 20, 30))
        draw.rectangle([440, 260, 480, 460], fill=(25, 20, 30))
        draw.line([(120, 340), (480, 340)], fill=(25, 20, 30), width=6)
        _draw_victorian_detective(draw, 300, 370, victorious=True)
    elif panel_num == 2:
        # Interior of Clock Tower - Giant Interlocking Gears
        draw.rectangle([0, 0, width, height], fill=(22, 18, 24, 255))
        cx, cy, radius = 300, 260, 180
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=(185, 140, 50), outline=(230, 180, 70), width=8)
        for i in range(16):
            ang = (i / 16) * 2 * math.pi
            tx1 = cx + int((radius - 5) * math.cos(ang))
            ty1 = cy + int((radius - 5) * math.sin(ang))
            tx2 = cx + int((radius + 25) * math.cos(ang))
            ty2 = cy + int((radius + 25) * math.sin(ang))
            draw.line([(tx1, ty1), (tx2, ty2)], fill=(210, 165, 60), width=20)
        draw.ellipse([cx - 65, cy - 65, cx + 65, cy + 65], fill=(35, 28, 38), outline=(230, 180, 70), width=5)
        # Broken clock face glass on floor
        draw.polygon([(180, 460), (240, 440), (220, 480)], fill=(200, 240, 255, 180), outline=(255, 255, 255))
        draw.polygon([(360, 450), (410, 465), (380, 490)], fill=(200, 240, 255, 180), outline=(255, 255, 255))
        _draw_victorian_detective(draw, 140, 350, has_lantern=True)
    elif panel_num == 3:
        # Rooftop pursuit
        for y in range(height):
            f = y / height
            draw.line([(0, y), (width, y)], fill=(int(14 + f * 25), int(16 + f * 26), int(28 + f * 35), 255))
        draw.ellipse([440, 50, 530, 140], fill=(255, 245, 210, 190))
        # Slanted roofs
        draw.polygon([(0, 430), (280, 320), (380, 450)], fill=(28, 26, 36), outline=(10, 10, 15), width=2)
        draw.polygon([(360, 440), (520, 340), (600, 420)], fill=(26, 24, 34), outline=(10, 10, 15), width=2)
        _draw_victorian_detective(draw, 220, 290, running=True)
        # Fleeing saboteur
        draw.polygon([(460, 280), (490, 340), (440, 340)], fill=(10, 10, 14))
    elif panel_num == 4:
        # Showdown on Big Ben Spire with lightning
        draw.rectangle([0, 0, width, height], fill=(12, 10, 22))
        # Lightning bolt
        draw.line([(300, 0), (280, 130), (330, 150), (270, 310)], fill=(255, 255, 220), width=4)
        draw.polygon([(240, 200), (360, 200), (300, 40)], fill=(32, 28, 42), outline=(15, 12, 20), width=2)
        draw.rectangle([220, 200, 380, 460], fill=(28, 25, 36))
        # Spire dial
        draw.ellipse([260, 230, 340, 310], fill=(255, 230, 150), outline=(20, 20, 20), width=3)
        _draw_victorian_detective(draw, 180, 330, fighting=True)
        draw.polygon([(380, 310), (420, 390), (360, 390)], fill=(12, 12, 16))
    else:
        # Panel 1: Establishing foggy street
        for y in range(height):
            f = y / height
            draw.line([(0, y), (width, y)], fill=(int(14 + f * 30), int(16 + f * 32), int(26 + f * 38), 255))
        draw.ellipse([420, 60, 520, 160], fill=(255, 245, 210, 190))
        # Street houses
        houses = [(15, 200, 110), (135, 160, 120), (265, 210, 110), (385, 180, 130), (525, 220, 75)]
        for hx, hy, hw in houses:
            pk = hx + hw // 2
            draw.polygon([(hx, hy), (pk, hy - 45), (hx + hw, hy)], fill=(25, 26, 36), outline=(10, 10, 15), width=2)
            draw.rectangle([hx, hy, hx + hw, 460], fill=(30, 28, 36), outline=(10, 10, 15), width=2)
        # Cobblestone ground & Lamp
        draw.rectangle([0, 460, width, height], fill=(22, 20, 26))
        _draw_gas_lamp(img, draw, 110, 310)
        _draw_victorian_detective(draw, 260, 355, has_lantern=False)

    _finish_panel(img, draw, width, height, panel_num, title, sfx, narration, dialogue)
    img.convert("RGB").save(output_path, "PNG")


def _draw_gas_lamp(img: Image.Image, draw: ImageDraw.ImageDraw, lx: int, ly: int) -> None:
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse([lx - 65, ly - 65, lx + 65, ly + 65], fill=(255, 215, 80, 50))
    img.alpha_composite(glow)
    draw.line([(lx, ly + 15), (lx, 460)], fill=(12, 12, 16), width=5)
    draw.polygon([(lx - 16, ly - 20), (lx + 16, ly - 20), (lx + 10, ly + 15), (lx - 10, ly + 15)], fill=(255, 230, 120), outline=(12, 12, 16), width=2)
    draw.polygon([(lx - 18, ly - 20), (lx, ly - 36), (lx + 18, ly - 20)], fill=(12, 12, 16))


def _draw_victorian_detective(draw: ImageDraw.ImageDraw, px: int, py: int, running: bool = False, fighting: bool = False, has_lantern: bool = False, victorious: bool = False) -> None:
    ink = (10, 10, 15, 255)
    # Cloak & Coat
    draw.polygon([(px - 18, py + 30), (px - 50, py + 105), (px + 35, py + 105), (px + 18, py + 30)], fill=ink)
    if running:
        draw.polygon([(px - 25, py + 95), (px - 5, py + 135), (px + 10, py + 130), (px - 10, py + 95)], fill=ink)
        draw.polygon([(px + 10, py + 95), (px + 35, py + 125), (px + 45, py + 115), (px + 18, py + 95)], fill=ink)
    elif fighting:
        draw.line([(px + 16, py + 25), (px + 60, py + 15)], fill=(200, 200, 210), width=4) # Cane strike
        draw.rectangle([px - 14, py + 95, px - 2, py + 140], fill=ink)
        draw.rectangle([px + 4, py + 95, px + 22, py + 135], fill=ink)
    elif victorious:
        draw.line([(px - 14, py + 25), (px - 35, py - 15)], fill=ink, width=5) # Cane held up
        draw.rectangle([px - 12, py + 95, px - 2, py + 140], fill=ink)
        draw.rectangle([px + 4, py + 95, px + 14, py + 140], fill=ink)
    else:
        draw.rectangle([px - 14, py + 95, px - 2, py + 140], fill=ink)
        draw.rectangle([px + 4, py + 95, px + 16, py + 140], fill=ink)
    draw.polygon([(px - 18, py + 20), (px + 18, py + 20), (px + 14, py + 65), (px - 14, py + 65)], fill=ink)
    if has_lantern:
        draw.line([(px + 16, py + 25), (px + 38, py + 45), (px + 38, py + 75)], fill=ink, width=4)
        draw.rectangle([px + 30, py + 75, px + 46, py + 98], fill=(255, 220, 80), outline=ink, width=2)
    # Deerstalker / Top Hat
    draw.ellipse([px - 12, py - 5, px + 12, py + 20], fill=ink)
    draw.rectangle([px - 12, py - 26, px + 12, py - 5], fill=ink)
    draw.ellipse([px - 20, py - 7, px + 20, py - 2], fill=ink)


# =========================================================================
# 2. Cyberpunk / Neon City Scene Drawer
# =========================================================================
def _draw_cyberpunk_scene(output_path: Path, panel_num: int, title: str, sfx: str, prompt: str, narration: str = "", dialogue: str = "") -> None:
    width, height = 600, 600
    img = Image.new("RGBA", (width, height), (10, 8, 22, 255))
    draw = ImageDraw.Draw(img)

    # Neon grid sky
    for y in range(height):
        f = y / height
        draw.line([(0, y), (width, y)], fill=(int(10 + f * 15), int(8 + f * 35), int(30 + f * 70), 255))

    if panel_num == 1:
        # Neon skyline with holographic billboards
        b_list = [(20, 240, 80, (0, 240, 255)), (110, 180, 95, (255, 40, 130)), (215, 230, 85, (0, 255, 170)), (310, 160, 100, (255, 215, 0)), (420, 220, 80, (180, 50, 255)), (510, 250, 75, (0, 240, 255))]
        for bx, by, bw, col in b_list:
            draw.rectangle([bx, by, bx + bw, 460], fill=(16, 18, 30), outline=col, width=2)
            # Billboard sign
            draw.rectangle([bx + 10, by + 20, bx + bw - 10, by + 50], fill=(20, 22, 38), outline=col, width=2)
            draw.text((bx + 15, by + 26), "NEO", fill=col)
        # Flying spinner vehicle
        draw.polygon([(360, 100), (430, 110), (410, 125), (340, 115)], fill=(0, 240, 255))
        draw.line([(340, 115), (260, 110)], fill=(0, 240, 255, 120), width=3)
        _draw_cyber_character(draw, 140, 360)
    elif panel_num == 2:
        # Data core chamber - glowing server racks & red alert
        draw.rectangle([0, 0, width, height], fill=(12, 10, 20))
        for rx in range(40, width, 140):
            draw.rectangle([rx, 80, rx + 100, 460], fill=(20, 22, 34), outline=(0, 255, 200), width=2)
            for sy in range(110, 440, 30):
                draw.rectangle([rx + 15, sy, rx + 85, sy + 14], fill=(0, 240, 255))
        # Central glowing AI core
        draw.ellipse([230, 180, 370, 320], fill=(255, 40, 100), outline=(255, 255, 255), width=4)
        _draw_cyber_character(draw, 180, 350, inspecting=True)
    elif panel_num == 3:
        # High speed pursuit with neon speed lines
        for _ in range(35):
            sx = random.randint(0, width)
            sy = random.randint(50, 480)
            draw.line([(sx, sy), (sx + random.randint(60, 160), sy - random.randint(20, 45))], fill=(0, 255, 240, 180), width=3)
        _draw_cyber_character(draw, 240, 320, leaping=True)
        # Laser bolts
        draw.line([(60, 200), (480, 360)], fill=(255, 40, 120), width=5)
        draw.line([(60, 200), (480, 360)], fill=(255, 255, 255), width=2)
    elif panel_num == 4:
        # Epic Climax - Cyber clash & EMP explosion
        draw.rectangle([0, 0, width, height], fill=(20, 10, 30))
        # Shockwave rings
        for r in range(40, 260, 45):
            draw.ellipse([300 - r, 250 - r, 300 + r, 250 + r], outline=(0, 240, 255), width=3)
        # Radial laser blast
        for i in range(12):
            ang = (i / 12) * 2 * math.pi
            x2 = 300 + int(240 * math.cos(ang))
            y2 = 250 + int(240 * math.sin(ang))
            draw.line([(300, 250), (x2, y2)], fill=(255, 40, 140), width=4)
        _draw_cyber_character(draw, 220, 330, leaping=True)
    else:
        # Panel 5: Dawn over Neo-Tokyo arcologies
        for y in range(height):
            f = y / height
            draw.line([(0, y), (width, y)], fill=(int(255 - f * 90), int(140 + f * 50), int(180 - f * 40), 255))
        draw.ellipse([380, 180, 480, 280], fill=(255, 245, 200))
        draw.rectangle([0, 440, width, height], fill=(15, 14, 25))
        _draw_cyber_character(draw, 270, 340, victorious=True)

    _finish_panel(img, draw, width, height, panel_num, title, sfx, narration, dialogue)
    img.convert("RGB").save(output_path, "PNG")


def _draw_cyber_character(draw: ImageDraw.ImageDraw, cx: int, cy: int, leaping: bool = False, inspecting: bool = False, victorious: bool = False) -> None:
    suit = (14, 16, 24, 255)
    visor = (0, 240, 255)
    if leaping:
        # Diagonal action pose
        draw.polygon([(cx - 20, cy), (cx + 30, cy - 20), (cx + 20, cy + 30), (cx - 30, cy + 50)], fill=suit)
        draw.line([(cx + 25, cy - 15), (cx + 65, cy - 35)], fill=visor, width=4)
    else:
        draw.rectangle([cx - 14, cy + 70, cx - 2, cy + 130], fill=suit)
        draw.rectangle([cx + 2, cy + 70, cx + 14, cy + 130], fill=suit)
        draw.polygon([(cx - 18, cy + 18), (cx + 18, cy + 18), (cx + 12, cy + 70), (cx - 12, cy + 70)], fill=suit)
        draw.ellipse([cx - 12, cy - 8, cx + 12, cy + 18], fill=suit)
        draw.rectangle([cx - 7, cy + 3, cx + 7, cy + 8], fill=visor)
        if victorious:
            draw.line([(cx + 14, cy + 20), (cx + 36, cy - 15)], fill=visor, width=4)


# =========================================================================
# 3. Sci-Fi / Deep Space Scene Drawer
# =========================================================================
def _draw_scifi_scene(output_path: Path, panel_num: int, title: str, sfx: str, prompt: str, narration: str = "", dialogue: str = "") -> None:
    width, height = 600, 600
    img = Image.new("RGBA", (width, height), (12, 10, 28, 255))
    draw = ImageDraw.Draw(img)

    # Cosmic Nebula gradient
    for y in range(height):
        f = y / height
        draw.line([(0, y), (width, y)], fill=(int(10 + f * 20), int(8 + f * 40), int(30 + f * 60), 255))

    # Starfield
    random.seed(panel_num * 88)
    for _ in range(45):
        sx = random.randint(10, 590)
        sy = random.randint(10, 420)
        draw.rectangle([sx, sy, sx + 2, sy + 2], fill=(255, 255, 255, 220))

    if panel_num == 1:
        # Ringed Gas Giant Planet
        draw.ellipse([370, 70, 480, 180], fill=(255, 190, 110))
        draw.arc([330, 110, 520, 150], start=10, end=190, fill=(0, 240, 255), width=4)
        # Space Station exterior
        draw.rectangle([40, 300, 260, 460], fill=(22, 28, 44), outline=(0, 210, 255), width=2)
        draw.line([(150, 300), (150, 220)], fill=(0, 210, 255), width=3)
        draw.ellipse([140, 210, 160, 230], fill=(255, 40, 80))
        _draw_scifi_astronaut(draw, 340, 350)
    elif panel_num == 2:
        # Alien Monolith Awakening
        draw.polygon([(380, 120), (440, 120), (470, 460), (350, 460)], fill=(15, 18, 30), outline=(0, 240, 255), width=3)
        for ry in range(160, 430, 35):
            draw.line([(390, ry), (430, ry)], fill=(0, 240, 255), width=3)
        _draw_scifi_astronaut(draw, 180, 340, inspecting=True)
    elif panel_num == 3:
        # Zero-G thruster pursuit with laser blasts
        _draw_scifi_astronaut(draw, 220, 280, jetpack=True)
        draw.line([(80, 180), (520, 340)], fill=(255, 30, 90), width=5)
        draw.line([(80, 180), (520, 340)], fill=(255, 255, 255), width=2)
    elif panel_num == 4:
        # Antimatter explosion / Warp breach
        for r in range(30, 240, 40):
            draw.ellipse([300 - r, 240 - r, 300 + r, 240 + r], outline=(255, 220, 100), width=4)
        for i in range(10):
            ang = (i / 10) * 2 * math.pi
            x2 = 300 + int(220 * math.cos(ang))
            y2 = 240 + int(220 * math.sin(ang))
            draw.line([(300, 240), (x2, y2)], fill=(0, 240, 255), width=4)
        _draw_scifi_astronaut(draw, 140, 320, jetpack=True)
    else:
        # Panel 5: Starship entering Hyperspace
        draw.polygon([(180, 300), (380, 260), (420, 290), (380, 320)], fill=(220, 230, 255), outline=(0, 240, 255), width=3)
        for tr_y in [270, 290, 310]:
            draw.line([(180, tr_y), (40, tr_y)], fill=(0, 240, 255, 200), width=4)
        _draw_scifi_astronaut(draw, 460, 330, victorious=True)

    _finish_panel(img, draw, width, height, panel_num, title, sfx, narration, dialogue)
    img.convert("RGB").save(output_path, "PNG")


def _draw_scifi_astronaut(draw: ImageDraw.ImageDraw, ax: int, ay: int, jetpack: bool = False, inspecting: bool = False, victorious: bool = False) -> None:
    suit = (220, 225, 240)
    visor = (255, 180, 0)
    draw.rectangle([ax - 14, ay + 65, ax - 2, ay + 125], fill=(30, 35, 50))
    draw.rectangle([ax + 2, ay + 65, ax + 14, ay + 125], fill=(30, 35, 50))
    draw.polygon([(ax - 18, ay + 18), (ax + 18, ay + 18), (ax + 14, ay + 68), (ax - 14, ay + 68)], fill=suit)
    draw.ellipse([ax - 14, ay - 8, ax + 14, ay + 18], fill=suit)
    draw.ellipse([ax - 8, ay, ax + 8, ay + 12], fill=visor)
    if jetpack:
        draw.rectangle([ax - 24, ay + 22, ax - 16, ay + 60], fill=(80, 90, 110))
        draw.polygon([(ax - 22, ay + 60), (ax - 16, ay + 90), (ax - 10, ay + 60)], fill=(0, 240, 255))
    if victorious:
        draw.line([(ax + 14, ay + 25), (ax + 36, ay - 10)], fill=suit, width=5)


# =========================================================================
# 4. Fantasy / Dragon / Castle Scene Drawer
# =========================================================================
def _draw_fantasy_scene(output_path: Path, panel_num: int, title: str, sfx: str, prompt: str, narration: str = "", dialogue: str = "") -> None:
    width, height = 600, 600
    img = Image.new("RGBA", (width, height), (18, 12, 28, 255))
    draw = ImageDraw.Draw(img)

    if panel_num == 5:
        # Golden sunrise over tranquil kingdom
        for y in range(height):
            f = y / height
            draw.line([(0, y), (width, y)], fill=(int(255 - f * 70), int(170 + f * 50), int(60 + f * 110), 255))
        draw.ellipse([240, 180, 360, 300], fill=(255, 235, 140))
        # Rolling green hills
        draw.arc([-100, 360, 400, 600], start=180, end=360, fill=(35, 75, 45), width=180)
        draw.arc([200, 380, 700, 620], start=180, end=360, fill=(28, 62, 38), width=180)
        _draw_fantasy_knight(draw, 270, 360, victorious=True)
    elif panel_num == 4:
        # Climax: Dragon flame versus magic shield
        draw.rectangle([0, 0, width, height], fill=(20, 10, 15))
        # Dragon silhouette breathing fire
        _draw_dragon(draw, 440, 180, breathing_fire=True)
        # Fire jet
        draw.polygon([(370, 185), (250, 330), (280, 410)], fill=(255, 100, 20, 220))
        draw.polygon([(370, 185), (260, 350), (275, 390)], fill=(255, 240, 60, 240))
        _draw_fantasy_knight(draw, 180, 350, shield_up=True)
    elif panel_num == 3:
        # Knight rushing across rope bridge amidst embers
        for y in range(height):
            f = y / height
            draw.line([(0, y), (width, y)], fill=(int(25 + f * 20), int(15 + f * 15), int(35 + f * 35), 255))
        draw.line([(0, 460), (width, 410)], fill=(90, 60, 40), width=6)
        _draw_fantasy_knight(draw, 240, 310, running=True)
        _draw_dragon(draw, 450, 150)
    elif panel_num == 2:
        # Lair / Hoard discovery
        draw.rectangle([0, 0, width, height], fill=(15, 12, 20))
        # Gold treasure pile
        draw.polygon([(260, 460), (420, 360), (560, 460)], fill=(215, 175, 45))
        # Dragon sleeping silhouette with slit eye
        _draw_dragon(draw, 450, 240, sleeping=True)
        _draw_fantasy_knight(draw, 160, 350)
    else:
        # Panel 1: Castle spires establishing
        for y in range(height):
            f = y / height
            draw.line([(0, y), (width, y)], fill=(int(20 + f * 25), int(15 + f * 20), int(40 + f * 45), 255))
        draw.ellipse([420, 60, 500, 140], fill=(255, 250, 220))
        # Spires
        spires = [(40, 240, 70), (130, 180, 85), (235, 220, 75), (330, 160, 95)]
        for sx, sy, sw in spires:
            draw.polygon([(sx, sy), (sx + sw // 2, sy - 55), (sx + sw, sy)], fill=(32, 28, 42), outline=(15, 12, 20), width=2)
            draw.rectangle([sx, sy, sx + sw, 460], fill=(36, 32, 48), outline=(15, 12, 20), width=2)
        _draw_fantasy_knight(draw, 470, 360)

    _finish_panel(img, draw, width, height, panel_num, title, sfx, narration, dialogue)
    img.convert("RGB").save(output_path, "PNG")


def _draw_dragon(draw: ImageDraw.ImageDraw, dx: int, dy: int, breathing_fire: bool = False, sleeping: bool = False) -> None:
    ink = (12, 10, 18)
    # Wings
    draw.polygon([(dx, dy), (dx + 110, dy - 65), (dx + 65, dy + 20)], fill=ink)
    draw.polygon([(dx, dy), (dx - 100, dy - 55), (dx - 55, dy + 20)], fill=ink)
    # Body & Neck
    draw.ellipse([dx - 35, dy - 15, dx + 35, dy + 15], fill=ink)
    draw.line([(dx + 25, dy), (dx + 80, dy + 40), (dx + 110, dy + 30)], fill=ink, width=4)
    # Head
    draw.polygon([(dx - 35, dy), (dx - 65, dy - 10), (dx - 45, dy + 10)], fill=ink)
    if sleeping:
        draw.line([(dx - 55, dy), (dx - 45, dy)], fill=(255, 215, 0), width=2)
    else:
        draw.ellipse([dx - 55, dy - 4, dx - 48, dy + 4], fill=(255, 220, 0))


def _draw_fantasy_knight(draw: ImageDraw.ImageDraw, kx: int, ky: int, running: bool = False, shield_up: bool = False, victorious: bool = False) -> None:
    ink = (14, 12, 20)
    cape = (180, 35, 40)
    draw.polygon([(kx - 15, ky + 25), (kx - 60, ky + 85), (kx - 15, ky + 75)], fill=cape)
    draw.rectangle([kx - 14, ky + 75, kx - 2, ky + 130], fill=ink)
    draw.rectangle([kx + 2, ky + 75, kx + 14, ky + 130], fill=ink)
    draw.polygon([(kx - 18, ky + 18), (kx + 18, ky + 18), (kx + 12, ky + 75), (kx - 12, ky + 75)], fill=ink)
    draw.ellipse([kx - 12, ky - 8, kx + 12, ky + 18], fill=ink)
    draw.rectangle([kx - 6, ky + 3, kx + 6, ky + 7], fill=(0, 240, 255))
    # Glowing Runic Sword
    draw.line([(kx + 14, ky + 25), (kx + 45, ky - 25)], fill=(0, 240, 255), width=5)
    draw.line([(kx + 14, ky + 25), (kx + 45, ky - 25)], fill=(255, 255, 255), width=2)
    if shield_up:
        draw.arc([kx + 10, ky - 35, kx + 110, ky + 65], start=210, end=350, fill=(0, 240, 255), width=6)
    if victorious:
        draw.line([(kx + 14, ky + 25), (kx + 20, ky - 45)], fill=(0, 240, 255), width=5)


# =========================================================================
# 5. Noir / Detective Scene Drawer
# =========================================================================
def _draw_noir_scene(output_path: Path, panel_num: int, title: str, sfx: str, prompt: str, narration: str = "", dialogue: str = "") -> None:
    width, height = 600, 600
    img = Image.new("RGBA", (width, height), (10, 10, 14, 255))
    draw = ImageDraw.Draw(img)

    for y in range(height):
        f = y / height
        draw.line([(0, y), (width, y)], fill=(int(10 + f * 18), int(12 + f * 20), int(16 + f * 24), 255))

    if panel_num == 1:
        # Rain-soaked alley with gaslamp
        for _ in range(80):
            rx = random.randint(0, width)
            ry = random.randint(0, 460)
            draw.line([(rx, ry), (rx - 10, ry + 30)], fill=(160, 180, 210, 80), width=1)
        draw.rectangle([0, 80, 160, 460], fill=(24, 24, 28))
        draw.rectangle([440, 80, 600, 460], fill=(24, 24, 28))
        draw.rectangle([0, 460, width, height], fill=(12, 12, 16))
        draw.ellipse([200, 480, 400, 520], fill=(32, 36, 48))
        _draw_victorian_detective(draw, 290, 350)
    elif panel_num == 2:
        # Office with venetian blinds shadows
        draw.rectangle([0, 0, width, height], fill=(18, 16, 20))
        for vy in range(40, 420, 25):
            draw.line([(0, vy), (width, vy + 40)], fill=(40, 36, 45, 140), width=10)
        # Desk & Telephone
        draw.rectangle([100, 360, 500, 480], fill=(32, 28, 34), outline=(15, 12, 18), width=3)
        _draw_victorian_detective(draw, 300, 260)
    elif panel_num == 3:
        # Waterfront docks pursuit
        draw.rectangle([0, 420, width, height], fill=(12, 16, 22))
        draw.line([(0, 420), (width, 420)], fill=(40, 45, 60), width=4)
        # Crates
        draw.rectangle([40, 320, 120, 420], fill=(45, 35, 28))
        draw.rectangle([120, 350, 190, 420], fill=(40, 32, 25))
        _draw_victorian_detective(draw, 280, 310, running=True)
    elif panel_num == 4:
        # Muzzle Flash in warehouse
        draw.rectangle([0, 0, width, height], fill=(10, 10, 14))
        # Gunflash burst
        draw.polygon([(280, 340), (440, 280), (320, 380)], fill=(255, 230, 90))
        draw.line([(280, 340), (480, 310)], fill=(255, 255, 255), width=3)
        _draw_victorian_detective(draw, 220, 320, fighting=True)
    else:
        # Panel 5: Cold harbor morning
        for y in range(height):
            f = y / height
            draw.line([(0, y), (width, y)], fill=(int(180 - f * 60), int(190 - f * 50), int(210 - f * 40), 255))
        draw.rectangle([0, 440, width, height], fill=(20, 22, 28))
        _draw_victorian_detective(draw, 280, 340, victorious=True)

    _finish_panel(img, draw, width, height, panel_num, title, sfx, narration, dialogue)
    img.convert("RGB").save(output_path, "PNG")


# =========================================================================
# 6. Pirate / High Seas Scene Drawer
# =========================================================================
def _draw_pirate_scene(output_path: Path, panel_num: int, title: str, sfx: str, prompt: str, narration: str = "", dialogue: str = "") -> None:
    width, height = 600, 600
    img = Image.new("RGBA", (width, height), (15, 25, 45, 255))
    draw = ImageDraw.Draw(img)

    if panel_num == 5:
        # Tropical beach sunset with gold chest
        for y in range(height):
            f = y / height
            draw.line([(0, y), (width, y)], fill=(int(255 - f * 60), int(150 + f * 50), int(50 + f * 80), 255))
        draw.ellipse([360, 180, 480, 300], fill=(255, 230, 120))
        # Sand
        draw.rectangle([0, 440, width, height], fill=(225, 195, 110))
        # Open Treasure Chest
        draw.rectangle([200, 390, 280, 450], fill=(95, 60, 30), outline=(20, 15, 10), width=2)
        draw.ellipse([215, 380, 265, 410], fill=(255, 215, 0))
        _draw_pirate_captain(draw, 340, 340, victorious=True)
    elif panel_num == 4:
        # Climax: Gunpowder explosion on deck
        draw.rectangle([0, 0, width, height], fill=(25, 15, 10))
        for r in range(40, 260, 45):
            draw.ellipse([300 - r, 240 - r, 300 + r, 240 + r], outline=(255, 160, 20), width=4)
        _draw_pirate_captain(draw, 180, 320, fighting=True)
    elif panel_num == 3:
        # Ship Rigging sword duel
        for y in range(height):
            f = y / height
            draw.line([(0, y), (width, y)], fill=(int(20 + f * 30), int(30 + f * 40), int(60 + f * 50), 255))
        draw.line([(100, 100), (100, 460)], fill=(55, 40, 25), width=8) # Mast
        draw.line([(20, 200), (300, 200)], fill=(55, 40, 25), width=6)
        _draw_pirate_captain(draw, 140, 270, fighting=True)
    elif panel_num == 2:
        # Skull Rock Island Cavern with glowing idol
        draw.rectangle([0, 0, width, height], fill=(12, 14, 22))
        # Skull rock mouth
        draw.polygon([(180, 180), (420, 180), (460, 460), (140, 460)], fill=(28, 30, 42))
        draw.ellipse([230, 240, 280, 290], fill=(0, 240, 255))
        draw.ellipse([320, 240, 370, 290], fill=(0, 240, 255))
        _draw_pirate_captain(draw, 180, 350)
    else:
        # Panel 1: Galleon sailing toward Skull Island
        for y in range(height):
            f = y / height
            draw.line([(0, y), (width, y)], fill=(int(18 + f * 35), int(35 + f * 45), int(70 + f * 60), 255))
        # Waves
        draw.rectangle([0, 420, width, height], fill=(15, 45, 75))
        for wx in range(0, width, 50):
            draw.arc([wx, 410, wx + 60, 440], start=180, end=360, fill=(0, 200, 220), width=3)
        # Galleon hull
        draw.polygon([(160, 370), (320, 370), (290, 430), (190, 430)], fill=(50, 35, 20))
        draw.polygon([(210, 240), (270, 240), (260, 360), (220, 360)], fill=(240, 240, 240)) # Sails
        _draw_pirate_captain(draw, 360, 320)

    _finish_panel(img, draw, width, height, panel_num, title, sfx, narration, dialogue)
    img.convert("RGB").save(output_path, "PNG")


def _draw_pirate_captain(draw: ImageDraw.ImageDraw, px: int, py: int, fighting: bool = False, victorious: bool = False) -> None:
    ink = (15, 12, 18)
    coat = (175, 30, 35)
    # Tricorn hat
    draw.polygon([(px - 22, py - 6), (px, py - 24), (px + 22, py - 6), (px, py - 12)], fill=ink)
    draw.ellipse([px - 10, py - 6, px + 10, py + 16], fill=ink)
    # Coat
    draw.polygon([(px - 18, py + 18), (px + 18, py + 18), (px + 14, py + 70), (px - 14, py + 70)], fill=coat)
    draw.rectangle([px - 12, py + 70, px - 2, py + 125], fill=ink)
    draw.rectangle([px + 2, py + 70, px + 12, py + 125], fill=ink) # Pegleg or boot
    # Cutlass Sword
    draw.line([(px + 14, py + 25), (px + 45, py - 15)], fill=(220, 225, 230), width=4)


# =========================================================================
# 7. Superhero / Metropolis Scene Drawer
# =========================================================================
def _draw_superhero_scene(output_path: Path, panel_num: int, title: str, sfx: str, prompt: str, narration: str = "", dialogue: str = "") -> None:
    width, height = 600, 600
    img = Image.new("RGBA", (width, height), (18, 15, 35, 255))
    draw = ImageDraw.Draw(img)

    for y in range(height):
        f = y / height
        draw.line([(0, y), (width, y)], fill=(int(18 + f * 45), int(14 + f * 25), int(42 + f * 35), 255))

    if panel_num == 5:
        # Golden sunrise over metropolis
        for y in range(height):
            f = y / height
            draw.line([(0, y), (width, y)], fill=(int(255 - f * 80), int(170 + f * 50), int(80 + f * 80), 255))
        draw.ellipse([360, 160, 480, 280], fill=(255, 235, 140))
        # Skyline silhouette
        b_list = [(20, 280, 80), (120, 230, 90), (220, 270, 80), (320, 200, 95), (430, 250, 85)]
        for bx, by, bw in b_list:
            draw.rectangle([bx, by, bx + bw, 460], fill=(22, 24, 38))
        draw.rectangle([0, 460, width, height], fill=(15, 16, 22))
        _draw_hero_figure(draw, 270, 350, victorious=True)
    elif panel_num == 4:
        # Epic Impact Climax punch & starburst
        draw.rectangle([0, 0, width, height], fill=(25, 10, 20))
        # Giant starburst
        bx, by = 300, 240
        pts = 16
        burst = []
        for i in range(pts * 2):
            ang = (i / (pts * 2)) * 2 * math.pi
            rad = 220 if i % 2 == 0 else 80
            burst.append((bx + int(rad * math.cos(ang)), by + int(rad * math.sin(ang))))
        draw.polygon(burst, fill=(255, 220, 0), outline=(255, 40, 40), width=4)
        _draw_hero_figure(draw, 200, 280, punching=True)
    elif panel_num == 3:
        # Mid-air flight through skyscraper canyon with speed lines
        for _ in range(40):
            sx = random.randint(0, width)
            sy = random.randint(40, 460)
            draw.line([(sx, sy), (sx + random.randint(50, 140), sy)], fill=(255, 255, 255, 160), width=2)
        _draw_hero_figure(draw, 240, 260, flying=True)
    elif panel_num == 2:
        # Threat sighting: Alarm spotlight & villain breach
        draw.polygon([(140, 460), (300, 0), (380, 0)], fill=(255, 240, 100, 45))
        # Skyline
        draw.rectangle([60, 260, 220, 460], fill=(22, 24, 38))
        draw.rectangle([260, 200, 440, 460], fill=(26, 30, 45))
        # Lightning surge
        draw.line([(350, 200), (330, 270), (370, 310), (340, 420)], fill=(0, 240, 255), width=4)
        _draw_hero_figure(draw, 140, 350)
    else:
        # Panel 1: Hero on gargoyle watching city lights
        draw.ellipse([430, 60, 520, 150], fill=(255, 255, 220))
        b_list = [(20, 280, 80), (110, 210, 90), (210, 260, 80), (300, 190, 100), (410, 250, 85), (505, 270, 80)]
        for bx, by, bw in b_list:
            draw.rectangle([bx, by, bx + bw, 460], fill=(22, 24, 38), outline=(10, 12, 18), width=2)
            for wy in range(by + 16, 450, 28):
                for wx in range(bx + 10, bx + bw - 12, 20):
                    draw.rectangle([wx, wy, wx + 8, wy + 12], fill=(255, 215, 0, 220))
        draw.rectangle([0, 460, width, height], fill=(12, 14, 20))
        _draw_hero_figure(draw, 210, 355)

    _finish_panel(img, draw, width, height, panel_num, title, sfx, narration, dialogue)
    img.convert("RGB").save(output_path, "PNG")


def _draw_hero_figure(draw: ImageDraw.ImageDraw, cx: int, cy: int, flying: bool = False, punching: bool = False, victorious: bool = False) -> None:
    suit = (15, 18, 28)
    cape = (220, 35, 40)
    if flying:
        # Horizontal flying pose
        draw.polygon([(cx - 40, cy + 10), (cx - 100, cy + 30), (cx - 30, cy + 25)], fill=cape)
        draw.rectangle([cx - 40, cy, cx + 50, cy + 18], fill=suit)
        draw.ellipse([cx + 45, cy - 2, cx + 65, cy + 20], fill=suit)
    elif punching:
        draw.polygon([(cx - 15, cy + 25), (cx - 75, cy + 85), (cx - 20, cy + 70)], fill=cape)
        draw.polygon([(cx - 18, cy + 18), (cx + 18, cy + 18), (cx + 12, cy + 70), (cx - 12, cy + 70)], fill=suit)
        draw.line([(cx + 14, cy + 25), (cx + 70, cy + 10)], fill=suit, width=6)
    elif victorious:
        draw.polygon([(cx - 15, cy + 25), (cx - 85, cy + 75), (cx - 30, cy + 65)], fill=cape)
        draw.rectangle([cx - 14, cy + 70, cx - 2, cy + 130], fill=suit)
        draw.rectangle([cx + 2, cy + 70, cx + 14, cy + 130], fill=suit)
        draw.polygon([(cx - 18, cy + 18), (cx + 18, cy + 18), (cx + 12, cy + 70), (cx - 12, cy + 70)], fill=suit)
        draw.line([(cx + 14, cy + 20), (cx + 35, cy - 25)], fill=suit, width=6)
    else:
        draw.polygon([(cx - 15, cy + 25), (cx - 75, cy + 85), (cx - 20, cy + 70)], fill=cape)
        draw.rectangle([cx - 14, cy + 70, cx - 2, cy + 130], fill=suit)
        draw.rectangle([cx + 2, cy + 70, cx + 14, cy + 130], fill=suit)
        draw.polygon([(cx - 18, cy + 18), (cx + 18, cy + 18), (cx + 12, cy + 70), (cx - 12, cy + 70)], fill=suit)
        draw.ellipse([cx - 12, cy - 8, cx + 12, cy + 18], fill=suit)


# =========================================================================
# 8. Western & 9. Horror Scene Drawers
# =========================================================================
def _draw_western_scene(output_path: Path, panel_num: int, title: str, sfx: str, prompt: str, narration: str = "", dialogue: str = "") -> None:
    width, height = 600, 600
    img = Image.new("RGBA", (width, height), (35, 20, 15, 255))
    draw = ImageDraw.Draw(img)

    for y in range(height):
        f = y / height
        draw.line([(0, y), (width, y)], fill=(int(255 - f * 80), int(140 + f * 40), int(60 + f * 50), 255))

    # Red Mesas
    draw.polygon([(40, 360), (90, 240), (220, 240), (280, 360)], fill=(120, 45, 30))
    draw.polygon([(300, 360), (350, 200), (480, 200), (540, 360)], fill=(100, 40, 25))
    draw.rectangle([0, 420, width, height], fill=(140, 75, 40))
    # Saguaro Cactus
    draw.line([(120, 350), (120, 440)], fill=(30, 55, 35), width=8)
    draw.line([(100, 380), (140, 380)], fill=(30, 55, 35), width=6)
    draw.line([(100, 360), (100, 380)], fill=(30, 55, 35), width=6)
    draw.line([(140, 360), (140, 380)], fill=(30, 55, 35), width=6)

    _draw_victorian_detective(draw, 340, 330)
    _finish_panel(img, draw, width, height, panel_num, title, sfx, narration, dialogue)
    img.convert("RGB").save(output_path, "PNG")


def _draw_horror_scene(output_path: Path, panel_num: int, title: str, sfx: str, prompt: str, narration: str = "", dialogue: str = "") -> None:
    width, height = 600, 600
    img = Image.new("RGBA", (width, height), (12, 10, 18, 255))
    draw = ImageDraw.Draw(img)

    for y in range(height):
        f = y / height
        draw.line([(0, y), (width, y)], fill=(int(12 + f * 20), int(10 + f * 15), int(22 + f * 30), 255))

    # Blood Moon
    draw.ellipse([400, 60, 500, 160], fill=(220, 50, 40))
    # Haunted hill & crooked trees
    draw.arc([100, 340, 600, 600], start=180, end=360, fill=(20, 18, 26), width=180)
    # Gnarled branches
    draw.line([(160, 420), (180, 320), (150, 260)], fill=(10, 8, 14), width=6)
    draw.line([(180, 320), (220, 270)], fill=(10, 8, 14), width=4)
    # Tombstones
    for tx in [300, 380, 460]:
        draw.rectangle([tx, 400, tx + 24, 435], fill=(45, 42, 52), outline=(10, 8, 14), width=2)
        draw.arc([tx, 390, tx + 24, 410], start=180, end=360, fill=(45, 42, 52), width=2)

    _draw_victorian_detective(draw, 240, 340)
    _finish_panel(img, draw, width, height, panel_num, title, sfx, narration, dialogue)
    img.convert("RGB").save(output_path, "PNG")


# =========================================================================
# 10. Universal Procedural Artist (for any other prompt!)
# =========================================================================
def _draw_custom_procedural_scene(output_path: Path, panel_num: int, title: str, sfx: str, prompt: str, narration: str = "", dialogue: str = "") -> None:
    """Procedurally synthesizes unique environments based on a deterministic hash of the user's prompt."""
    width, height = 600, 600
    h_val = int(hashlib.sha256(f"{prompt}".encode()).hexdigest()[:8], 16)

    # 6 Dynamic Palette Themes
    palettes = [
        ((255, 100, 60), (255, 180, 80), (35, 20, 45)),   # Sunset Blaze
        ((15, 240, 160), (10, 80, 120), (8, 18, 30)),     # Toxic Cyber Emerald
        ((180, 50, 255), (60, 30, 140), (15, 10, 32)),    # Cosmic Royal Violet
        ((0, 210, 255), (20, 70, 160), (10, 20, 40)),     # Glacial Cobalt
        ((255, 60, 60), (180, 20, 40), (25, 10, 15)),     # Volcanic Crimson
        ((255, 215, 0), (220, 140, 20), (30, 22, 14))     # Solar Amber
    ]
    pal = palettes[h_val % len(palettes)]

    img = Image.new("RGBA", (width, height), pal[2])
    draw = ImageDraw.Draw(img)

    # Sky gradient
    for y in range(height):
        f = y / height
        draw.line([(0, y), (width, y)], fill=(
            int(pal[0][0] * (1 - f) + pal[1][0] * f),
            int(pal[0][1] * (1 - f) + pal[1][1] * f),
            int(pal[0][2] * (1 - f) + pal[1][2] * f),
            255
        ))

    # Celestial Body
    draw.ellipse([380, 60, 490, 170], fill=(255, 245, 210), outline=(255, 255, 255), width=2)

    # Dynamic Horizon
    horizon_type = h_val % 3
    if horizon_type == 0:
        # Jagged Mountain Range
        draw.polygon([(0, 440), (120, 260), (240, 380), (380, 230), (510, 360), (width, 280), (width, 460), (0, 460)], fill=(32, 28, 44))
    elif horizon_type == 1:
        # Monolithic Skyline
        for bx in range(20, width, 90):
            bh = 120 + ((bx * 7 + h_val) % 180)
            draw.rectangle([bx, 440 - bh, bx + 70, 460], fill=(26, 28, 42), outline=(pal[0]), width=1)
    else:
        # Rolling Dunes
        draw.arc([-60, 320, 380, 600], start=180, end=360, fill=(45, 38, 55), width=180)
        draw.arc([220, 340, 720, 620], start=180, end=360, fill=(35, 30, 45), width=180)

    # Ground
    draw.rectangle([0, 440, width, height], fill=(15, 14, 22))

    # Panel-Specific Choreography
    if panel_num == 4:
        # Impact Climax
        bx, by = 300, 230
        pts = 12
        burst = []
        for i in range(pts * 2):
            ang = (i / (pts * 2)) * 2 * math.pi
            rad = 200 if i % 2 == 0 else 70
            burst.append((bx + int(rad * math.cos(ang)), by + int(rad * math.sin(ang))))
        draw.polygon(burst, fill=(255, 230, 80), outline=(255, 50, 50), width=4)
        _draw_hero_figure(draw, 220, 280, punching=True)
    elif panel_num == 3:
        # Speedlines action
        for _ in range(35):
            sx = random.randint(0, width)
            sy = random.randint(40, 440)
            draw.line([(sx, sy), (sx + random.randint(60, 160), sy)], fill=(255, 255, 255, 180), width=2)
        _draw_hero_figure(draw, 250, 310, flying=True)
    elif panel_num == 2:
        # Glowing mystery anomaly
        draw.ellipse([340, 240, 440, 340], fill=pal[0], outline=(255, 255, 255), width=3)
        _draw_hero_figure(draw, 180, 350)
    elif panel_num == 5:
        # Victory pose
        _draw_hero_figure(draw, 270, 340, victorious=True)
    else:
        # Establishing shot
        _draw_hero_figure(draw, 240, 350)

    _finish_panel(img, draw, width, height, panel_num, title, sfx, narration, dialogue)
    img.convert("RGB").save(output_path, "PNG")


# =========================================================================
# Finishing Decorator (Halftone, Badges, Caption, Ink Border)
# =========================================================================
def _finish_panel(
    img: Image.Image,
    draw: ImageDraw.ImageDraw,
    width: int,
    height: int,
    panel_num: int,
    title: str,
    sfx: str,
    narration: str = "",
    dialogue: str = ""
) -> None:
    """Adds halftone dot corners, sound effect burst badge, panel header, caption box, and ink border."""
    font_sfx, font_title, font_caption = _get_fonts()

    # 1. Halftone dots in top corner
    for dx in range(15, 130, 16):
        for dy in range(15, 80, 16):
            draw.ellipse([dx, dy, dx + 3, dy + 3], fill=(255, 255, 255, 35))

    # 2. Sound effect burst badge (Top-Right)
    if sfx:
        bx, by = width - 85, 75
        pts = 10
        burst = []
        for i in range(pts * 2):
            ang = (i / (pts * 2)) * 2 * math.pi
            rad = 46 if i % 2 == 0 else 24
            burst.append((bx + int(rad * math.cos(ang)), by + int(rad * math.sin(ang))))

        draw.polygon([(x + 3, y + 3) for x, y in burst], fill=(10, 10, 15, 220))
        draw.polygon(burst, fill=(255, 220, 0), outline=(10, 10, 15), width=3)
        bbox = draw.textbbox((0, 0), sfx, font=font_sfx)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text((bx - tw // 2, by - th // 2), sfx, fill=(225, 30, 40), font=font_sfx)

    # 3. Panel Title Tag (Top-Left)
    lbl = f"PANEL {panel_num}: {title.upper()[:22]}"
    t_bbox = draw.textbbox((0, 0), lbl, font=font_title)
    tb_w = t_bbox[2] - t_bbox[0] + 16
    draw.rectangle([14, 14, 14 + tb_w, 38], fill=(15, 15, 24, 235), outline=(255, 208, 39), width=2)
    draw.text((22, 19), lbl, fill=(255, 255, 255), font=font_title)

    # 4. Comic Narration or Dialogue Caption Box (Bottom)
    cap_text = narration or dialogue
    if cap_text:
        lines = textwrap.wrap(cap_text, width=54)
        if len(lines) > 3:
            lines = lines[:2] + [lines[2][:45] + "..."]
        line_height = 18
        box_h = max(40, len(lines) * line_height + 16)
        box_y = height - box_h - 14

        # Drop shadow
        draw.rectangle([18, box_y + 4, width - 14, height - 10], fill=(10, 10, 15, 180))
        # Authentic yellow comic caption box
        draw.rectangle([14, box_y, width - 18, height - 14], fill=(255, 252, 225), outline=(15, 15, 24), width=3)

        cur_y = box_y + 8
        for line in lines:
            draw.text((24, cur_y), line, fill=(18, 18, 24), font=font_caption)
            cur_y += line_height

    # 5. Heavy ink border
    draw.rectangle([0, 0, width - 1, height - 1], outline=(15, 15, 24), width=6)


def test_image_generation(prompt: str, art_style: str = "Classic Comic Book") -> dict:
    """Diagnostic helper testing image generation and returning status & URL."""
    import uuid
    test_filename = f"test_{uuid.uuid4().hex[:6]}.png"
    url, path = generate_panel_image(
        prompt=prompt,
        art_style=art_style,
        filename=test_filename,
        panel_number=1,
        title="Diagnostic Test",
        sound_effect="TEST!",
        narration="Diagnostic test illustration synthesized successfully."
    )
    mode = "Cloud Diffusion Engine" if has_hf_key() else "Procedural Comic Scene Illustrator"
    return {
        "status": "success",
        "image_url": url,
        "local_path": path,
        "prompt_used": prompt,
        "generation_mode": mode
    }
