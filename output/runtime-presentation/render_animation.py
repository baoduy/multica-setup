"""Render the original Archify runtime architecture with synchronized arrow dots."""
from pathlib import Path
import io
import math
import re
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw, ImageFont
import resvg_py


OUT = Path(__file__).resolve().parent
SOURCE = OUT.parents[1] / ".archify/architecture-runtime/runtime.html"
SIZE = (1440, 1440)
FPS, SECONDS, SUPERSAMPLE = 50, 4, 2
DIAGRAM_WIDTH = 1280
DX, DY = 80, 64
NAVY = "#172A43"
FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"


def load_diagram():
    html = SOURCE.read_text()
    svg = re.search(r"<svg\b.*?</svg>", html, re.S).group()
    tree = ET.fromstring(svg)
    _, _, width, height = map(float, tree.get("viewBox").split())
    light = re.search(r'\[data-theme="light"\]\s*\{(.*?)\}', html, re.S).group(1)
    tokens = dict(re.findall(r"--([\w-]+)\s*:\s*([^;]+);", light))
    classes = sorted({cls for group in re.findall(r'class="([^"]+)"', svg)
                      for cls in group.split()})
    css = []
    for cls in classes:
        match = re.search(r"(?<![\w-])\." + re.escape(cls) + r"\s*\{([^}]+)\}", html)
        if match:
            body = re.sub(r"var\(--([\w-]+)\)", lambda m: tokens[m[1]], match[1])
            css.append("." + cls + " {" + body + "}")
    css.append('text {font-family: "Menlo", monospace;}')
    # Resolve the region's browser-only color-mix to the native light palette.
    css.append(".c-region {fill:rgba(251,191,36,.05); stroke:"
               + tokens["cloud-stroke"] + "; stroke-dasharray:8,4;}")
    css.append(".semantic-sigil {fill:none; stroke:currentColor; stroke-width:1.35;"
               "stroke-linecap:round; stroke-linejoin:round; opacity:.76;}")
    for kind in ("backend", "frontend", "cloud", "security", "external"):
        css.append(".s-" + kind + " {color:" + tokens[kind + "-stroke"] + ";}")

    routes = []
    colors = {
        "a-emphasis": tokens["arrow-emphasis"],
        "a-security": tokens["security-stroke"],
        "a-dashed": tokens["database-stroke"],
        "a-default": tokens["arrow"],
    }
    for el in tree.iter("path"):
        if el.get("data-composition-points"):
            points = [tuple(map(float, p.split(",")))
                      for p in el.get("data-composition-points").split(";")]
            routes.append((points, colors[el.get("class")]))

    diagram_height = round(DIAGRAM_WIDTH * height / width)
    svg = svg.replace("<svg ", '<svg xmlns="http://www.w3.org/2000/svg" '
                      f'width="{DIAGRAM_WIDTH}" height="{diagram_height}" ', 1)
    svg = svg.replace("<!-- Definitions -->", "<style>" + "".join(css) + "</style>", 1)
    svg = re.sub(r'<pattern id="grid".*?</pattern>',
                 '<pattern id="grid" width="12" height="12" patternUnits="userSpaceOnUse">'
                 '<circle cx="1" cy="1" r=".5" fill="#d9dee5"/></pattern>', svg, flags=re.S)
    return svg, routes, DIAGRAM_WIDTH / width, diagram_height


def draw_dot(draw, points, progress, color):
    lengths = [math.dist(a, b) for a, b in zip(points, points[1:])]
    remaining = sum(lengths) * progress
    for a, b, length in zip(points, points[1:], lengths):
        if length == 0:
            continue
        if remaining <= length:
            x = a[0] + (b[0] - a[0]) * remaining / length
            y = a[1] + (b[1] - a[1]) * remaining / length
            radius, inner = 6 * SUPERSAMPLE, 1.875 * SUPERSAMPLE
            draw.ellipse((x-radius, y-radius, x+radius, y+radius),
                         fill="white", outline=color, width=3)
            draw.ellipse((x-inner, y-inner, x+inner, y+inner), fill=color)
            return
        remaining -= length


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    svg, routes, diagram_scale, diagram_height = load_diagram()
    (OUT / "runtime-layout.svg").write_text(svg)
    background = Image.new("RGB", tuple(v*SUPERSAMPLE for v in SIZE), "#f4f5f7")
    diagram = Image.open(io.BytesIO(resvg_py.svg_to_bytes(
        svg_string=svg, width=DIAGRAM_WIDTH*SUPERSAMPLE,
        height=diagram_height*SUPERSAMPLE, background="white"))).convert("RGB")
    background.paste(diagram, (DX*SUPERSAMPLE, DY*SUPERSAMPLE))
    draw = ImageDraw.Draw(background)
    def text(x, y, value, size, color, bold=False):
        draw.text((x*SUPERSAMPLE, y*SUPERSAMPLE), value, fill=color,
                  font=ImageFont.truetype(BOLD if bold else FONT, size*SUPERSAMPLE))
    text(80, 20, "Multica setup - Runtime architecture", 26, NAVY, True)
    draw.rounded_rectangle((160, 2640, 2720, 2820), radius=18, fill=NAVY)
    text(100, 1334, "From root tickets to published packages", 25, "white", True)
    text(100, 1374, "Runtime, agent teams, review gates, and release connections.", 21, "#DAE3EF")
    background.resize(SIZE, Image.Resampling.LANCZOS).save(OUT / "runtime-overview.png")
    routes = [
        ([(SUPERSAMPLE*(DX+x*diagram_scale), SUPERSAMPLE*(DY+y*diagram_scale))
          for x, y in points], color) for points, color in routes
    ]
    palette_source = background.copy()
    draw = ImageDraw.Draw(palette_source)
    for i, color in enumerate(sorted({color for _, color in routes} | {"white"})):
        draw.rectangle((i*40, 0, (i+1)*40-1, 39), fill=color)
    palette = palette_source.resize(SIZE, Image.Resampling.LANCZOS).quantize(colors=256)
    frames = []
    for n in range(FPS*SECONDS):
        phase = n / (FPS*SECONDS)
        progress = phase*phase*(3-2*phase)
        opacity = min(1, phase/0.04, (1-phase)/0.04)
        canvas = background.copy()
        draw = ImageDraw.Draw(canvas)
        for points, color in routes:
            draw_dot(draw, points, progress, color)
        if opacity < 1:
            canvas = Image.blend(background, canvas, opacity)
        frames.append(canvas.resize(SIZE, Image.Resampling.LANCZOS).quantize(
            palette=palette, dither=Image.Dither.NONE))
    frames[0].save(OUT / "runtime-animation.gif", save_all=True,
                   append_images=frames[1:], duration=1000//FPS, loop=0,
                   optimize=True, disposal=1)
    print(f"Complete: {len(routes)} synchronized arrows, {SIZE}, {SECONDS}s, {FPS} fps")


if __name__ == "__main__":
    main()
