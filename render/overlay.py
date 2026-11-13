"""Frame overlays: one consistent typographic layout for every simulation clip.

Layout (margins scale with the frame's short side; designed at 1080 px):

    SIMULATED TIME                        ● Galaxy A
    0.26 billion years                    ● Galaxy B



    20 kpc  65,000 light-years                     N-BODY SIMULATION
    |———————|                                5,000 particles · stars shown

The time is read from the snapshot.  Numbers use Inter's tabular figures so the readout
does not jitter as digits change.  The scale bar keeps a fixed label for the whole clip
and its length follows the camera smoothly.  Soft scrims behind the text keep it legible
over bright galaxy light.
"""
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT_DIR = Path("/usr/share/fonts/opentype/inter")
KPC_LY = 3261.56

PRIMARY = (238, 241, 247)
SECONDARY = (150, 160, 180)
TERTIARY = (108, 117, 136)


@lru_cache(maxsize=64)
def font(weight, size, display=False):
    name = f"{'InterDisplay' if display else 'Inter'}-{weight}.otf"
    p = FONT_DIR / name
    if not p.exists():
        p = FONT_DIR / "Inter-Regular.otf"
    try:
        return ImageFont.truetype(str(p), max(6, int(round(size))), layout_engine=ImageFont.Layout.RAQM)
    except Exception:
        return ImageFont.load_default()


def _features():
    from PIL import features
    return ["tnum"] if features.check("raqm") else None


TNUM = _features()


def tracked(draw, xy, text, fnt, fill, tracking, anchor="ls"):
    """Draw letter-spaced text (for small-caps labels).  Returns the drawn width."""
    widths = [fnt.getlength(c) for c in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x, y = xy
    if anchor[0] == "r":
        x -= total
    for c, w in zip(text, widths):
        draw.text((x, y), c, font=fnt, fill=fill, anchor="l" + anchor[1])
        x += w + tracking
    return total


@lru_cache(maxsize=8)
def scrims(W, H, bg, strength):
    """Vertical darkening gradients behind the top and bottom text bands (RGBA)."""
    u = min(W, H) / 1080.0
    a = np.zeros(H, np.float32)
    y = np.arange(H, dtype=np.float32)
    top = np.clip(1 - y / (300 * u), 0, 1) ** 2
    bot = np.clip(1 - (H - y) / (240 * u), 0, 1) ** 2
    a = np.maximum(top, bot) * strength
    rgba = np.zeros((H, W, 4), np.uint8)
    rgba[..., :3] = bg
    rgba[..., 3] = (a * 255 + 0.5).astype(np.uint8)[:, None]
    return Image.fromarray(rgba, "RGBA")


def nice_ly(kpc):
    """Light-years to two significant figures, e.g. 20 kpc -> '65,000'."""
    return f"{int(float(f'{kpc * KPC_LY:.2g}')):,}"


def draw_overlay(im, cfg, t_gyr, kpc_per_px, galaxy_colors, galaxy_names, frame, n_particles):
    """Draw the overlay onto ``im`` (PIL RGB image, final resolution)."""
    ov = cfg or {}
    W, H = im.size
    u = min(W, H) / 1080.0
    M = float(ov.get("margin", 64)) * u
    alpha = 1.0
    fade = int(ov.get("fade_in_frames", 0))
    if fade > 0:
        x = min(1.0, frame / fade)
        alpha = x * x * (3 - 2 * x)
    if alpha <= 0:
        return im
    bg = tuple(int(c) for c in ov.get("_bg", (7, 9, 15)))
    base = im.convert("RGBA")
    if ov.get("scrim", True):
        base = Image.alpha_composite(base, scrims(W, H, bg, float(ov.get("scrim_strength", 0.55))))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    A = int(255 * alpha)
    P, S, T = PRIMARY + (A,), SECONDARY + (A,), TERTIARY + (A,)

    # --- simulated time (top left) -------------------------------------------------
    tc = ov.get("time", {})
    if tc is not False:
        label = tc.get("label", "SIMULATED TIME")
        unit = tc.get("unit", "billion years")
        dec = int(tc.get("decimals", 2))
        val = t_gyr + float(tc.get("offset_gyr", 0.0))
        y_label = M + 18 * u
        tracked(d, (M, y_label), label, font("Medium", 19 * u), S, 2.2 * u)
        fbig = font("SemiBold", 66 * u, display=True)
        num = f"{val:.{dec}f}"
        y_num = y_label + 76 * u
        d.text((M - 3 * u, y_num), num, font=fbig, fill=P, anchor="ls", features=TNUM)
        nw = d.textlength(num, font=fbig, features=TNUM)
        d.text((M + nw + 12 * u, y_num), unit, font=font("Regular", 28 * u), fill=S, anchor="ls")

    # --- panel title (top right; replaces the legend when given) --------------------
    pt = ov.get("title")
    if pt:
        tracked(d, (W - M, M + 18 * u), pt["text"], font("SemiBold", 21 * u), P, 2.2 * u, anchor="rs")
        if pt.get("sub"):
            d.text((W - M, M + 50 * u), pt["sub"], font=font("Regular", 21 * u), fill=S, anchor="rs")

    # --- legend (top right) --------------------------------------------------------
    lg = ov.get("legend", True) if not pt else False
    if lg:
        entries = lg if isinstance(lg, list) else [{"name": n, "galaxy": i} for i, n in enumerate(galaxy_names)]
        f = font("Medium", 24 * u)
        for i, e in enumerate(entries):
            y = M + 18 * u + i * 40 * u
            tw = d.textlength(e["name"], font=f)
            d.text((W - M, y), e["name"], font=f, fill=P, anchor="rs")
            col = tuple(int(255 * c) for c in galaxy_colors[int(e["galaxy"])]) + (A,)
            cx, cy, r = W - M - tw - 18 * u, y - 8 * u, 7 * u
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)

    # --- scale bar (bottom left) ----------------------------------------------------
    sb = ov.get("scale_bar", {})
    if sb is not False:
        kpc = float(sb.get("kpc", 20))
        L = kpc / kpc_per_px
        yb = H - M - 4 * u
        lw = max(1, int(round(2 * u)))
        d.line([(M, yb), (M + L, yb)], fill=P, width=lw)
        for xx in (M, M + L):
            d.line([(xx, yb - 9 * u), (xx, yb + 1 * u)], fill=P, width=lw)
        f1 = font("Medium", 23 * u)
        lab = f"{kpc:g} kpc"
        d.text((M, yb - 22 * u), lab, font=f1, fill=P, anchor="ls")
        if sb.get("light_years", True):
            w1 = d.textlength(lab, font=f1)
            d.text((M + w1 + 12 * u, yb - 22 * u), f"{nice_ly(kpc)} light-years",
                   font=font("Regular", 20 * u), fill=T, anchor="ls")

    # --- provenance tag (bottom right) ---------------------------------------------
    tag = ov.get("tag", {})
    if tag is not False:
        title = tag.get("title", "N-BODY SIMULATION")
        sub = tag.get("subtitle", f"{n_particles:,} particles · stars shown")
        tracked(d, (W - M, H - M - 30 * u), title, font("Medium", 19 * u), S, 2.2 * u, anchor="rs")
        d.text((W - M, H - M - 2 * u), sub, font=font("Regular", 19 * u), fill=T, anchor="rs")

    out = Image.alpha_composite(base, layer).convert("RGB")
    return out
