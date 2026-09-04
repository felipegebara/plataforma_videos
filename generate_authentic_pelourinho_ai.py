import os
import sys
import time
import json
import shutil
import urllib.request
import urllib.parse
from pathlib import Path
from PIL import Image, ImageEnhance
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Antigravity/2.0"}

images_dir = Path(r"c:\Users\fgeba\Documents\quizz\lendas e historia\output\images\pelourinho_real")
artifacts_dir = Path(r"C:\Users\fgeba\.gemini\antigravity\brain\0910298c-5f57-4975-a1e1-10a7451cea7a")
images_dir.mkdir(parents=True, exist_ok=True)

raw_file = images_dir / "raw_pelourinho.jpg"
fmt_mod = images_dir / "pelourinho_real_modern.png"
fmt_1880 = images_dir / "pelourinho_real_1880.png"

# Prompt explicitly avoiding human faces: architectural focus only
prompt = (
    "Breathtaking photorealistic 8k architectural photograph of Pelourinho square in Salvador Bahia Brazil, "
    "empty cobblestone street, colorful Portuguese colonial house facades, sunny day, "
    "no human faces, wide angle architectural view, National Geographic documentary quality, masterpiece, no watermark"
)

encoded = urllib.parse.quote(prompt)
seed_val = (int(time.time()) + 999) % 999999
ai_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1920&nologo=true&seed={seed_val}"

print("Generating 8K AI Architectural Photograph of Pelourinho (No Faces)...")
req = urllib.request.Request(ai_url, headers=HEADERS)
with urllib.request.urlopen(req, timeout=20) as resp:
    content = resp.read()
    with open(raw_file, "wb") as f:
        f.write(content)

# Format 9:16 HD Modern
img = Image.open(raw_file).convert("RGB")
w, h = 1080, 1920
aspect_target = 9 / 16.0
aspect_img = img.width / float(img.height)

if aspect_img > aspect_target:
    new_w = int(img.height * aspect_target)
    left = (img.width - new_w) // 2
    img = img.crop((left, 0, left + new_w, img.height))
else:
    new_h = int(img.width / aspect_target)
    top = (img.height - new_h) // 2
    img = img.crop((0, top, img.width, top + new_h))

img_mod = img.resize((w, h), Image.Resampling.LANCZOS)
img_mod.save(fmt_mod, format="PNG")
shutil.copy(fmt_mod, artifacts_dir / "salvador_pelourinho_real_modern.png")

# Historical 1880 Transformation on the EXACT SAME PHOTO
np_mod = np.array(img_mod).astype(float)
r, g, b = np_mod[:, :, 0], np_mod[:, :, 1], np_mod[:, :, 2]
sepia_r = np.clip(0.393 * r + 0.769 * g + 0.189 * b, 0, 255)
sepia_g = np.clip(0.349 * r + 0.686 * g + 0.168 * b, 0, 255)
sepia_b = np.clip(0.272 * r + 0.534 * g + 0.131 * b, 0, 255)

np_sepia = np.stack([sepia_r, sepia_g, sepia_b], axis=2).astype(np.uint8)
img_sepia = Image.fromarray(np_sepia)
img_sepia = ImageEnhance.Contrast(img_sepia).enhance(1.25)
img_sepia.save(fmt_1880, format="PNG")
shutil.copy(fmt_1880, artifacts_dir / "salvador_pelourinho_real_1880.png")

print("OK: Pelourinho architectural photos (no faces) saved successfully!")
