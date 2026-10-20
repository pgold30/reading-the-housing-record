"""Build the studio-quality 'How the Studies Connect' video for nychousingdata.com.

Uses the real studio human narration and clean visuals from
'The Anatomy of a Public Record' (The_Anatomy_of_a_Public_Record.mp4), replacing
inaccurate slides with authentic figures from the papers:
  1. 0.00 -> 35.93: Queens condo intro, tax gap, DOF vs ACRIS join
  2. 60.04 -> 97.28: Foreclosure deeds to lenders & 74% vs 6% non-zero cents chart
  3. 97.86 -> 108.49: Real deed index paths chart (stories/deed-index-paths.png)
  4. 117.72 -> 139.30: Cash discount & surname screen (cash gap 1.53 log pts)
  5. 149.76 -> 168.46: 2019 whole-price tax notches ($2M, $3M, $5M cliffs)
  6. 168.46 -> 177.48: Real tax round prices chart (stories/tax-round-prices.png)
  7. 188.50 -> 216.77: Condo linkage (96.1% Brooklyn vs 51.7% Bronx) & simulation intro
  8. 216.77 -> 224.06: Real simulation benchmark figure (fig/wedge-benchmark-v6-4.png)
  9. 224.06 -> 305.36: Fixed cohort, 3 policy fixes & close on nychousingdata.com

Usage: python3 build_studies_connect_video.py [SOURCE_VIDEO] [SITE_DIR] [OUT_DIR]
"""
import subprocess, sys, shutil
from pathlib import Path
from PIL import Image

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/Users/pablo/Downloads/The_Anatomy_of_a_Public_Record.mp4')
SITE = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('/Users/pablo/Documents/ChatGPT/papers/research-site-stories')
OUT = Path(sys.argv[3]) if len(sys.argv) > 3 else SITE / 'assets' / 'media'

TMP = Path('/tmp/studies_connect_build')
if TMP.exists():
    shutil.rmtree(TMP)
TMP.mkdir(parents=True, exist_ok=True)

W, H, FPS = 1280, 720, 25

# Verified segments from The_Anatomy_of_a_Public_Record.mp4:
# (kind, chart_rel_path, start_sec, end_sec, description)
SEGMENTS = [
    (
        'clip', None, 0.00, 35.93,
        "Two buyers of $900k Queens condo, $13,860 vs $0, DOF vs ACRIS join"
    ),
    (
        'clip', None, 60.04, 97.28,
        "Foreclosure deeds to lenders, 74% vs 6% non-zero cents chart"
    ),
    (
        'chart', 'stories/deed-index-paths.png', 97.86, 108.49,
        "Real deed index paths paper figure replacing fake crash chart"
    ),
    (
        'clip', None, 117.72, 139.30,
        "9% cash discount, surname screen, corporate cash gap 1.53 log pts"
    ),
    (
        'clip', None, 149.76, 168.46,
        "2019 state transfer tax whole-price cliffs at $2M, $3M, $5M"
    ),
    (
        'chart', 'stories/tax-round-prices.png', 168.46, 177.48,
        "Real tax round prices paper figure ($1,999,999 surged from 4 to 127)"
    ),
    (
        'clip', None, 188.50, 216.77,
        "Condo linkage 96.1% Brooklyn vs 51.7% Bronx, intro to simulation"
    ),
    (
        'chart', 'fig/wedge-benchmark-v6-4.png', 216.77, 224.06,
        "Real simulation benchmark figure replacing +82% bar"
    ),
    (
        'clip', None, 224.06, 305.36,
        "Fixed entry cohort, 3 policy fixes, ending on nychousingdata.com"
    ),
]


def make_chart_canvas(rel_path, tag, max_w=1240, max_h=680):
    """Render a paper chart centered on a clean 1280x720 white canvas."""
    chart_path = SITE / 'assets' / rel_path
    im = Image.open(chart_path).convert('RGBA')
    canvas = Image.new('RGBA', (W, H), (255, 255, 255, 255))
    scale = min(max_w / im.width, max_h / im.height)
    new_w = int(round(im.width * scale))
    new_h = int(round(im.height * scale))
    resized = im.resize((new_w, new_h), Image.Resampling.LANCZOS)
    x = (W - new_w) // 2
    y = (H - new_h) // 2
    canvas.paste(resized, (x, y), resized)
    out_png = TMP / f'{tag}_canvas.png'
    canvas.convert('RGB').save(out_png)
    return out_png


def build_video():
    print(f"Source video: {SRC}")
    print(f"Building studio-quality 'How the Studies Connect' video ({len(SEGMENTS)} segments)...")
    
    parts = []
    for i, (kind, rel_path, start, end, desc) in enumerate(SEGMENTS, 1):
        tag = f'seg{i:02d}'
        dur = end - start
        out_seg = TMP / f'{tag}.mp4'
        print(f"[{i:02d}/{len(SEGMENTS):02d}] {kind:5s} {start:6.2f} -> {end:6.2f} ({dur:5.2f}s): {desc}...")
        
        if kind == 'clip':
            cmd = [
                'ffmpeg', '-v', 'error', '-y',
                '-ss', f'{start:.2f}', '-t', f'{dur:.2f}', '-i', str(SRC),
                '-vf', f'scale={W}:{H},fps={FPS},format=yuv420p',
                '-map', '0:v', '-map', '0:a',
                '-c:v', 'libx264', '-preset', 'fast', '-crf', '19',
                '-pix_fmt', 'yuv420p', '-r', str(FPS),
                '-c:a', 'aac', '-b:a', '128k', '-ar', '44100', '-ac', '2',
                '-t', f'{dur:.2f}',
                str(out_seg)
            ]
        else:
            chart_png = make_chart_canvas(rel_path, tag)
            cmd = [
                'ffmpeg', '-v', 'error', '-y',
                '-ss', f'{start:.2f}', '-t', f'{dur:.2f}', '-i', str(SRC),
                '-loop', '1', '-framerate', str(FPS), '-t', f'{dur:.2f}', '-i', str(chart_png),
                '-map', '1:v', '-map', '0:a',
                '-c:v', 'libx264', '-preset', 'fast', '-crf', '19',
                '-pix_fmt', 'yuv420p', '-r', str(FPS),
                '-c:a', 'aac', '-b:a', '128k', '-ar', '44100', '-ac', '2',
                '-t', f'{dur:.2f}',
                str(out_seg)
            ]
        subprocess.run(cmd, check=True)
        parts.append(out_seg)
    
    # Concat all segments smoothly
    lst = TMP / 'list.txt'
    lst.write_text(''.join(f"file '{p}'\n" for p in parts))
    
    OUT.mkdir(parents=True, exist_ok=True)
    final_video = OUT / 'how-the-studies-connect.mp4'
    poster_img = OUT / 'how-the-studies-connect-poster.jpg'
    
    print(f"\nConcatenating {len(parts)} segments into {final_video}...")
    subprocess.run([
        'ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(lst),
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '20',
        '-c:a', 'aac', '-b:a', '128k', '-ar', '44100', '-ac', '2',
        '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(final_video)
    ], check=True)
    
    # Extract clean poster image at 1.5s
    print(f"Extracting poster image at 1.5s to {poster_img}...")
    subprocess.run([
        'ffmpeg', '-v', 'error', '-y', '-ss', '1.5', '-i', str(final_video),
        '-frames:v', '1', '-q:v', '2', str(poster_img)
    ], check=True)
    
    # Sync with dist
    dist_media = SITE / 'dist' / 'assets' / 'media'
    dist_media.mkdir(parents=True, exist_ok=True)
    shutil.copy2(final_video, dist_media / final_video.name)
    shutil.copy2(poster_img, dist_media / poster_img.name)
    
    # Copy to Downloads
    downloads_dest = Path('/Users/pablo/Downloads/how-the-studies-connect.mp4')
    shutil.copy2(final_video, downloads_dest)
    
    total_mb = final_video.stat().st_size / (1024 * 1024)
    print("\nSUCCESS!")
    print(f"Final video: {final_video} ({total_mb:.1f} MB)")
    print(f"Poster:      {poster_img}")
    print(f"Dist copy:   {dist_media / final_video.name}")
    print(f"Downloads:   {downloads_dest}")


if __name__ == '__main__':
    build_video()
