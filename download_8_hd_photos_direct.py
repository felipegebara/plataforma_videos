import sys
import urllib.request
import shutil
from pathlib import Path
from PIL import Image, ImageEnhance

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Antigravity/2.0"}

images_dir = Path(r"c:\Users\fgeba\Documents\quizz\lendas e historia\output\images\morro_azul_8_pack")
artifacts_dir = Path(r"C:\Users\fgeba\.gemini\antigravity\brain\0910298c-5f57-4975-a1e1-10a7451cea7a")
images_dir.mkdir(parents=True, exist_ok=True)

PHOTO_URLS = [
    # 1. Sunrise over misty mountains & forest
    "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=1080&h=1920&fit=crop&q=85",
    # 2. Dense rainforest mist & dark forest
    "https://images.unsplash.com/photo-1448375240586-882707db888b?w=1080&h=1920&fit=crop&q=85",
    # 3. Macro green leaves with sun rays
    "https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?w=1080&h=1920&fit=crop&q=85",
    # 4. Paraglider lookout mountain valley sunset
    "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=1080&h=1920&fit=crop&q=85",
    # 5. Underground cavern cave with glowing lights
    "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=1080&h=1920&fit=crop&q=85",
    # 6. Historic timber framing house in countryside
    "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=1080&h=1920&fit=crop&q=85",
    # 7. Milky way starry night sky over mountains
    "https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?w=1080&h=1920&fit=crop&q=85",
    # 8. Golden hour sunset over mountain valley
    "https://images.unsplash.com/photo-1472214103451-9374bd1c798e?w=1080&h=1920&fit=crop&q=85"
]

for idx, url in enumerate(PHOTO_URLS, 1):
    raw_path = images_dir / f"raw_image_{idx}.jpg"
    final_path = images_dir / f"image_{idx}.png"
    artifact_path = artifacts_dir / f"morro_azul_image_{idx}.png"

    print(f"Downloading Photo {idx}/8 from Unsplash HD...")
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        content = resp.read()
        with open(raw_path, "wb") as f:
            f.write(content)

    img = Image.open(raw_path).convert("RGB")
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

    img = img.resize((w, h), Image.Resampling.LANCZOS)
    img = ImageEnhance.Contrast(img).enhance(1.20)
    img = ImageEnhance.Color(img).enhance(1.15)
    img = ImageEnhance.Sharpness(img).enhance(1.25)

    img.save(final_path, format="PNG")
    shutil.copy(final_path, artifact_path)
    print(f"OK Photo {idx}/8 Saved: {final_path.stat().st_size} bytes")

print("ALL 8 HD REAL PHOTOS DOWNLOADED AND SAVED PERFECTLY!")
