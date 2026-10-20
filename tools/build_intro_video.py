"""Build the site's intro video from number-free scenes of the NotebookLM render and the site's own charts.

Every figure in the captions comes from the papers (tax v3.2, house v3.9, deed v1.0.11, dataset v1.1.0).
Usage: python build_intro.py SOURCE_VIDEO SITE_DIR OUT_DIR
"""
import subprocess, sys, textwrap
from pathlib import Path
from PIL import Image

SRC, SITE, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
TMP = OUT / 'parts'; TMP.mkdir(parents=True, exist_ok=True)
SANS = '/System/Library/Fonts/Supplemental/Arial.ttf'
SERIF = '/System/Library/Fonts/Supplemental/Georgia Bold.ttf'
W, H, FPS, FADE = 1280, 720, 25, 0.45

# (kind, source, start, length, slow, caption, style)
SEGMENTS = [
    ('clip', None, 0.3, 6.0, 1.0, "New York's housing records, explained", 'title'),
    ('clip', None, 8.8, 2.5, 1.6, "Two buyers. The same $900,000 condo in Queens.", 'cap'),
    ('chart', 'mortgage-recording-comparison.png', 0, 7.0, 1, "The buyer who borrows $720,000 owes $13,860 in mortgage recording tax. The cash buyer owes none.", 'cap'),
    ('clip', None, 24.8, 4.7, 1.0, "Ten years of city sales, 2016 to 2025, linked to the deeds and mortgages filed with them.", 'cap'),
    ('clip', None, 71.2, 6.0, 1.0, "Some deeds record an amount set by law, such as a lender's foreclosure bid, not a price.", 'cap'),
    ('chart', 'deed-index-paths.png', 0, 7.0, 1, "Counted as sales, they shift the timing of a house-price index around 2010. The size of the crash barely changes.", 'cap'),
    ('clip', None, 109.3, 6.0, 1.0, "Houses bought for cash look about 9% cheaper than the same houses bought with a mortgage.", 'cap'),
    ('chart', 'cash-discount.png', 0, 7.5, 1, "About half of that gap disappears once sales between people who share a surname are set aside. For company buyers, what remains is too small to tell from zero.", 'cap'),
    ('clip', None, 145.6, 4.0, 1.0, "Since 2019, some New York buyer taxes jump on the whole price at round numbers.", 'cap'),
    ('chart', 'tax-dollar-step.png', 0, 6.0, 1, "One dollar over $2 million adds about $5,000 in buyer tax.", 'cap'),
    ('clip', None, 149.9, 3.0, 1.7, "Sales at exactly $1,999,999: 4 from 2016 to March 2019, and 127 from 2020 to 2025.", 'cap'),
    ('chart', 'condo-coverage.png', 0, 7.0, 1, "The same matching rules link 96% of Brooklyn condo sales to a deed, but 52% in the Bronx.", 'cap'),
    ('clip', None, 228.8, 6.0, 1.0, "In a housing simulation, how you count changes which policy looks best.", 'cap'),
    ('clip', None, 236.2, 5.0, 1.4, "What the city could change: collect the recording tax on every purchase, charge tax rates on slices of the price, and publish the deed number with each sale.", 'cap'),
    ('clip', None, 290.5, 6.0, 1.0, "nychousingdata.com", 'end'),
]


def caption_png(caption, style, tag):
    """Transparent 1280x720 overlay: caption band or title card (Pillow, since this ffmpeg lacks drawtext)."""
    from PIL import ImageDraw, ImageFont
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    if style == 'cap':
        font = ImageFont.truetype(SANS, 33)
        lines = textwrap.wrap(caption, 62)
        lh = 46; band = lh * len(lines) + 44
        d.rectangle([0, H - band, W, H], fill=(15, 30, 42, 200))
        y = H - band + 22
        for ln in lines:
            w = d.textlength(ln, font=font); d.text(((W - w) / 2, y), ln, font=font, fill='white'); y += lh
    else:
        sub = ('Independent research on New York City property records' if style == 'title'
               else 'Papers, data and code · Independent research by Pablo Loschi')
        d.rectangle([0, H / 2 - 110, W, H / 2 + 110], fill=(15, 30, 42, 160))
        ft = ImageFont.truetype(SERIF, 54); fs = ImageFont.truetype(SANS, 27)
        w = d.textlength(caption, font=ft); d.text(((W - w) / 2, H / 2 - 66), caption, font=ft, fill='white')
        w = d.textlength(sub, font=fs); d.text(((W - w) / 2, H / 2 + 26), sub, font=fs, fill=(219, 231, 238))
    p = TMP / f'{tag}_cap.png'; img.save(p); return p


def chart_frame(png, tag):
    """Chart on a white 16:9 canvas, leaving room for the caption band."""
    im = Image.open(SITE / 'assets' / 'stories' / png).convert('RGB')
    cw, ch = 2560, 1440
    canvas = Image.new('RGB', (cw, ch), 'white')
    maxw, maxh = 2300, 1120
    s = min(maxw / im.width, maxh / im.height)
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    canvas.paste(im, ((cw - im.width) // 2, 40))
    p = TMP / f'{tag}.png'; canvas.save(p); return p


parts = []
for i, (kind, png, start, length, slow, caption, style) in enumerate(SEGMENTS, 1):
    tag = f'seg{i:02d}'
    dur = length * slow
    cap = caption_png(caption, style, tag)
    fades = f"fade=t=in:st=0:d={FADE},fade=t=out:st={dur - FADE:.2f}:d={FADE}"
    if kind == 'clip':
        base = f"[0:v]setpts={slow}*PTS,scale={W}:{H},fps={FPS}[b]"
        inputs = ['-ss', str(start), '-t', str(length), '-i', str(SRC)]
    else:
        img = chart_frame(png, tag)
        frames = int(dur * FPS)
        base = (f"[0:v]zoompan=z='1+0.035*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                f"d={frames}:s={W}x{H}:fps={FPS}[b]")
        inputs = ['-loop', '1', '-framerate', str(FPS), '-t', f'{dur:.2f}', '-i', str(img)]
    fc = f"{base};[b][1:v]overlay=0:0,{fades},format=yuv420p[v]"
    out = TMP / f'{tag}.mp4'
    cmd = ['ffmpeg', '-v', 'error', '-y'] + inputs + ['-loop', '1', '-i', str(cap), '-filter_complex', fc,
           '-map', '[v]', '-an', '-t', f'{dur:.2f}', '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', str(out)]
    subprocess.run(cmd, check=True)
    parts.append(out)

lst = TMP / 'list.txt'; lst.write_text(''.join(f"file '{p}'\n" for p in parts))
final = OUT / 'nyc-housing-data-intro.mp4'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(lst), '-c:v', 'libx264', '-preset', 'slow',
                '-crf', '23', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(final)], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '2.5', '-i', str(final), '-frames:v', '1', '-q:v', '3',
                str(OUT / 'nyc-housing-data-intro-poster.jpg')], check=True)
print(final, final.stat().st_size)
