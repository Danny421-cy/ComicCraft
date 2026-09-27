import os
from PIL import Image
from app.image_generator import generate_panel_image, test_image_generation as run_image_diagnostic

def test_generate_panel_image():
    """TC-08: Verify image generation outputs a valid 600x600 PNG image."""
    test_file = "test_case_panel_1.png"
    web_url, local_path = generate_panel_image(
        prompt="A brave knight stands before a crystal dragon",
        art_style="Classic Comic Book",
        filename=test_file,
        panel_number=1,
        title="Dragon Lair",
        sound_effect="ROAR!"
    )

    assert os.path.exists(local_path)
    assert web_url.startswith("/static/panels/")
    
    with Image.open(local_path) as img:
        assert img.format == "PNG"
        assert img.size == (600, 600)

def test_art_style_themes():
    """TC-09: Verify generation under different comic styles."""
    styles = ["Classic Comic Book", "Dark Cyberpunk", "Manga / Anime", "Vintage Pop Art"]
    for s in styles:
        fname = f"test_style_{s.replace(' ', '_').replace('/', '')}.png"
        url, path = generate_panel_image(
            prompt="Dramatic character silhouette",
            art_style=s,
            filename=fname,
            panel_number=2,
            title="Style Test",
            sound_effect="KRAK!"
        )
        assert os.path.exists(path)

def test_diagnostic_helper():
    """TC-16: Verify test_image_generation diagnostic tool."""
    res = run_image_diagnostic(prompt="Futuristic hovercar race", art_style="Dark Cyberpunk")
    assert res["status"] == "success"
    assert "image_url" in res
    assert os.path.exists(res["local_path"])

