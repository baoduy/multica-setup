"""Animate Archify's native SVG without changing its authored geometry."""
from pathlib import Path
import io
import re
import math
import subprocess
import argparse
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont
import resvg_py
import imageio_ffmpeg

NAVY, MUTED = '#172A43', '#64748B'
FONT = '/System/Library/Fonts/Supplemental/Arial.ttf'
BOLD = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'

def text(d, xy, value, size=24, color=NAVY, bold=False):
    d.text(xy, value, font=ImageFont.truetype(BOLD if bold else FONT, size), fill=color)

def dot_on_path(d, points, fraction, color, scale=1):
    lengths = [math.dist(a, b) for a, b in zip(points, points[1:])]
    distance = sum(lengths) * fraction
    for a, b, length in zip(points, points[1:], lengths):
        if length == 0:
            continue
        if distance <= length:
            x = a[0] + (b[0] - a[0]) * distance / length
            y = a[1] + (b[1] - a[1]) * distance / length
            radius = 8 * scale
            inner = 2.5 * scale
            d.ellipse((x-radius, y-radius, x+radius, y+radius), fill='white', outline=color, width=max(1, round(2*scale)))
            d.ellipse((x-inner, y-inner, x+inner, y+inner), fill=color)
            return
        distance -= length

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
SOURCE=ROOT/'.archify/workflow-setup-gitflow/setup-gitflow.html'
W,H,FPS=1920,1080,15
SCALE=1760/1138
DX,DY=80,88
GREEN,RED,PURPLE='#059669','#e11d48','#7c3aed'

# Extract all node rectangles and connector points directly from the source SVG.
html=SOURCE.read_text()
svg=re.search(r'<svg viewBox="0 0 1138 660".*?</svg>',html,re.S).group(0)
tree=ET.fromstring(svg)
nodes={}
edges={}
for el in tree.iter():
    if el.tag=='g' and el.get('data-node-id'):
        rect=el.find('rect')
        nodes[el.get('data-node-id')]=tuple(float(rect.get(a)) for a in ('x','y','width','height'))
    if el.tag=='path' and el.get('data-composition-points'):
        edges[el.get('data-edge-id')]=[tuple(map(float,p.split(','))) for p in el.get('data-composition-points').split(';')]

# Resolve Archify's classic light palette into standalone SVG styles.
light=re.search(r'\[data-theme="light"\]\s*\{(.*?)\}',html,re.S).group(1)
tokens=dict(re.findall(r'--([\w-]+)\s*:\s*([^;]+);',light))
css=[]
classes=set(re.findall(r'class="([^"]+)"',svg))
for clist in classes:
    for cls in clist.split():
        match=re.search(r'(?<![\w-])\.'+re.escape(cls)+r'\s*\{([^}]+)\}',html)
        if match:
            body=re.sub(r'var\(--([\w-]+)\)',lambda m:tokens.get(m[1],'#94a3b8'),match[1])
            css.append('.'+cls+' {'+body+'}')
css.append('text {font-family: "Menlo", monospace;}')
css.append('.c-lane {fill:rgba(248,250,252,.65);stroke:#cbd5e1;stroke-dasharray:6,6;}')
css.append('.semantic-sigil {fill:none; stroke:currentColor; stroke-width:1.35; stroke-linecap:round; stroke-linejoin:round; opacity:.76;}')
for kind in ['backend','security','database','cloud']:
    css.append('.s-'+kind+' {color:'+tokens[kind+'-stroke']+';}')

# Clip only unused whitespace below the authored swimlanes; keep every coordinate.
svg=svg.replace('<svg viewBox="0 0 1138 660"', '<svg xmlns="http://www.w3.org/2000/svg" width="1760" height="836" viewBox="0 0 1138 540"',1)
svg=svg.replace('<!-- Definitions -->','<style>'+''.join(css)+'</style><!-- Definitions -->',1)
svg=re.sub(r'(<title id="archify-diagram-title">).*?(</title>)',r'\1Multica setup - git flow\2',svg,flags=re.S)
svg=re.sub(r'<pattern id="grid".*?</pattern>',
    '<pattern id="grid" width="12" height="12" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".5" fill="#d9dee5"/></pattern>',svg,flags=re.S)
BASE=Image.open(io.BytesIO(resvg_py.svg_to_bytes(svg_string=svg,width=1760,height=836,background='white'))).convert('RGB')

SCENES=[
 (3,None,None,'Git flow','Follow the original Archify layout: commit → review → release → sync to live.'),
 (4,'commit',None,'1  Fix Commit','The steward creates one focused commit per Fix Issue, scoped to the drunk bundle.'),
 (4,'devtip','commit-push','2  Push to dev','Push HEAD:refs/heads/dev, then verify the remote tip with git ls-remote.'),
 (4,'pr','dev-pr','3  Open or update the PR','Reuse one open dev → main pull request and wait for the owner.'),
 (4,'review','pr-review','4  Owner Review','The owner approves or rejects. Only the owner can merge to main.'),
 (4,'merge','review-merge','5  Merge to main','The owner merges; the push triggers a GitHub Action and the sync run.'),
 (4,'diff','merge-sync','6  Sync and verify','Compare live/drunk..origin/main, apply the changes, then verify with lock + read-back checks.'),
 (4,'moved','diff-move','7  Move the verified live tag','Only when all read-back checks agree: move and push live/drunk to main.'),
 (5,'commit','review-reject','Recovery  •  Owner rejects','Return to Fix Commit, update the same PR, and request owner review again.'),
 (5,'manual','diff-blocked','Recovery  •  Sync blocked','Unsupported changes require manual steps. The live/drunk tag stays put.'),
 (5,'moved','manual-accept','Recovery  •  Apply manual steps and retry','Rerun --accept after the manual steps; verify the result before advancing the tag.'),
 (4,None,None,'Owner approval. Verified sync. A traceable live state.','On any failure, the tag stays put so the next run retries the same commit range.'),
]
DURATION=sum(s[0] for s in SCENES)

def current(t):
    start=0
    for duration,node,edge,title,caption in SCENES:
        if t<start+duration:
            return duration,node,edge,title,caption,t-start
        start+=duration
    return (*SCENES[-1],0)

def frame(t,still=False):
    duration,node,edge,title,caption,local=current(t)
    if still:
        node=edge=None
        title='Owner approval. Verified sync. A traceable live state.'
        caption='The workflow preserves human merge control and moves the live tag only after verification.'
    im=Image.new('RGB',(W,H),'#f4f5f7')
    d=ImageDraw.Draw(im)
    text(d,(80,29),'Multica setup - git flow',30,NAVY,True)
    im.paste(BASE,(DX,DY))
    d=ImageDraw.Draw(im)
    if node:
        color=RED if edge in ['review-reject','diff-blocked'] else PURPLE if node=='moved' else GREEN
        x,y,w,h=nodes[node]
        x,y,w,h=DX+x*SCALE,DY+y*SCALE,w*SCALE,h*SCALE
        # Outline sits outside the node and never obscures its labels.
        pad=6+2*math.sin(local*math.pi)
        d.rounded_rectangle((x-pad,y-pad,x+w+pad,y+h+pad),radius=14,outline=color,width=4)
        if edge:
            points=[(DX+a*SCALE,DY+b*SCALE) for a,b in edges[edge]]
            # The marker travels along the exact authored connector route.
            dot_on_path(d,points,min(local/2.5,1),color)
    d.rounded_rectangle((80,943,1840,1049),radius=12,fill=NAVY)
    text(d,(104,960),title,27,'white',True)
    text(d,(104,1003),caption,22,'#DAE3EF')
    if not still:
        d.rectangle((80,1045,80+1760*t/DURATION,1049),fill=GREEN)
    return im

GIF_SIZE = (1440, 810)
GIF_FPS = 50  # GIF timing uses 10 ms ticks; 20 ms is an exact frame duration.
GIF_SECONDS = 4

def render_gif():
    # Use one clock for every connector, independent of the narrated scenes.
    # Draw at twice the export resolution for antialiased, subpixel motion.
    scale = 2 * GIF_SIZE[0] / W
    size = tuple(v * 2 for v in GIF_SIZE)
    background = frame(0, True).resize(size, Image.Resampling.LANCZOS)
    routes = {
        edge_id: [(scale*(DX+x*SCALE), scale*(DY+y*SCALE)) for x,y in points]
        for edge_id, points in edges.items()
    }
    palette_source = background.copy()
    draw = ImageDraw.Draw(palette_source)
    for i, color in enumerate((GREEN, RED, PURPLE, 'white')):
        draw.rectangle((i*40, 0, (i+1)*40-1, 39), fill=color)
    palette = palette_source.resize(GIF_SIZE, Image.Resampling.LANCZOS).quantize(colors=256)
    frames = []
    for n in range(GIF_SECONDS * GIF_FPS):
        phase = n / (GIF_SECONDS * GIF_FPS)
        # Ease departure/arrival and fade across the reset for a seamless loop.
        progress = phase * phase * (3 - 2 * phase)
        opacity = min(1, phase / 0.04, (1 - phase) / 0.04)
        canvas = background.copy()
        draw = ImageDraw.Draw(canvas)
        for edge_id, points in routes.items():
            color = RED if edge_id in ('review-reject', 'diff-blocked', 'sync-blocked') else GREEN
            dot_on_path(draw, points, progress, color, scale)
        if opacity < 1:
            canvas = Image.blend(background, canvas, opacity)
        frames.append(canvas.resize(GIF_SIZE, Image.Resampling.LANCZOS).quantize(
            palette=palette, dither=Image.Dither.NONE))
    frames[0].save(OUT/'gitflow-archify-animation.gif', save_all=True,
        append_images=frames[1:], duration=1000//GIF_FPS, loop=0,
        optimize=True, disposal=1)
    print(f'GIF complete: {len(routes)} synchronized arrows, {GIF_SECONDS}s, {GIF_FPS} fps', flush=True)

def main(gif_only=False):
    if gif_only:
        render_gif()
        return
    (OUT/'gitflow-archify-layout.svg').write_text(svg)
    frame(0,True).save(OUT/'gitflow-archify-overview.png')
    proc=subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-f','rawvideo','-vcodec','rawvideo',
      '-s',f'{W}x{H}','-pix_fmt','rgb24','-r',str(FPS),'-i','-',
      '-an','-vcodec','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p',
      '-movflags','+faststart',str(OUT/'gitflow-archify-animation.mp4')],stdin=subprocess.PIPE,stderr=subprocess.DEVNULL)
    for n in range(DURATION*FPS):
        im=frame(n/FPS)
        proc.stdin.write(im.tobytes())
        if n%(FPS*5)==0:
            print(f'Rendered {n/FPS:.0f}/{DURATION}s',flush=True)
    proc.stdin.close()
    if proc.wait()!=0: raise RuntimeError('Video export failed')
    render_gif()
    print(f'Complete: {DURATION}s video',flush=True)

if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--gif-only', action='store_true', help='Regenerate only the synchronized GIF')
    main(parser.parse_args().gif_only)
