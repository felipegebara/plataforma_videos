import urllib.request
import shutil
from pathlib import Path
from PIL import Image, ImageEnhance

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Antigravity/2.0"}

images_dir = Path(r"c:\Users\fgeba\Documents\quizz\lendas e historia\output\images\pelourinho_real")
artifacts_dir = Path(r"C:\Users\fgeba\.gemini\antigravity\brain\0910298c-5f57-4975-a1e1-10a7451cea7a")
images_dir.mkdir(parents=True, exist_ok=True)

# Direct HD photograph of Salvador Pelourinho (colorful colonial facades & cobblestone street)
PELOURINHO_URL = "https://images.unsplash.com/photo-1548625361-188b753065b7?w=1080&h=1920&fit=crop&q=85"

raw_file = images_dir / "raw_pelourinho.jpg"
fmt_mod = images_dir / "pelourinho_real_modern.png"
fmt_1880 = images_dir / "pelourinho_real_1880.png"

print("Downloading authentic Pelourinho Salvador photo...")
req = urllib.request.Request(PELOURINHO_URL, headers=HEADERS)
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        content = resp.read()
        with open(raw_file, "wb") as f:
            f.write(content)
        print("✓ Photo downloaded!")
except Exception as e:
    print("Fallback download...")
    # Wikimedia backup URL
    backup_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/Largo_do_Pelourinho_-_Salvador.jpg/800px-Largo_do_Pelourinho_-_Salvador.jpg"
    req = urllib.request.Request(backup_url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        content = resp.read()
        with open(raw_file, "wb") as f:
            f.write(content)

# Format to 9:16 HD
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
import numpy as np
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

print("✓ Photos formatted and saved successfully!")
