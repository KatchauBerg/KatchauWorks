#!/usr/bin/env python3
"""
Guts art generator (Berserk) — desenha com Cairo, sem imagens externas.

Gera em themes/Guts/:
  wallpapers/guts-eclipse.png         eclipse com coroa carmesim e o Espadachim Negro no morro
  wallpapers/guts-brand.png           Marca do Sacrifício sangrando sobre pedra escura
  wallpapers/guts-dragonslayer.png    a Dragonslayer cravada, aço e cinza
  wallpapers/guts-embers.mp4          loop animado: eclipse pulsando, brasas e cinzas subindo
  logo.png                            logo do fastfetch (Marca do Sacrifício)

Uso:
  python3 tools/guts_art.py [--size 2560x1440] [--only logo,eclipse,brand,sword,video]
"""
import argparse
import math
import random
import subprocess
from pathlib import Path

import cairo

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "themes/Guts"


def hexc(h, a=1.0):
    h = h.lstrip("#")
    return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)


C = {
    "void":   "#050404",
    "black":  "#0d0c0c",
    "coal":   "#1c1a1a",
    "ash":    "#4a4646",
    "steel":  "#8e9196",
    "bone":   "#d9cfc1",
    "blood":  "#c8102e",
    "crimson": "#7a0c1c",
    "ember":  "#ff4d2e",
    "glow":   "#ff2a3d",
}


def setc(cr, name, a=1.0):
    cr.set_source_rgba(*hexc(C.get(name, name), a))


# ------------------------------------------------------------- texturas ---
_grain = {}


def grain(cr, W, H, alpha=0.06, seed=1):
    """Ruído granulado (papel/pedra) — dá o ar de mangá envelhecido."""
    if seed not in _grain:
        n = 256
        rnd = random.Random(seed)
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, n, n)
        buf = surf.get_data()
        stride = surf.get_stride()
        for y in range(n):
            for x in range(n):
                v = rnd.randint(0, 255)
                i = y * stride + x * 4
                buf[i:i + 4] = bytes((v, v, v, 255))
        surf.mark_dirty()
        _grain[seed] = surf
    pat = cairo.SurfacePattern(_grain[seed])
    pat.set_extend(cairo.EXTEND_REPEAT)
    cr.save()
    cr.set_source(pat)
    cr.paint_with_alpha(alpha)
    cr.restore()


def vignette(cr, W, H, strength=0.85):
    rg = cairo.RadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, W * 0.75)
    rg.add_color_stop_rgba(0, 0, 0, 0, 0)
    rg.add_color_stop_rgba(1, 0, 0, 0, strength)
    cr.set_source(rg)
    cr.paint()


# --------------------------------------------------------------- formas ---
def brand(cr, x, y, h, color="blood", width=None, glow=True, drip=True, seed=5):
    """
    Marca do Sacrifício (estilizada): haste vertical com gancho no topo e
    um X cruzando a parte de baixo, com as pontas inferiores curvadas.
    (x, y) = topo da haste, h = altura total.
    """
    lw = width or h * 0.05
    def path():
        # haste
        cr.move_to(x, y + h * 0.06)
        cr.line_to(x, y + h)
        # gancho/forquilha no topo
        cr.move_to(x, y + h * 0.18)
        cr.curve_to(x - h * 0.02, y + h * 0.08, x - h * 0.10, y + h * 0.02, x - h * 0.16, y)
        cr.move_to(x, y + h * 0.18)
        cr.curve_to(x + h * 0.02, y + h * 0.10, x + h * 0.08, y + h * 0.05, x + h * 0.12, y + h * 0.04)
        # X inferior
        cr.move_to(x - h * 0.24, y + h * 0.42)
        cr.curve_to(x - h * 0.08, y + h * 0.56, x + h * 0.10, y + h * 0.74, x + h * 0.20, y + h * 0.96)
        cr.move_to(x + h * 0.24, y + h * 0.42)
        cr.curve_to(x + h * 0.08, y + h * 0.56, x - h * 0.10, y + h * 0.74, x - h * 0.20, y + h * 0.96)

    cr.save()
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.set_line_join(cairo.LINE_JOIN_ROUND)
    if glow:
        # brilho suave: muitas camadas finas e quase transparentes
        for i in range(16, 0, -1):
            path()
            setc(cr, "glow", 0.028)
            cr.set_line_width(lw * (1 + i * 0.55))
            cr.stroke()
    path()
    setc(cr, color)
    cr.set_line_width(lw)
    cr.stroke()
    if drip:
        rnd = random.Random(seed)
        for px, py in [(x, y + h), (x + h * 0.20, y + h * 0.96), (x - h * 0.20, y + h * 0.96),
                       (x - h * 0.24, y + h * 0.42), (x + h * 0.24, y + h * 0.42)]:
            for _ in range(rnd.randint(1, 2)):
                dx = px + rnd.uniform(-lw * 0.3, lw * 0.3)
                L = h * rnd.uniform(0.03, 0.14)
                w = lw * rnd.uniform(0.25, 0.45)
                setc(cr, color)
                cr.move_to(dx - w / 2, py)
                cr.line_to(dx - w / 3, py + L)
                cr.arc(dx, py + L, w / 2.6, math.pi, 0)
                cr.line_to(dx + w / 2, py)
                cr.close_path()
                cr.fill()
    cr.restore()


def eclipse(cr, x, y, r, pulse=0.0):
    """Sol negro com coroa carmesim. pulse ∈ [0,1] aumenta o brilho."""
    k = 1 + 0.12 * pulse
    for rr, a in [(r * 4.0 * k, 0.10), (r * 2.4 * k, 0.22), (r * 1.6 * k, 0.45)]:
        rg = cairo.RadialGradient(x, y, r * 0.95, x, y, rr)
        rg.add_color_stop_rgba(0, *hexc(C["glow"], a + 0.1 * pulse))
        rg.add_color_stop_rgba(0.35, *hexc(C["blood"], a * 0.6))
        rg.add_color_stop_rgba(1, *hexc(C["crimson"], 0))
        cr.set_source(rg)
        cr.arc(x, y, rr, 0, 2 * math.pi)
        cr.fill()
    # anel fino brilhante
    setc(cr, "ember", 0.8 + 0.2 * pulse)
    cr.set_line_width(r * 0.06)
    cr.arc(x, y, r * 1.02, 0, 2 * math.pi)
    cr.stroke()
    setc(cr, "void")
    cr.arc(x, y, r, 0, 2 * math.pi)
    cr.fill()


def swordsman(cr, x, y, s, cape_wave=0.0):
    """Silhueta do Espadachim Negro com a Dragonslayer no ombro. (x,y) = pés."""
    cr.save()
    cr.translate(x, y)
    cr.scale(s, s)
    setc(cr, "void")
    # capa esvoaçante
    w = cape_wave * 18
    cr.move_to(-30, -250)
    cr.curve_to(-70, -180, -95 - w, -90, -120 - w, 0)
    cr.line_to(-95 - w * 0.6, -10)
    cr.line_to(-80 - w * 0.4, 6)
    cr.line_to(-55, -4)
    cr.line_to(40, 0)
    cr.curve_to(55, -100, 50, -190, 30, -250)
    cr.close_path()
    cr.fill()
    # pernas
    cr.rectangle(-28, -60, 22, 60)
    cr.rectangle(8, -60, 22, 60)
    cr.fill()
    # tronco / ombreiras
    cr.move_to(-48, -255); cr.line_to(50, -255); cr.line_to(38, -150); cr.line_to(-36, -150); cr.close_path(); cr.fill()
    # cabeça (cabelo espetado)
    cr.arc(2, -282, 22, 0, 2 * math.pi); cr.fill()
    for i in range(7):
        a = -math.pi * (0.15 + 0.7 * i / 6)
        cr.move_to(2 + 14 * math.cos(a - 0.25), -282 + 14 * math.sin(a - 0.25))
        cr.line_to(2 + 36 * math.cos(a), -282 + 36 * math.sin(a))
        cr.line_to(2 + 14 * math.cos(a + 0.25), -282 + 14 * math.sin(a + 0.25))
        cr.fill()
    # Dragonslayer apoiada no ombro direito, apontando para cima/trás
    cr.save()
    cr.translate(30, -240)
    cr.rotate(-0.95)
    cr.rectangle(-20, -12, 40, 24)          # empunhadura/guarda
    cr.fill()
    cr.rectangle(-60, -6, 40, 12)           # cabo
    cr.fill()
    cr.move_to(20, -34); cr.line_to(380, -34); cr.line_to(405, 0); cr.line_to(380, 34); cr.line_to(20, 34)
    cr.close_path(); cr.fill()
    cr.restore()
    # olho/lampejo vermelho
    setc(cr, "glow", 0.9)
    cr.arc(10, -284, 3.2, 0, 2 * math.pi); cr.fill()
    cr.restore()


def dragonslayer(cr, x, y, h):
    """A Dragonslayer cravada no chão, vista de frente. (x,y)=ponta enterrada."""
    w = h * 0.21
    cr.save()
    # lâmina
    g = cairo.LinearGradient(x - w / 2, 0, x + w / 2, 0)
    g.add_color_stop_rgba(0, *hexc("#3a3a3c"))
    g.add_color_stop_rgba(0.48, *hexc("#a7abb1"))
    g.add_color_stop_rgba(0.52, *hexc("#6c6f74"))
    g.add_color_stop_rgba(1, *hexc("#232325"))
    cr.set_source(g)
    cr.move_to(x - w / 2, y - h * 0.76)
    cr.line_to(x + w / 2, y - h * 0.76)
    cr.line_to(x + w / 2, y - h * 0.10)
    cr.line_to(x + w * 0.1, y)
    cr.line_to(x - w * 0.1, y)
    cr.line_to(x - w / 2, y - h * 0.10)
    cr.close_path()
    cr.fill()
    # marcas/arranhões e sangue seco
    rnd = random.Random(9)
    cr.set_line_width(max(1, h * 0.002))
    for _ in range(40):
        yy = y - h * rnd.uniform(0.1, 0.76)
        xx = x + rnd.uniform(-w * 0.45, w * 0.45)
        setc(cr, "black", rnd.uniform(0.2, 0.5))
        cr.move_to(xx, yy); cr.line_to(xx + rnd.uniform(-w * 0.2, w * 0.2), yy + rnd.uniform(-8, 8))
        cr.stroke()
    for _ in range(14):
        setc(cr, "crimson", rnd.uniform(0.25, 0.6))
        cr.arc(x + rnd.uniform(-w * 0.4, w * 0.4), y - h * rnd.uniform(0.05, 0.5), rnd.uniform(2, w * 0.08), 0, 2 * math.pi)
        cr.fill()
    # guarda: barra grossa e curta, ferro escuro
    setc(cr, "#2a2a2c")
    cr.rectangle(x - w * 0.78, y - h * 0.80, w * 1.56, h * 0.045)
    cr.fill()
    # cabo longo enrolado em couro
    setc(cr, "#1a1818")
    cr.rectangle(x - w * 0.11, y - h * 0.99, w * 0.22, h * 0.19)
    cr.fill()
    setc(cr, "#2e2a28")
    cr.set_line_width(max(1, h * 0.004))
    for k in range(9):
        yy = y - h * 0.81 - k * h * 0.02
        cr.move_to(x - w * 0.11, yy); cr.line_to(x + w * 0.11, yy - h * 0.008)
        cr.stroke()
    setc(cr, "#2a2a2c")
    cr.rectangle(x - w * 0.16, y - h * 1.0, w * 0.32, h * 0.02)
    cr.fill()
    cr.restore()


def ground(cr, W, H, top):
    setc(cr, "void")
    cr.move_to(0, H)
    cr.line_to(0, top + 40)
    cr.curve_to(W * 0.25, top - 10, W * 0.45, top + 30, W * 0.62, top - 30)
    cr.curve_to(W * 0.78, top - 70, W * 0.9, top + 10, W, top - 5)
    cr.line_to(W, H)
    cr.close_path()
    cr.fill()


def make_embers(W, H, n, seed):
    rnd = random.Random(seed)
    return [dict(x=rnd.random() * W, ph=rnd.random(), sp=rnd.choice([1, 1, 2]),
                 r=rnd.uniform(1.2, 3.8), sway=rnd.uniform(10, 50), col=rnd.choice(["ember", "glow", "blood", "steel"]))
            for _ in range(n)]


def draw_embers(cr, W, H, embers, t, u):
    for e in embers:
        p = (e["ph"] + t * e["sp"]) % 1.0
        y = H * (1.05 - p * 1.1)
        x = e["x"] + math.sin(2 * math.pi * (p * 2 + e["ph"])) * e["sway"] * u
        a = math.sin(math.pi * p)
        if e["col"] == "steel":   # cinzas
            setc(cr, "steel", 0.35 * a)
            cr.rectangle(x, y, e["r"] * u * 1.4, e["r"] * u * 0.7)
        else:
            rg = cairo.RadialGradient(x, y, 0, x, y, e["r"] * 3 * u)
            rg.add_color_stop_rgba(0, *hexc(C[e["col"]], 0.9 * a))
            rg.add_color_stop_rgba(1, *hexc(C[e["col"]], 0))
            cr.set_source(rg)
            cr.arc(x, y, e["r"] * 3 * u, 0, 2 * math.pi)
        cr.fill()


def caption(cr, x, y, size, text, sub=None, color="steel"):
    cr.select_font_face("DejaVu Serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    cr.set_font_size(size)
    # espaçamento entre letras
    spaced = " ".join(text)
    e = cr.text_extents(spaced)
    setc(cr, color, 0.85)
    cr.move_to(x - e.width / 2, y)
    cr.show_text(spaced)
    if sub:
        cr.select_font_face("DejaVu Serif", cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(size * 0.38)
        e2 = cr.text_extents(sub)
        setc(cr, "ash", 0.9)
        cr.move_to(x - e2.width / 2, y + size * 0.9)
        cr.show_text(sub)


# ------------------------------------------------------------ composições ---
def sky(cr, W, H):
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgba(0, *hexc(C["void"]))
    g.add_color_stop_rgba(0.6, *hexc("#1a0608"))
    g.add_color_stop_rgba(1, *hexc("#3a0a10"))
    cr.set_source(g)
    cr.paint()


def scene_eclipse(cr, W, H, t=0.0, embers=None):
    u = H / 1080
    sky(cr, W, H)
    pulse = 0.5 + 0.5 * math.sin(2 * math.pi * t)
    eclipse(cr, W * 0.5, H * 0.34, 120 * u, pulse)
    # névoa vermelha rasteira
    for i in range(3):
        off = ((t + i / 3) % 1.0) * W
        rg = cairo.RadialGradient(off, H * 0.82, 0, off, H * 0.82, W * 0.35)
        rg.add_color_stop_rgba(0, *hexc(C["blood"], 0.10))
        rg.add_color_stop_rgba(1, *hexc(C["blood"], 0))
        cr.set_source(rg)
        cr.paint()
    ground(cr, W, H, H * 0.86)
    swordsman(cr, W * 0.66, H * 0.86 - 32 * u, 1.3 * u, math.sin(2 * math.pi * t * 2))
    draw_embers(cr, W, H, embers or make_embers(W, H, 140, 3), t, u)
    grain(cr, W, H, 0.05)
    vignette(cr, W, H, 0.8)


def scene_brand(cr, W, H):
    u = H / 1080
    setc(cr, "black")
    cr.paint()
    # pedra: manchas
    rnd = random.Random(2)
    for _ in range(60):
        x, y, r = rnd.random() * W, rnd.random() * H, rnd.uniform(80, 400) * u
        rg = cairo.RadialGradient(x, y, 0, x, y, r)
        rg.add_color_stop_rgba(0, *hexc(C["coal"], rnd.uniform(0.2, 0.5)))
        rg.add_color_stop_rgba(1, *hexc(C["coal"], 0))
        cr.set_source(rg)
        cr.paint()
    grain(cr, W, H, 0.09, seed=4)
    brand(cr, W * 0.5, H * 0.16, 560 * u)
    caption(cr, W * 0.5, H * 0.9, 34 * u, "STRUGGLER", "“if you're always worried about crushing the ants beneath you, you won't be able to walk”")
    vignette(cr, W, H, 0.9)


def scene_sword(cr, W, H):
    u = H / 1080
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgba(0, *hexc("#1b1b1d"))
    g.add_color_stop_rgba(1, *hexc("#080808"))
    cr.set_source(g)
    cr.paint()
    # marca ao fundo, quase apagada
    brand(cr, W * 0.5, H * 0.08, 760 * u, color="crimson", glow=True, drip=False)
    cr.save()
    setc(cr, "black", 0.55)
    cr.paint()
    cr.restore()
    dragonslayer(cr, W * 0.5, H * 0.93, 900 * u)
    setc(cr, "void")
    cr.rectangle(0, H * 0.9, W, H * 0.1)
    cr.fill()
    grain(cr, W, H, 0.07, seed=7)
    caption(cr, W * 0.5, H * 0.975, 22 * u, "TOO BIG TO BE CALLED A SWORD", color="ash")
    vignette(cr, W, H, 0.75)


# ---------------------------------------------------------------- saídas ---
def render_png(path, W, H, fn):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    cr = cairo.Context(surf)
    fn(cr, W, H)
    path.parent.mkdir(parents=True, exist_ok=True)
    surf.write_to_png(str(path))
    print(f"  ✓ {path.relative_to(ROOT)}")


def render_logo(path, size=512):
    render_png(path, size, size, lambda cr, W, H: brand(cr, W * 0.5, H * 0.08, H * 0.78, seed=11))


def render_video(path, W, H, seconds=8, fps=30):
    path.parent.mkdir(parents=True, exist_ok=True)
    n = seconds * fps
    embers = make_embers(W, H, 140, 3)
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error",
         "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
         "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p",
         "-movflags", "+faststart", str(path)],
        stdin=subprocess.PIPE,
    )
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    for i in range(n):
        cr = cairo.Context(surf)
        scene_eclipse(cr, W, H, t=i / n, embers=embers)
        surf.flush()
        ff.stdin.write(bytes(surf.get_data()))
        if i % fps == 0:
            print(f"\r  … frame {i}/{n}", end="", flush=True)
    ff.stdin.close()
    ff.wait()
    print(f"\r  ✓ {path.relative_to(ROOT)}            ")
    render_png(path.with_suffix(".poster.png"), W, H, lambda cr, w, h: scene_eclipse(cr, w, h, 0.0, embers))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", default="1920x1080")
    ap.add_argument("--only", default="logo,eclipse,brand,sword,video")
    ap.add_argument("--seconds", type=int, default=8)
    ap.add_argument("--fps", type=int, default=30)
    a = ap.parse_args()
    W, H = map(int, a.size.lower().split("x"))
    only = set(a.only.split(","))
    wp = OUT / "wallpapers"
    print(f"Guts art → {W}x{H}")
    if "logo" in only:
        render_logo(OUT / "logo.png")
    if "eclipse" in only:
        render_png(wp / "guts-eclipse.png", W, H, scene_eclipse)
    if "brand" in only:
        render_png(wp / "guts-brand.png", W, H, scene_brand)
    if "sword" in only:
        render_png(wp / "guts-dragonslayer.png", W, H, scene_sword)
    if "video" in only:
        render_video(wp / "guts-embers.mp4", W, H, a.seconds, a.fps)


if __name__ == "__main__":
    main()
