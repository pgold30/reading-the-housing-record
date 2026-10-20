"""Build cinematic video using Google's native AI voice (Audio Overview from NotebookLM)
and verified site charts/footage.

Matches duration to Google AI voice: 97.8 seconds.
"""
import subprocess, sys, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

AUDIO_PATH = Path('/Users/pablo/Downloads/Fixing_Flawed_NYC_Housing_Data.m4a')
SRC = Path('/Users/pablo/Downloads/The_Anatomy_of_a_Public_Record.mp4')
SITE = Path('/Users/pablo/Documents/ChatGPT/papers/research-site-stories')
OUT = SITE / 'assets' / 'media'

TMP = Path('/tmp/omni_video_build')
if TMP.exists():
    shutil.rmtree(TMP)
TMP.mkdir(parents=True, exist_ok=True)

SANS = '/System/Library/Fonts/Supplemental/Arial.ttf'
SERIF = '/System/Library/Fonts/Supplemental/Georgia Bold.ttf'
W, H, FPS, FADE = 1280, 720, 25, 0.40

# Total duration = 97.8s
# (kind, chart_rel_path, start_time, duration, caption, style)
SEGMENTS = [
    (
        'clip', None, 0.3, 6.5,
        "New York's Housing Records: How the Studies Connect",
        'title'
    ),
    (
        'clip', None, 24.8, 7.0,
        "Public records govern taxes, price indices, and housing policies. But raw records hide critical caveats.",
        'cap'
    ),
    (
        'clip', None, 8.8, 7.0,
        "Shared records: 729,000 city sales linked to ACRIS deeds and mortgages under fixed, documented rules.",
        'cap'
    ),
    (
        'chart', 'stories/condo-coverage.png', 0, 7.5,
        "Why it matters: Fixed matching links 96% of Brooklyn condo sales to a deed, but only 52% in the Bronx.",
        'cap'
    ),
    (
        'clip', None, 71.2, 7.0,
        "What is the amount? Foreclosure deeds to lenders record statutory debt or bids, not market prices.",
        'cap'
    ),
    (
        'chart', 'stories/deed-index-paths.png', 0, 7.5,
        "Why it matters: Counted as sales, they shift price index timing around 2010. The true crash depth barely changes.",
        'cap'
    ),
    (
        'clip', None, 109.3, 7.0,
        "Who buys, and with what financing? Cash purchases appear about 9% cheaper than mortgaged sales.",
        'cap'
    ),
    (
        'chart', 'stories/cash-discount.png', 0, 7.5,
        "Why it matters: Half the gap disappears when family transfers are screened. Company cash discounts are near zero.",
        'cap'
    ),
    (
        'clip', None, 145.6, 7.0,
        "What happens at a tax line? The 2019 whole-price notches add about $5,000 for just $1 over $2 million.",
        'cap'
    ),
    (
        'chart', 'stories/tax-dollar-step.png', 0, 7.5,
        "Why it matters: Sales bunch below the cliff (4 to 127 at $1,999,999). Marginal slice rates raise revenue without cliffs.",
        'cap'
    ),
    (
        'clip', None, 228.8, 7.0,
        "A separate simulation tests the measures: In allocation simulations, the benchmark moves with policy.",
        'cap'
    ),
    (
        'chart', 'fig/wedge-benchmark-v6-4.png', 0, 7.5,
        "Why it matters: A moving benchmark can show policy gains while real value falls. A fixed cohort restores true rankings.",
        'cap'
    ),
    (
        'clip', None, 236.2, 6.5,
        "How the numbers help: Collect 0.88% on purchase prices, charge progressive tax slices, and publish deed numbers with sales.",
        'cap'
    ),
    (
        'clip', None, 290.5, 5.3,
        "Explore the transactions, papers, and code",
        'end'
    ),
]


def caption_png(caption, style, tag):
    import textwrap
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if style == 'cap':
        font = ImageFont.truetype(SANS, 32)
        lines = textwrap.wrap(caption, 60)
        lh = 44
        band = lh * len(lines) + 40
        d.rectangle([0, H - band, W, H], fill=(15, 30, 42, 215))
        y = H - band + 20
        for ln in lines:
            w = d.textlength(ln, font=font)
            d.text(((W - w) / 2, y), ln, font=font, fill='white')
            y += lh
    else:
        sub = ('How the studies connect · Independent research by Pablo Loschi' if style == 'title'
               else 'nychousingdata.com · Independent research by Pablo Loschi')
        d.rectangle([0, H / 2 - 110, W, H / 2 + 110], fill=(15, 30, 42, 185))
        ft = ImageFont.truetype(SERIF, 48)
        fs = ImageFont.truetype(SANS, 26)
        w = d.textlength(caption, font=ft)
        d.text(((W - w) / 2, H / 2 - 62), caption, font=ft, fill='white')
        w = d.textlength(sub, font=fs)
        d.text(((W - w) / 2, H / 2 + 26), sub, font=fs, fill=(219, 231, 238))
    p = TMP / f'{tag}_cap.png'
    img.save(p)
    return p


def chart_frame(rel_path, tag):
    im = Image.open(SITE / 'assets' / rel_path).convert('RGB')
    cw, ch = 2560, 1440
    canvas = Image.new('RGB', (cw, ch), 'white')
    maxw, maxh = 2260, 1100
    s = min(maxw / im.width, maxh / im.height)
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    canvas.paste(im, ((cw - im.width) // 2, 40))
    p = TMP / f'{tag}.png'
    canvas.save(p)
    return p


print("Building video segments...")
parts = []
total_time = sum(s[3] for s in SEGMENTS)
print(f"Total video segments duration: {total_time:.2f}s (target: 97.8s)")

for i, (kind, rel_path, start, dur, caption, style) in enumerate(SEGMENTS, 1):
    tag = f'seg{i:02d}'
    print(f"[{i:02d}/{len(SEGMENTS):02d}] {kind} ({dur:.1f}s): {caption[:35]}...")
    cap = caption_png(caption, style, tag)
    fades = f"fade=t=in:st=0:d={FADE},fade=t=out:st={dur - FADE:.2f}:d={FADE}"
    
    if kind == 'clip':
        base = f"[0:v]scale={W}:{H},fps={FPS}[b]"
        inputs = ['-ss', str(start), '-t', str(dur), '-i', str(SRC)]
    else:
        img = chart_frame(rel_path, tag)
        frames = int(dur * FPS)
        base = (f"[0:v]zoompan=z='1+0.035*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                f"d={frames}:s={W}x{H}:fps={FPS}[b]")
        inputs = ['-loop', '1', '-framerate', str(FPS), '-t', f'{dur:.2f}', '-i', str(img)]
    
    fc = f"{base};[b][1:v]overlay=0:0,{fades},format=yuv420p[v]"
    out = TMP / f'{tag}.mp4'
    cmd = ['ffmpeg', '-v', 'error', '-y'] + inputs + [
        '-loop', '1', '-i', str(cap),
        '-filter_complex', fc,
        '-map', '[v]', '-an',
        '-t', f'{dur:.2f}',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '20',
        str(out)
    ]
    subprocess.run(cmd, check=True)
    parts.append(out)

# Concat video
lst = TMP / 'list.txt'
lst.write_text(''.join(f"file '{p}'\n" for p in parts))
video_no_audio = TMP / 'video_concat.mp4'

print("Concatenating video stream...")
subprocess.run([
    'ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(lst),
    '-c:v', 'copy', str(video_no_audio)
], check=True)

# Mux with Google AI audio
final_video = OUT / 'how-the-studies-connect.mp4'
poster_img = OUT / 'how-the-studies-connect-poster.jpg'
downloads_dest = Path('/Users/pablo/Downloads/how-the-studies-connect-google-voice.mp4')

print(f"Muxing with Google AI audio: {AUDIO_PATH}...")
afade = "afade=t=in:ss=0:d=0.3,afade=t=out:st=96.8:d=1.0"
subprocess.run([
    'ffmpeg', '-v', 'error', '-y',
    '-i', str(video_no_audio),
    '-i', str(AUDIO_PATH),
    '-filter_complex', f"[1:a]{afade}[a]",
    '-map', '0:v', '-map', '[a]',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '21',
    '-c:a', 'aac', '-b:a', '192k',
    '-shortest',
    '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
    str(final_video)
], check=True)

# Generate poster at 2.5s
subprocess.run([
    'ffmpeg', '-v', 'error', '-y', '-ss', '2.5', '-i', str(final_video),
    '-frames:v', '1', '-q:v', '3', str(poster_img)
], check=True)

# Sync with dist & Downloads
dist_media = SITE / 'dist' / 'assets' / 'media'
dist_media.mkdir(parents=True, exist_ok=True)
shutil.copy2(final_video, dist_media / final_video.name)
shutil.copy2(poster_img, dist_media / poster_img.name)
shutil.copy2(final_video, downloads_dest)

print("\nSUCCESS!")
print(f"Final video: {final_video} ({final_video.stat().st_size / (1024*1024):.1f} MB)")
print(f"Downloads copy: {downloads_dest}")
