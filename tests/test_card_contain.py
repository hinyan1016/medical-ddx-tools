import io
import sys
from pathlib import Path
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from card_webp import card_bytes

def test_contain_preserves_footer_that_cover_crops(tmp_path):
    src = tmp_path / "source.png"
    im = Image.new("RGB", (600, 600), "white")
    im.paste("red", (0, 560, 600, 600))
    im.save(src)
    cover = Image.open(io.BytesIO(card_bytes(src)))
    contained = Image.open(io.BytesIO(card_bytes(src, fit="contain")))
    assert contained.size == (800, 450)
    assert contained.getpixel((400, 430))[0] > 200
    assert contained.getpixel((400, 430))[1] < 80
    assert cover.getpixel((300, cover.height-5))[1] > 200
    assert contained.getpixel((10, 200))[1] > 200

def test_default_is_existing_cover(tmp_path):
    src = tmp_path / "source.png"
    Image.new("RGB", (900, 1200), "blue").save(src)
    assert card_bytes(src) == card_bytes(src, fit="cover")
