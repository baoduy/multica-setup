"""Render a presentation animation from the proposed Archify Git flow.

Run with Pillow and imageio-ffmpeg installed. No source diagram is modified.
"""
from pathlib import Path
import math
import subprocess
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

OUT = Path(__file__).resolve().parent
W, H, FPS = 1920, 1080, 15
NAVY, MUTED = '#172A43', '#64748B'
TEAL, BLUE, AMBER = '#008775', '#3463CB', '#BC6814'
BG, LINE = '#F4F7FB', '#D5DFEB'
FONT = '/System/Library/Fonts/Supplemental/Arial.ttf'
BOLD = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'

def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else FONT, size)

STEPS = [
    ('Fix & push', 'Agent / dev branch', ['One commit per fix issue', 'Push directly to dev'], TEAL),
    ('Open / update PR', 'dev → main', ['Reuse one open PR', 'Wait for owner review'], TEAL),
    ('Owner review', 'Human approval gate', ['Approve or reject', 'Only the owner merges'], BLUE),
    ('Merge to main', 'Approved release', ['Owner merges the PR', 'Push triggers GitHub Action'], BLUE),
    ('Sync workspace', 'Automatic sync', ['Diff live/drunk..origin/main', 'Lock + read-back checks'], TEAL),
    ('Confirm live', 'Verified release marker', ['Move tag after verification', 'live/drunk matches main'], TEAL),
]
SCENES = [
    (3, -1, 'A controlled path from fix to live', 'Agent prepares changes. The owner approves. Sync verifies the live workspace.'),
    (4, 0, '01  Prepare a focused fix', 'The agent commits on dev and pushes an explicit refspec; dev is never force-pushed.'),
    (4, 1, '02  Keep review in one pull request', 'Open or update the existing dev → main PR, then wait for the owner.'),
    (4, 2, '03  Keep release approval with the owner', 'The owner reviews the change and decides whether to approve or request another fix.'),
    (4, 3, '04  Merge the approved change', 'Only the owner merges to main. The push triggers a GitHub Action and the sync run.'),
    (4, 4, '05  Apply and verify the live changes', 'drunk-live-sync.py compares the live tag with origin/main and verifies the result by read-back.'),
    (4, 5, '06  Record the verified live state', 'Only after all read-back checks agree, move and push the live/drunk tag to main.'),
    (5, 6, 'Recovery path  •  Review rejected', 'Return to the fix step, update the same PR, and ask the owner to review again.'),
    (5, 7, 'Recovery path  •  Sync blocked', 'Apply the manual steps for unsupported changes, then rerun with --accept and verify before moving the tag.'),
    (5, 8, 'Human control. Verified sync. A traceable live state.', 'On any failure, the live tag stays put so the next run retries the same commit range.'),
]
DURATION = sum(s[0] for s in SCENES)

def text(d, xy, value, size=24, color=NAVY, bold=False):
    d.text(xy, value, font=font(size, bold), fill=color)

def center(d, x, y, value, size=24, color=NAVY, bold=False):
    f = font(size, bold)
    d.text((x - d.textlength(value, font=f)/2, y), value, font=f, fill=color)

def path(d, pts, color, width=4, dashed=False):
    for a, b in zip(pts, pts[1:]):
        length = math.dist(a, b)
        if dashed:
            for dist in range(0, int(length), 20):
                end = min(dist+10, length)
                p = tuple(a[j]+(b[j]-a[j])*dist/length for j in (0,1))
                q = tuple(a[j]+(b[j]-a[j])*end/length for j in (0,1))
                d.line([p,q], fill=color, width=width)
        else:
            d.line([a,b], fill=color, width=width)
    a,b=pts[-2:]
    angle=math.atan2(b[1]-a[1],b[0]-a[0])
    d.polygon([b, (b[0]-13*math.cos(angle-.5), b[1]-13*math.sin(angle-.5)),
               (b[0]-13*math.cos(angle+.5), b[1]-13*math.sin(angle+.5))], fill=color)

def dot_on_path(d, pts, fraction, color):
    lengths=[math.dist(a,b) for a,b in zip(pts,pts[1:])]
    dist=sum(lengths)*fraction
    for a,b,length in zip(pts,pts[1:],lengths):
        if dist<=length:
            x=a[0]+(b[0]-a[0])*dist/length
            y=a[1]+(b[1]-a[1])*dist/length
            d.ellipse((x-15,y-15,x+15,y+15),fill='white',outline=color,width=4)
            d.ellipse((x-5,y-5,x+5,y+5),fill=color)
            return
        dist-=length

def scene_at(t):
    start=0
    for duration, active, title, subtitle in SCENES:
        if t<start+duration:
            return active, title, subtitle, t-start, duration
        start+=duration
    return 8, SCENES[-1][2], SCENES[-1][3], 4.9, 5

def render(t, overview=False):
    active,title,subtitle,local,duration=scene_at(t)
    if overview:
        active=8
        title='Human control. Verified sync. A traceable live state.'
        subtitle='Owner approval governs release. The live tag advances only after successful verification.'
    im=Image.new('RGB',(W,H),BG)
    d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,12),fill=TEAL)
    text(d,(80,55),'MULTICA SETUP  /  DELIVERY WORKFLOW',22,TEAL,True)
    text(d,(80,105),'From fix to a verified live workspace',54,NAVY,True)
    text(d,(82,181),'A clear approval gate, automated sync, and safe recovery paths',28,MUTED)
    d.rounded_rectangle((1642, sixty:=60,1840,104),radius=22,fill='#E8EDF6')
    center(d,1741,70,'PROPOSED FLOW',19,BLUE,True)

    phases=[(80,626,'01  PREPARE',TEAL),(668,920,'02  APPROVE',BLUE),
            (962,1214,'03  RELEASE',BLUE),(1256,1802,'04  SYNC & VERIFY',TEAL)]
    for x,end,label,color in phases:
        text(d,(x,270),label,20,color,True)
        d.line((x,307,end,307),fill=LINE,width=3)

    y,ch,cw=346,211,252
    xs=[80+i*294 for i in range(6)]
    for i,(label,role,lines,color) in enumerate(STEPS):
        x=xs[i]
        selected=active==i
        done=active==8 or (0<=active<=5 and i<active)
        border=color if selected or done else LINE
        fill='#EAF6F3' if selected and color==TEAL else '#EDF2FE' if selected else 'white'
        d.rounded_rectangle((x,y+5,x+cw,y+ch+5),radius=16,fill='#E5EBF3')
        d.rounded_rectangle((x,y,x+cw,y+ch),radius=16,fill=fill,outline=border,width=4 if selected else 2)
        d.ellipse((x+20,y+20,x+60,y+60),fill=color if selected or done else '#E9EEF5')
        center(d,x+40,y+27,str(i+1),22,'white' if selected or done else MUTED,True)
        text(d,(x+20,y+76),label,25,NAVY,True)
        text(d,(x+20,y+112),role,19,color,True)
        for j,line in enumerate(lines):
            text(d,(x+20,y+150+j*25),line,17,MUTED)
        if i<5:
            pts=[(x+cw+5,y+104),(xs[i+1]-8,y+104)]
            path(d,pts,TEAL if done else LINE,4)
            if active==i+1 and local<1.5:
                dot_on_path(d,pts,min(local/1.5,1),TEAL)
        if selected:
            d.rounded_rectangle((x+18,y+ch+18,x+cw-18,y+ch+23),radius=2,fill=LINE)
            d.rounded_rectangle((x+18,y+ch+18,x+18+(cw-36)*min(local/duration,1),y+ch+23),radius=2,fill=color)

    # Exception cards retain the recovery semantics without crossing the main flow.
    recoveries=[(80,840,6,'Review rejected','Fix again → update the same PR → owner review',BLUE),
                (1016,1802,7,'Sync blocked','Manual steps → rerun --accept → verify → move tag',AMBER)]
    for x,end,which,label,detail,color in recoveries:
        selected=active==which
        d.rounded_rectangle((x,661,end,777),radius=14,fill='#FFF5E8' if selected and which==7 else '#EDF2FE' if selected else 'white',outline=color if selected else LINE,width=3 if selected else 2)
        text(d,(x+24,680),label,25,color,True)
        text(d,(x+24,727),detail,22,MUTED)
    reject=[(xs[2]+126,562),(xs[2]+126,618),(xs[0]+126,618),(xs[0]+126,562)]
    blocked=[(xs[4]+126,562),(xs[4]+126,650)]
    path(d,reject,BLUE if active==6 else LINE,3,True)
    path(d,blocked,AMBER if active==7 else LINE,3,True)
    if active==6:
        dot_on_path(d,reject,(local/3)%1,BLUE)
    if active==7:
        dot_on_path(d,blocked,(local/2)%1,AMBER)
    text(d,(1016,794),'On any failure: tag stays put; retry the same range.',20,MUTED)

    d.rounded_rectangle((80,852,1840,1004),radius=20,fill=NAVY)
    text(d,(112,878),title,32,'white',True)
    # Keep the explanatory caption comfortably within the 16:9 canvas.
    words=subtitle.split(); lines=[]; line=''
    for word in words:
        trial=(line+' '+word).strip()
        if d.textlength(trial,font=font(25))>1680:
            lines.append(line); line=word
        else: line=trial
    lines.append(line)
    for j,line in enumerate(lines):
        text(d,(112,930+j*31),line,25,'#CCD8E8')
    text(d,(80,1031),'SOURCE  .archify/workflow-setup-gitflow  •  Proposed workflow',17,MUTED)
    text(d,(1520,1031),'OWNER CONTROL  /  VERIFIED LIVE',17,MUTED,True)
    if not overview:
        d.rectangle((0,H-5,W*t/DURATION,H),fill=TEAL)
    return im

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    render(40,True).save(OUT/'gitflow-overview.png')
    # Constant-rate H.264 video for common presentation applications.
    video=OUT/'gitflow-presentation.mp4'
    proc=subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-f','rawvideo','-vcodec','rawvideo',
        '-s',f'{W}x{H}','-pix_fmt','rgb24','-r',str(FPS),'-i','-',
        '-an','-vcodec','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p',
        '-movflags','+faststart',str(video)],stdin=subprocess.PIPE,stderr=subprocess.DEVNULL)
    gif_frames=[]
    for n in range(DURATION*FPS):
        im=render(n/FPS)
        proc.stdin.write(im.tobytes())
        if n%3==0:
            gif_frames.append(im.resize((1280,720),Image.Resampling.LANCZOS))
        if n%(FPS*5)==0:
            print(f'Rendered {n/FPS:.0f}/{DURATION}s',flush=True)
    proc.stdin.close()
    if proc.wait()!=0:
        raise RuntimeError('Video export failed')
    # One shared palette avoids color flicker between frames.
    palette=render(40,True).resize((1280,720)).quantize(colors=128)
    frames=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in gif_frames]
    frames[0].save(OUT/'gitflow-presentation.gif',save_all=True,append_images=frames[1:],
                   duration=200,loop=0,optimize=True,disposal=1)
    for idx,t in enumerate([5,13,21,29,34,40]):
        render(t).resize((960,540)).save(OUT/f'preview-{idx+1}.png')
    print(f'Complete: {DURATION}s; {len(frames)} GIF frames; {video}',flush=True)

if __name__=='__main__':
    main()
