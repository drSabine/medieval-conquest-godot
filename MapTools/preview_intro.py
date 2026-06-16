"""Render the character-intro splash for both heroes using the real idle sprites."""
import os, textwrap
from PIL import Image, ImageDraw, ImageFont

W, H = 1366, 768
FONT_DIR = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")

def font(sz, bold=True):
    for n in (("georgiab.ttf" if bold else "georgia.ttf"), "arialbd.ttf", "arial.ttf"):
        p = os.path.join(FONT_DIR, n)
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, sz)
            except OSError:
                pass
    return ImageFont.load_default()

def first_frame(path, fw, fh):
    im = Image.open(path).convert("RGBA").crop((0, 0, fw, fh))
    bb = im.getbbox()
    return im.crop(bb) if bb else im

def render(sheet, fw, fh, scale, line, out):
    img = Image.new("RGBA", (W, H), (9, 9, 13, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([W // 2 - 260, H // 2 - 240, W // 2 + 260, H // 2 + 60], fill=(18, 18, 26, 255))
    spr = first_frame(sheet, fw, fh)
    spr = spr.resize((int(spr.width * scale), int(spr.height * scale)), Image.NEAREST)
    img.alpha_composite(spr, (683 - spr.width // 2, 340 - spr.height // 2))
    f = font(40)
    y = H // 2 + 150
    for ln in textwrap.wrap(line, width=42):
        bb = d.textbbox((0, 0), ln, font=f); tw = bb[2] - bb[0]
        x = (W - tw) // 2
        for ox, oy in [(-3, 0), (3, 0), (0, -3), (0, 3)]:
            d.text((x + ox, y + oy), ln, font=f, fill=(0, 0, 0, 255))
        d.text((x, y), ln, font=f, fill=(224, 194, 110, 255))
        y += 54
    fh2 = font(16, bold=False)
    hint = "Press any key to continue"
    bb = d.textbbox((0, 0), hint, font=fh2); tw = bb[2] - bb[0]
    d.text(((W - tw) // 2, H - 46), hint, font=fh2, fill=(150, 150, 165, 220))
    img.convert("RGB").resize((820, 461)).save(out)
    print("saved", out)

if __name__ == "__main__":
    os.makedirs("preview", exist_ok=True)
    render("../Assets/PlayerAssets/Medieval King Pack 2/Sprites/Idle.png", 160, 111, 4.0,
           "You Have Chosen the Almighty Medieval Knight, Lion of the West!",
           "preview/intro_knight.png")
    render("../Assets/PlayerAssets/Huntress/Idle.png", 150, 150, 3.2,
           "You Have Chosen the Huntress of Saxony, Ranger of the Northern Forest.",
           "preview/intro_huntress.png")
