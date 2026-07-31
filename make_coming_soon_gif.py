from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, random

W, H = 600, 900
SCALE = 2
SW, SH = W * SCALE, H * SCALE
FPS = 24
DURATION = int(1000 / FPS)

BG = (5, 4, 3, 255)                 # near-black warm
AMBER = (230, 160, 60)
GOLD = (255, 198, 92)
COPPER = (160, 99, 19)
DIM = (90, 70, 45)
TEXT = (240, 224, 198)
MUT = (120, 100, 75)

NAME_FONT = r"C:\Windows\Fonts\seguisb.ttf"
MONO_FONT = r"C:\Windows\Fonts\consolab.ttf"

LOGO = r"C:\Users\RAMZI\AppData\Local\Temp\opencode\boostUP-showcase\logo.png"

def font(path, size):
    return ImageFont.truetype(path, size)

def clamp255(v):
    return max(0, min(255, int(v)))

def lerp_color(c1, c2, t):
    return tuple(clamp255(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def draw_radial_glow(img, cx, cy, r, color, strength=80):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(r, 0, -8):
        a = int(strength * (1 - i / r) ** 2)
        d.ellipse([cx - i, cy - i, cx + i, cy + i], fill=color + (a,))
    layer = layer.filter(ImageFilter.GaussianBlur(20 * SCALE))
    img.alpha_composite(layer)

def draw_logo_watermark(img, t):
    logo = Image.open(LOGO).convert("RGBA")
    logo = logo.resize((int(340 * SCALE), int(340 * SCALE)), Image.LANCZOS)
    # tint dark
    tint = Image.new("RGBA", logo.size, (40, 30, 12, 255))
    logo = Image.alpha_composite(logo, tint)
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    cx = (SW - logo.width) // 2
    cy = int(230 * SCALE)
    # fade in and out subtly
    a = 0.7 + 0.3 * math.sin(t * 1.1)
    alpha = logo.getchannel("A").point(lambda p: int(p * min(1, max(0, a))))
    logo.putalpha(alpha)
    layer.paste(logo, (cx, cy), logo)
    img.alpha_composite(layer)

def draw_frame(img, t, d):
    # --- background ---
    draw_radial_glow(img, SW // 2, int(400 * SCALE), int(320 * SCALE), (150, 95, 25), 70)

    # --- subtle grid ---
    step = 40 * SCALE
    for gx in range(0, SW, step):
        d.line([gx, 0, gx, SH], fill=(70, 55, 30, 22))
    for gy in range(0, SH, step):
        d.line([0, gy, SW, gy], fill=(70, 55, 30, 18))

    # --- watermark logo ---
    draw_logo_watermark(img, t)

    # --- top bar ---
    mf = font(MONO_FONT, int(13 * SCALE))
    d.text((30 * SCALE, 34 * SCALE), "BOOSTUP  v2.1.0", font=mf, fill=MUT)

    # --- pulsing corner brackets ---
    cb = 26 * SCALE
    pul = 120 + 60 * math.sin(t * 2.4)
    ccol = AMBER + (int(pul),)
    for cx, cy, sx, sy in [(18 * SCALE, 18 * SCALE, 1, 1),
                           (SW - 18 * SCALE, 18 * SCALE, -1, 1),
                           (18 * SCALE, SH - 18 * SCALE, 1, -1),
                           (SW - 18 * SCALE, SH - 18 * SCALE, -1, -1)]:
        d.line([cx, cy, cx + cb * sx, cy], fill=ccol, width=2 * SCALE)
        d.line([cx, cy, cx, cy + cb * sy], fill=ccol, width=2 * SCALE)

    # --- headline ---
    hf = font(NAME_FONT, int(44 * SCALE))
    words = "COMING SOON"
    x = (SW - d.textlength(words, font=hf)) // 2
    y = int(620 * SCALE)
    # glow
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.text((x, y), words, font=hf, fill=AMBER + (int(90 + 60 * math.sin(t * 2)),))
    glow = glow.filter(ImageFilter.GaussianBlur(10 * SCALE))
    img.alpha_composite(glow)
    # per-letter reveal + shimmer
    xpos = x
    for i, ch in enumerate(words):
        ph = ((t - i * 0.06) % 1.4) / 1.4
        if ph < 0.2:
            a = int(255 * (ph / 0.2))
        else:
            a = 255
        col = lerp_color(GOLD, AMBER, (math.sin(t * 1.6 + i) + 1) / 2)
        d.text((xpos, y), ch, font=hf, fill=col + (a,))
        xpos += d.textlength(ch, font=hf)

    # --- subtitle ---
    sf = font(NAME_FONT, int(17 * SCALE))
    sub = "Desktop-grade PC optimization for gamers"
    sx = (SW - d.textlength(sub, font=sf)) // 2
    d.text((sx, y + int(72 * SCALE)), sub, font=sf, fill=TEXT)

    # --- boot log (center) ---
    lines = [
        "\u279c  initializing core modules",
        "\u279c  loading optimizer engine",
        "\u279c  calibrating network routing",
    ]
    for li, ln in enumerate(lines):
        appear_at = 0.4 + li * 0.5
        lt = t - appear_at
        if lt < 0:
            continue
        nch = min(len(ln), int(lt * 22))
        shown = ln[:nch]
        ly = int(270 * SCALE) + li * 26 * SCALE
        d.text((110 * SCALE, ly), shown, font=mf, fill=GOLD)
        if nch < len(ln) and int(t * 3) % 2 == 0:
            d.text((110 * SCALE + d.textlength(shown, font=mf), ly), "_", font=mf, fill=GOLD)
        # status tick
        if lt > 1.0:
            d.text((640 * SCALE, ly), "[ OK ]", font=mf, fill=GOLD)

    # --- progress bar ---
    pw = 420 * SCALE
    px, py = int(90 * SCALE), int(540 * SCALE)
    d.rounded_rectangle([px, py, px + pw, py + 12 * SCALE], radius=6 * SCALE, fill=(30, 24, 14, 255))
    prog = min(0.92, (t * 0.30) / 1.0) * (1 / 0.92) if t < 3.2 else 0.92
    prog = min(0.92, max(0, t * 0.30)) if t < 3.05 else 0.92
    w = int(pw * (prog / 0.92))
    d.rounded_rectangle([px, py, px + w, py + 12 * SCALE], radius=6 * SCALE, fill=AMBER)
    # sheen
    sheen_x = px + ((t * 1.5 * pw) % (pw + 40 * SCALE)) - 20 * SCALE
    d.rounded_rectangle([sheen_x, py, sheen_x + 36 * SCALE, py + 12 * SCALE], radius=6 * SCALE,
                        fill=(255, 225, 160, 160))
    d.text((px + pw + 18 * SCALE, py - 3 * SCALE), f"{int(prog * 100)}%", font=mf, fill=GOLD)

    # --- URL ---
    uf = font(MONO_FONT, int(15 * SCALE))
    url = "myboostup.netlify.app"
    ux = (SW - d.textlength(url, font=uf)) // 2
    uy = int(720 * SCALE)
    d.text((ux, uy), url, font=uf, fill=TEXT)
    if int(t * 2.4) % 2 == 0:
        d.text((ux + d.textlength(url, font=uf) + 6 * SCALE, uy), "_", font=uf, fill=GOLD)

    # --- scanline ---
    sy = int(((t * 160 * SCALE) % (SH + 160 * SCALE)) - 80 * SCALE)
    scan = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(scan)
    h = 60 * SCALE
    for i in range(h):
        a = int(7 * math.exp(-i / (h * 0.3)))
        sd.line([16 * SCALE, sy + i, SW - 16 * SCALE, sy + i], fill=GOLD + (a,))
    img.alpha_composite(scan)

    # --- particles ---
    prng = random.Random(13)
    for i in range(20):
        pxp = (prng.random() * SW, ((prng.random() * SH) - (t * 22 * SCALE) % SH) % SH)
        a = int(30 + 60 * math.sin(t * 2.2 + i))
        r = int(SCALE * (1.5 + (i % 3)))
        d.ellipse([pxp[0], pxp[1], pxp[0] + r, pxp[1] + r], fill=GOLD + (a,))

def main():
    total = int(4.0 * FPS)
    frames = []
    for i in range(total):
        t = i / FPS
        img = Image.new("RGBA", (SW, SH), BG)
        d = ImageDraw.Draw(img)
        draw_frame(img, t, d)
        down = img.resize((W, H), Image.LANCZOS).convert("P", palette=Image.ADAPTIVE, colors=255)
        frames.append(down)

    out = r"C:\Users\RAMZI\AppData\Local\Temp\opencode\boostUP-showcase\coming-soon.gif"
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=DURATION, loop=0, optimize=True)
    print("wrote", out, "frames:", len(frames))

if __name__ == "__main__":
    main()
