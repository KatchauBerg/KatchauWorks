#!/usr/bin/env python3
"""
Kuromi art generator — desenha a Kuromi com Cairo (vetorial, sem imagens externas).

Gera em themes/Kuromi/:
  wallpapers/kuromi-night.png      cena noturna com lua, estrelas e Kuromi
  wallpapers/kuromi-pattern.png    padrão de caveirinhas, corações e Kuromis
  wallpapers/kuromi-minimal.png    minimalista, para focar no trabalho
  wallpapers/kuromi-dreams.mp4     loop animado (estrelas, morcegos, Kuromi flutuando)
  logo.png                         logo do fastfetch

Uso:
  python3 tools/kuromi_art.py                 # tudo, em 1920x1080
  python3 tools/kuromi_art.py --size 2560x1440
  python3 tools/kuromi_art.py --only logo,night
"""
import argparse
import math
import random
import subprocess
from pathlib import Path

import cairo

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------- paleta ---
def hexc(h, a=1.0):
    h = h.lstrip("#")
    return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)

C = {
    "void":     "#0f0b14",
    "night":    "#1a1224",
    "plum":     "#2b1d3a",
    "grape":    "#4a2f66",
    "lavender": "#b794f6",
    "lilac":    "#d8c4ff",
    "pink":     "#ff8fc8",
    "hotpink":  "#ff5fa2",
    "blush":    "#ffb3d6",
    "white":    "#fffafd",
    "ink":      "#16111b",
    "hood":     "#1c1622",
    "hoodhi":   "#3a2d48",
    "yellow":   "#ffe08a",
}


def setc(cr, name, a=1.0):
    cr.set_source_rgba(*hexc(C.get(name, name), a))


# ---------------------------------------------------------------- formas ---
def heart(cr, x, y, s):
    cr.save()
    cr.translate(x, y)
    cr.scale(s, s)
    cr.move_to(0, 0.35)
    cr.curve_to(-0.05, 0.3, -0.5, 0.05, -0.5, -0.2)
    cr.curve_to(-0.5, -0.45, -0.2, -0.55, 0, -0.3)
    cr.curve_to(0.2, -0.55, 0.5, -0.45, 0.5, -0.2)
    cr.curve_to(0.5, 0.05, 0.05, 0.3, 0, 0.35)
    cr.close_path()
    cr.restore()


def star(cr, x, y, r, points=4, inner=0.38, rot=0.0):
    cr.save()
    cr.translate(x, y)
    cr.rotate(rot)
    for i in range(points * 2):
        rr = r if i % 2 == 0 else r * inner
        a = math.pi * i / points - math.pi / 2
        (cr.move_to if i == 0 else cr.line_to)(rr * math.cos(a), rr * math.sin(a))
    cr.close_path()
    cr.restore()


def skull(cr, x, y, s, color="pink", eye="ink"):
    """Caveirinha fofa (emblema da Kuromi). (x,y) = centro, s = largura aprox."""
    cr.save()
    cr.translate(x, y)
    cr.scale(s / 100, s / 100)
    setc(cr, color)
    # crânio
    cr.arc(0, -8, 42, 0, 2 * math.pi)
    cr.fill()
    # mandíbula
    cr.new_sub_path()
    rounded_rect(cr, -24, 18, 48, 26, 9)
    cr.fill()
    setc(cr, eye)
    # olhos
    cr.save(); cr.translate(-16, -6); cr.scale(1, 1.15); cr.arc(0, 0, 11, 0, 2 * math.pi); cr.restore(); cr.fill()
    cr.save(); cr.translate(16, -6); cr.scale(1, 1.15); cr.arc(0, 0, 11, 0, 2 * math.pi); cr.restore(); cr.fill()
    # nariz
    cr.move_to(0, 10); cr.line_to(-5, 19); cr.line_to(5, 19); cr.close_path(); cr.fill()
    # dentes
    cr.set_line_width(3.5)
    for dx in (-9, 0, 9):
        cr.move_to(dx, 28); cr.line_to(dx, 42)
    cr.stroke()
    cr.restore()


def rounded_rect(cr, x, y, w, h, r):
    cr.move_to(x + r, y)
    cr.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    cr.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    cr.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    cr.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    cr.close_path()


def bat(cr, x, y, s, flap=0.0, color="ink"):
    """Morceguinho. flap em [-1, 1] dobra as asas."""
    cr.save()
    cr.translate(x, y)
    cr.scale(s / 100, s / 100)
    setc(cr, color)
    lift = -18 * flap
    for side in (-1, 1):
        cr.move_to(0, -4)
        cr.curve_to(side * 18, -16 + lift, side * 38, -26 + lift, side * 52, -14 + lift)
        cr.curve_to(side * 44, -8 + lift * 0.6, side * 42, 0, side * 46, 8)
        cr.curve_to(side * 36, 2, side * 30, 4, side * 26, 12)
        cr.curve_to(side * 20, 4, side * 12, 6, 0, 10)
        cr.close_path()
        cr.fill()
    cr.arc(0, 0, 11, 0, 2 * math.pi)
    cr.fill()
    # orelhinhas
    for side in (-1, 1):
        cr.move_to(side * 4, -8); cr.line_to(side * 10, -20); cr.line_to(side * 11, -6); cr.close_path(); cr.fill()
    setc(cr, "pink")
    cr.arc(-4, -1, 2.2, 0, 2 * math.pi); cr.fill()
    cr.arc(4, -1, 2.2, 0, 2 * math.pi); cr.fill()
    cr.restore()


def kuromi(cr, x, y, s, wink=0.0, tail=0.0, blush=True, outline=True):
    """
    Kuromi (busto). (x, y) = centro do rosto, s = escala (1.0 ≈ 512px de altura).
    wink: 0 aberto → 1 olho direito fechado. tail: ângulo extra do rabinho.
    """
    cr.save()
    cr.translate(x, y)
    cr.scale(s, s)
    lw = 7

    # --- rabinho de diabinho (atrás do corpo)
    cr.save()
    cr.translate(120, 150)
    cr.rotate(tail)
    setc(cr, "hood")
    cr.set_line_width(14)
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.move_to(0, 0)
    cr.curve_to(70, 20, 90, -50, 140, -60)
    cr.stroke()
    cr.move_to(140, -60)
    cr.line_to(150, -95); cr.line_to(172, -62); cr.line_to(160, -48); cr.close_path()
    cr.fill()
    cr.restore()

    # --- corpinho
    setc(cr, "hood")
    cr.move_to(-110, 110)
    cr.curve_to(-140, 190, -130, 250, -100, 260)
    cr.line_to(100, 260)
    cr.curve_to(130, 250, 140, 190, 110, 110)
    cr.close_path()
    cr.fill()
    # gola rosa
    setc(cr, "pink")
    cr.move_to(-95, 135)
    cr.curve_to(-50, 175, 50, 175, 95, 135)
    cr.curve_to(60, 205, -60, 205, -95, 135)
    cr.close_path()
    cr.fill()
    # bracinhos
    setc(cr, "white")
    cr.arc(-108, 215, 26, 0, 2 * math.pi); cr.fill()
    cr.arc(108, 215, 26, 0, 2 * math.pi); cr.fill()

    # --- capuz com orelhas de bobo da corte
    hood = lambda: (
        cr.move_to(-190, 70),
        cr.curve_to(-215, -10, -200, -90, -160, -140),          # lateral esquerda
        cr.curve_to(-175, -200, -215, -250, -250, -300),        # sobe a orelha esq.
        cr.curve_to(-170, -285, -110, -240, -85, -185),         # desce p/ topo
        cr.curve_to(-30, -205, 30, -205, 85, -185),             # topo da cabeça
        cr.curve_to(110, -240, 170, -285, 250, -300),           # orelha dir.
        cr.curve_to(215, -250, 175, -200, 160, -140),
        cr.curve_to(200, -90, 215, -10, 190, 70),               # lateral direita
        cr.curve_to(150, 140, -150, 140, -190, 70),             # base
        cr.close_path(),
    )
    hood()
    setc(cr, "hood")
    cr.fill_preserve()
    if outline:
        setc(cr, "hoodhi")
        cr.set_line_width(lw)
        cr.stroke()
    else:
        cr.new_path()

    # brilho no capuz
    cr.save()
    hood(); cr.clip()
    g = cairo.LinearGradient(-200, -300, 120, 60)
    g.add_color_stop_rgba(0, *hexc(C["grape"], 0.55))
    g.add_color_stop_rgba(0.45, *hexc(C["hood"], 0.0))
    cr.set_source(g)
    cr.paint()
    cr.restore()

    # pontinhas das orelhas (rosa)
    for side in (-1, 1):
        setc(cr, "pink")
        cr.arc(side * 248, -300, 16, 0, 2 * math.pi)
        cr.fill()

    # --- rosto (abertura do capuz, com bico no meio da testa)
    face = lambda: (
        cr.move_to(0, -70),
        cr.curve_to(-40, -105, -120, -110, -150, -55),
        cr.curve_to(-180, 0, -160, 85, -90, 110),
        cr.curve_to(-40, 128, 40, 128, 90, 110),
        cr.curve_to(160, 85, 180, 0, 150, -55),
        cr.curve_to(120, -110, 40, -105, 0, -70),
        cr.close_path(),
    )
    face()
    setc(cr, "white")
    cr.fill_preserve()
    if outline:
        setc(cr, "ink")
        cr.set_line_width(4)
        cr.stroke()
    else:
        cr.new_path()

    # --- caveira rosa na testa do capuz
    skull(cr, 0, -140, 74)

    # --- olhos
    def eye(ex, closed):
        if closed > 0.5:
            setc(cr, "ink")
            cr.set_line_width(7)
            cr.set_line_cap(cairo.LINE_CAP_ROUND)
            cr.move_to(ex - 20, 8)
            cr.curve_to(ex - 8, -6, ex + 8, -6, ex + 20, 8)
            cr.stroke()
            return
        open_ = 1.0 - closed * 2
        cr.save()
        cr.translate(ex, 5)
        cr.scale(1, max(0.08, open_) * 1.35)
        setc(cr, "ink")
        cr.arc(0, 0, 22, 0, 2 * math.pi)
        cr.fill()
        cr.restore()
        if open_ > 0.4:
            setc(cr, "white")
            cr.arc(ex + 7, -9, 7, 0, 2 * math.pi); cr.fill()
            cr.arc(ex - 7, 14, 3.2, 0, 2 * math.pi); cr.fill()

    eye(-62, 0.0)
    eye(62, wink)

    # nariz
    setc(cr, "yellow")
    cr.save(); cr.translate(0, 40); cr.scale(1.3, 1); cr.arc(0, 0, 8, 0, 2 * math.pi); cr.restore(); cr.fill()

    # boca travessa com dentinho
    setc(cr, "ink")
    cr.set_line_width(5)
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.move_to(-26, 62)
    cr.curve_to(-12, 78, 12, 78, 26, 62)
    cr.stroke()
    setc(cr, "white")
    cr.move_to(8, 70); cr.line_to(16, 69); cr.line_to(12, 80); cr.close_path(); cr.fill()

    # bochechas
    if blush:
        for side in (-1, 1):
            cr.save()
            cr.translate(side * 105, 55)
            cr.scale(1.5, 1)
            rg = cairo.RadialGradient(0, 0, 0, 0, 0, 20)
            rg.add_color_stop_rgba(0, *hexc(C["pink"], 0.75))
            rg.add_color_stop_rgba(1, *hexc(C["pink"], 0.0))
            cr.set_source(rg)
            cr.arc(0, 0, 20, 0, 2 * math.pi)
            cr.fill()
            cr.restore()

    cr.restore()


# ---------------------------------------------------------------- fundos ---
def night_sky(cr, W, H):
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgba(0.0, *hexc(C["void"]))
    g.add_color_stop_rgba(0.55, *hexc(C["night"]))
    g.add_color_stop_rgba(1.0, *hexc(C["plum"]))
    cr.set_source(g)
    cr.paint()
    # névoa rosada no horizonte
    rg = cairo.RadialGradient(W * 0.7, H * 1.05, 0, W * 0.7, H * 1.05, H * 0.9)
    rg.add_color_stop_rgba(0, *hexc(C["hotpink"], 0.28))
    rg.add_color_stop_rgba(1, *hexc(C["hotpink"], 0.0))
    cr.set_source(rg)
    cr.paint()
    rg = cairo.RadialGradient(W * 0.15, H * 0.1, 0, W * 0.15, H * 0.1, H * 0.8)
    rg.add_color_stop_rgba(0, *hexc(C["lavender"], 0.12))
    rg.add_color_stop_rgba(1, *hexc(C["lavender"], 0.0))
    cr.set_source(rg)
    cr.paint()


def moon(cr, x, y, r):
    halo = cairo.RadialGradient(x, y, r * 0.8, x, y, r * 3)
    halo.add_color_stop_rgba(0, *hexc(C["lilac"], 0.25))
    halo.add_color_stop_rgba(1, *hexc(C["lilac"], 0.0))
    cr.set_source(halo)
    cr.arc(x, y, r * 3, 0, 2 * math.pi)
    cr.fill()
    # lua crescente
    cr.push_group()
    setc(cr, "lilac")
    cr.arc(x, y, r, 0, 2 * math.pi)
    cr.fill()
    cr.set_operator(cairo.OPERATOR_CLEAR)
    cr.arc(x + r * 0.45, y - r * 0.2, r * 0.88, 0, 2 * math.pi)
    cr.fill()
    cr.pop_group_to_source()
    cr.paint()


def hills(cr, W, H):
    setc(cr, "void")
    cr.move_to(0, H)
    cr.line_to(0, H * 0.86)
    cr.curve_to(W * 0.2, H * 0.78, W * 0.35, H * 0.92, W * 0.55, H * 0.85)
    cr.curve_to(W * 0.75, H * 0.78, W * 0.9, H * 0.88, W, H * 0.82)
    cr.line_to(W, H)
    cr.close_path()
    cr.fill()


def make_stars(W, H, n, seed):
    rnd = random.Random(seed)
    return [
        dict(x=rnd.random() * W, y=rnd.random() * H * 0.8, r=rnd.uniform(1.0, 3.4),
             ph=rnd.random() * 2 * math.pi, sp=rnd.choice([1, 2, 3]),
             kind=rnd.choice(["dot", "dot", "dot", "spark", "heart"]),
             col=rnd.choice(["white", "lilac", "pink", "lavender"]))
        for _ in range(n)
    ]


def draw_stars(cr, stars, t=0.0, scale=1.0):
    for s in stars:
        tw = 0.55 + 0.45 * math.sin(s["ph"] + 2 * math.pi * s["sp"] * t)
        r = s["r"] * scale
        setc(cr, s["col"], 0.35 + 0.65 * tw)
        if s["kind"] == "dot":
            cr.arc(s["x"], s["y"], r, 0, 2 * math.pi)
        elif s["kind"] == "spark":
            star(cr, s["x"], s["y"], r * 3.2 * (0.7 + 0.3 * tw))
        else:
            heart(cr, s["x"], s["y"], r * 5)
        cr.fill()


def title(cr, x, y, size, text="KUROMI", sub="stay cute, stay chaotic"):
    cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    cr.set_font_size(size)
    ext = cr.text_extents(text)
    # sombra roxa
    setc(cr, "grape", 0.9)
    cr.move_to(x - ext.width / 2 + size * 0.05, y + size * 0.05)
    cr.show_text(text)
    setc(cr, "pink")
    cr.move_to(x - ext.width / 2, y)
    cr.show_text(text)
    if sub:
        cr.select_font_face("Sans", cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(size * 0.24)
        e2 = cr.text_extents(sub)
        setc(cr, "lilac", 0.85)
        sy = y + size * 0.5
        cr.move_to(x - e2.width / 2, sy)
        cr.show_text(sub)
        # corações desenhados (a fonte padrão não tem o glifo ♡)
        setc(cr, "pink")
        for side in (-1, 1):
            heart(cr, x + side * (e2.width / 2 + size * 0.2), sy - size * 0.08, size * 0.2)
            cr.fill()


# ------------------------------------------------------------ composições ---
def scene_night(cr, W, H, t=0.0, stars=None):
    """Cena principal. t ∈ [0,1) para animação em loop."""
    u = H / 1080
    night_sky(cr, W, H)
    draw_stars(cr, stars or make_stars(W, H, 220, 7), t, u)
    moon(cr, W * 0.16, H * 0.2, 70 * u)

    # morcegos voando em loop
    rnd = random.Random(3)
    for i in range(6):
        base_y = H * rnd.uniform(0.12, 0.5)
        speed = rnd.choice([1, 1, 2])
        px = ((rnd.random() + t * speed) % 1.0) * (W + 300 * u) - 150 * u
        py = base_y + math.sin(2 * math.pi * (t * speed * 2 + i / 6)) * 25 * u
        flap = math.sin(2 * math.pi * (t * 16 + i / 3))
        bat(cr, px, py, rnd.uniform(40, 70) * u, flap, "grape" if i % 2 else "ink")

    hills(cr, W, H)

    # corações subindo
    rnd = random.Random(11)
    for i in range(14):
        hx = W * rnd.uniform(0.45, 0.98)
        prog = (rnd.random() + t) % 1.0
        hy = H * (1.05 - prog * 0.9)
        a = math.sin(math.pi * prog) * 0.7
        setc(cr, rnd.choice(["pink", "hotpink", "lavender"]), a)
        heart(cr, hx + math.sin(2 * math.pi * (prog * 2 + i / 7)) * 18 * u, hy, rnd.uniform(14, 30) * u)
        cr.fill()

    # Kuromi flutuando à direita
    bob = math.sin(2 * math.pi * t) * 14 * u
    blink_phase = (t * 2) % 1.0
    wink = 1.0 if 0.47 < blink_phase < 0.53 else 0.0
    tail = math.sin(2 * math.pi * t * 2) * 0.18
    # sombra/brilho atrás
    rg = cairo.RadialGradient(W * 0.72, H * 0.5, 0, W * 0.72, H * 0.5, 420 * u)
    rg.add_color_stop_rgba(0, *hexc(C["lavender"], 0.22))
    rg.add_color_stop_rgba(1, *hexc(C["lavender"], 0.0))
    cr.set_source(rg)
    cr.paint()
    kuromi(cr, W * 0.72, H * 0.47 + bob, 1.05 * u, wink=wink, tail=tail)

    title(cr, W * 0.28, H * 0.72, 120 * u)


def scene_pattern(cr, W, H):
    u = H / 1080
    setc(cr, "night")
    cr.paint()
    step = 180 * u
    rows = int(H / step) + 2
    cols = int(W / step) + 2
    for r in range(rows):
        for c in range(cols):
            x = c * step + (step / 2 if r % 2 else 0)
            y = r * step
            k = (r * 7 + c * 3) % 5
            if k == 0:
                kuromi(cr, x, y + 10 * u, 0.17 * u)
            elif k in (1, 3):
                skull(cr, x, y, 46 * u, color="pink" if k == 1 else "lavender", eye="night")
            elif k == 2:
                setc(cr, "hotpink", 0.8)
                heart(cr, x, y, 46 * u)
                cr.fill()
            else:
                setc(cr, "lilac", 0.7)
                star(cr, x, y, 18 * u)
                cr.fill()
    # vinheta
    rg = cairo.RadialGradient(W / 2, H / 2, H * 0.3, W / 2, H / 2, W * 0.75)
    rg.add_color_stop_rgba(0, *hexc(C["void"], 0.0))
    rg.add_color_stop_rgba(1, *hexc(C["void"], 0.75))
    cr.set_source(rg)
    cr.paint()


def scene_minimal(cr, W, H):
    u = H / 1080
    g = cairo.LinearGradient(0, 0, W, H)
    g.add_color_stop_rgba(0, *hexc(C["void"]))
    g.add_color_stop_rgba(1, *hexc(C["night"]))
    cr.set_source(g)
    cr.paint()
    draw_stars(cr, make_stars(W, H, 60, 21), 0.0, u * 0.8)
    rg = cairo.RadialGradient(W / 2, H / 2, 0, W / 2, H / 2, 300 * u)
    rg.add_color_stop_rgba(0, *hexc(C["hotpink"], 0.18))
    rg.add_color_stop_rgba(1, *hexc(C["hotpink"], 0.0))
    cr.set_source(rg)
    cr.paint()
    skull(cr, W / 2, H / 2 - 20 * u, 150 * u)
    cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    cr.set_font_size(30 * u)
    txt = "k u r o m i"
    e = cr.text_extents(txt)
    setc(cr, "lavender", 0.8)
    cr.move_to(W / 2 - e.width / 2, H / 2 + 120 * u)
    cr.show_text(txt)


# ---------------------------------------------------------------- saídas ---
def render_png(path, W, H, fn):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    cr = cairo.Context(surf)
    cr.set_antialias(cairo.ANTIALIAS_BEST)
    fn(cr, W, H)
    path.parent.mkdir(parents=True, exist_ok=True)
    surf.write_to_png(str(path))
    print(f"  ✓ {path.relative_to(ROOT)}")


def render_logo(path, size=512):
    def fn(cr, W, H):
        # Kuromi inteira cabe em ~ 560 x 600 unidades
        s = size / 620
        kuromi(cr, W / 2, H * 0.56, s)
    render_png(path, size, size, fn)


def render_video(path, W, H, seconds=8, fps=30):
    path.parent.mkdir(parents=True, exist_ok=True)
    n = seconds * fps
    stars = make_stars(W, H, 220, 7)
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
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.set_source_rgba(0, 0, 0, 1)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)
        scene_night(cr, W, H, t=i / n, stars=stars)
        surf.flush()
        ff.stdin.write(bytes(surf.get_data()))
        if i % fps == 0:
            print(f"\r  … frame {i}/{n}", end="", flush=True)
    ff.stdin.close()
    ff.wait()
    print(f"\r  ✓ {path.relative_to(ROOT)}            ")
    # pôster (primeiro frame) — usado no lockscreen enquanto o vídeo roda
    render_png(path.with_suffix(".poster.png"), W, H, lambda cr, w, h: scene_night(cr, w, h, 0.0, stars))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", default="1920x1080")
    ap.add_argument("--only", default="logo,night,pattern,minimal,video")
    ap.add_argument("--seconds", type=int, default=8)
    ap.add_argument("--fps", type=int, default=30)
    a = ap.parse_args()
    W, H = map(int, a.size.lower().split("x"))
    only = set(a.only.split(","))
    print(f"Kuromi art → {W}x{H}")
    st = an = ROOT / "themes/Kuromi/wallpapers"
    if "logo" in only:
        render_logo(ROOT / "themes/Kuromi/logo.png")
    if "night" in only:
        render_png(st / "kuromi-night.png", W, H, scene_night)
    if "pattern" in only:
        render_png(st / "kuromi-pattern.png", W, H, scene_pattern)
    if "minimal" in only:
        render_png(st / "kuromi-minimal.png", W, H, scene_minimal)
    if "video" in only:
        render_video(an / "kuromi-dreams.mp4", W, H, a.seconds, a.fps)


if __name__ == "__main__":
    main()
