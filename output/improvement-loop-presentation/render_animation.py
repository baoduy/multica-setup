"""Animate Archify's native SVG without changing its authored geometry."""
from pathlib import Path
import io
import re
import math
import subprocess
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont
import resvg_py
import imageio_ffmpeg

NAVY, MUTED = '#172A43', '#64748B'
FONT = '/System/Library/Fonts/Supplemental/Arial.ttf'
BOLD = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'

def text(d, xy, value, size=24, color=NAVY, bold=False):
    d.text(xy, value, font=ImageFont.truetype(BOLD if bold else FONT, size), fill=color)

def dot_on_path(d, points, fraction, color):
    lengths = [math.dist(a, b) for a, b in zip(points, points[1:])]
    distance = sum(lengths) * fraction
    for a, b, length in zip(points, points[1:], lengths):
        if distance <= length:
            x = a[0] + (b[0] - a[0]) * distance / length
            y = a[1] + (b[1] - a[1]) * distance / length
            d.ellipse((x-15, y-15, x+15, y+15), fill='white', outline=color, width=4)
            d.ellipse((x-5, y-5, x+5, y+5), fill=color)
            return
        distance -= length

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
SOURCE=ROOT/'.archify/workflow-setup-improvement-loop/setup-improvement-loop.html'
W,H,FPS=1920,1080,15
SCALE=836/590
DIAGRAM_W=round(1081*SCALE)
DX,DY=(W-DIAGRAM_W)//2,88
GREEN,RED,PURPLE='#059669','#e11d48','#7c3aed'

# Extract all node rectangles and connector points directly from the source SVG.
html=SOURCE.read_text()
svg=re.search(r'<svg viewBox="0 0 1081 660".*?</svg>',html,re.S).group(0)
# Generic presentation labels; original SVG geometry is preserved.
REPLACEMENTS={
    'multica-setup Improvement Loop (proposed, drunk-workspace)': 'Multica setup - Improvement loop',
    'GitHub baoduy/multica-setup': 'GitHub setup repository',
    'Agents on this PC runtime': 'Agent runtime',
    'drunk-setup project': 'Workspace setup project',
    'setup-steward, drunk only': 'setup-steward, scoped fixes',
    'setup-steward, Mon 09:00': 'setup-steward, weekly',
    'claude_ultra Sync': 'Sync Agent',
    'sync-live.py from main': 'sync resources from main',
    'multica-api.st24.live': 'Workspace API',
}
for old,new in REPLACEMENTS.items():
    svg=svg.replace(old,new)
assert 'drunk' not in svg.lower()
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
for kind in ['backend','security','database','cloud','messagebus','external']:
    css.append('.s-'+kind+' {color:'+tokens[kind+'-stroke']+';}')

# Clip only unused whitespace below the authored swimlanes; keep every coordinate.
svg=svg.replace('<svg viewBox="0 0 1081 660"', '<svg xmlns="http://www.w3.org/2000/svg" width="1532" height="836" viewBox="0 0 1081 590"',1)
svg=svg.replace('<!-- Definitions -->','<style>'+''.join(css)+'</style><!-- Definitions -->',1)
svg=re.sub(r'(<title id="archify-diagram-title">).*?(</title>)',r'\1Multica setup - Improvement loop\2',svg,flags=re.S)
svg=re.sub(r'<pattern id="grid".*?</pattern>',
    '<pattern id="grid" width="12" height="12" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".5" fill="#d9dee5"/></pattern>',svg,flags=re.S)
(OUT/'improvement-loop-layout.svg').write_text(svg)
BASE=Image.open(io.BytesIO(resvg_py.svg_to_bytes(svg_string=svg,width=DIAGRAM_W,height=836,background='white'))).convert('RGB')

SCENES=[
 (2,None,None,'Continuous improvement, from evidence to release','Monitor live runs, turn recurring problems into fixes, then review and sync the improvements.'),
 (3,'runs',None,'1  Observe live agent runs','Squads, gates, and autopilots produce the evidence for the next improvement cycle.'),
 (3,'signals','runs-emit','2  Capture run signals','Record gate rounds, scores, and failures so recurring problems are visible.'),
 (3,'retro','signals-read','3  Run the weekly retrospective','The setup steward reviews seven days of signals and groups repeated problems.'),
 (3,'issues','retro-open','4  Create focused fix issues','Create one issue per problem in the workspace setup project.'),
 (3,'fix','issue-assign','5  Fix or revert','Assign the issue to the setup steward and make a change within the agreed scope.'),
 (3,'dev','fix-commit','6  Commit to dev','Push the focused fix to the dev branch with an explicit refspec.'),
 (3,'pr','dev-pr','7  Open or update the pull request','Reuse one open dev → main PR and keep the issue waiting for owner review.'),
 (3,'review','pr-review','8  Owner review','The owner approves or rejects the change. Only the owner merges to main.'),
 (3,'main','review-merge','9  Merge and trigger release','The approved merge triggers a GitHub Action, which calls the sync webhook.'),
 (3,'hook','main-webhook','10  Start the sync autopilot','The webhook starts the autopilot, creates a sync issue, and assigns the sync agent.'),
 (3,'sync','hook-run','11  Sync and verify','The sync agent applies the approved resources from main and performs exact read-back checks.'),
 (3,'runs','sync-live','Close the loop  •  Improvements are live','After successful verification, the live tag advances and agent runs use the updated setup.'),
 (4,'issues','review-reject','Recovery  •  Owner requests changes','The owner comments on the fix issue; revise the change and return it for review.'),
 (4,'blocked','sync-blocked','Recovery  •  Unsupported sync change','Block the sync issue and list the manual steps. Keep the live tag unchanged until verification succeeds.'),
 (4,None,None,'Observe. Improve. Review. Sync. Repeat.','Run evidence drives focused fixes, owner approval controls release, and verification confirms the live state.'),
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
        title='Observe. Improve. Review. Sync. Repeat.'
        caption='Run evidence drives focused fixes, owner approval controls release, and verification confirms the live state.'
    im=Image.new('RGB',(W,H),'#f4f5f7')
    d=ImageDraw.Draw(im)
    text(d,(80,29),'Multica setup - Improvement loop',30,NAVY,True)
    im.paste(BASE,(DX,DY))
    d=ImageDraw.Draw(im)
    if node:
        color=RED if edge in ['review-reject','sync-blocked'] else PURPLE if node=='moved' else GREEN
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

def main():
    frame(0,True).save(OUT/'improvement-loop-overview.png')
    proc=subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-f','rawvideo','-vcodec','rawvideo',
      '-s',f'{W}x{H}','-pix_fmt','rgb24','-r',str(FPS),'-i','-',
      '-an','-vcodec','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p',
      '-movflags','+faststart',str(OUT/'improvement-loop-animation.mp4')],stdin=subprocess.PIPE,stderr=subprocess.DEVNULL)
    gif=[]
    for n in range(DURATION*FPS):
        im=frame(n/FPS)
        proc.stdin.write(im.tobytes())
        if n%3==0:
            gif.append(im.resize((1440,810),Image.Resampling.LANCZOS))
        if n%(FPS*5)==0:
            print(f'Rendered {n/FPS:.0f}/{DURATION}s',flush=True)
    proc.stdin.close()
    if proc.wait()!=0: raise RuntimeError('Video export failed')
    palette=frame(0,True).resize((1440,810)).quantize(colors=192)
    frames=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in gif]
    frames[0].save(OUT/'improvement-loop-animation.gif',save_all=True,append_images=frames[1:],
      duration=40,loop=0,optimize=True,disposal=1)
    print(f'Complete: {DURATION}s video; {DURATION/5:g}s GIF; {len(frames)} GIF frames',flush=True)

if __name__=='__main__': main()
