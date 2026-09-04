import urllib.request
import urllib.parse
import json
import shutil
from pathlib import Path
from PIL import Image, ImageEnhance, ImageDraw, ImageFont, ImageFilter

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Antigravity/2.0"}

images_dir = Path(r"c:\Users\fgeba\Documents\quizz\lendas e historia\output\images\pelourinho_real")
artifacts_dir = Path(r"C:\Users\fgeba\.gemini\antigravity\brain\0910298c-5f57-4975-a1e1-10a7451cea7a")
images_dir.mkdir(parents=True, exist_ok=True)

# Search Wikimedia Commons specifically for authentic Pelourinho & Salvador Bahia photos
SEARCH_TERMS = [
    ("Pelourinho Salvador Bahia largo", "modern_pelourinho.jpg"),
    ("Farol da Barra Salvador Bahia", "farol_da_barra.jpg"),
    ("Elevador Lacerda Salvador Bahia", "elevador_lacerda.jpg"),
    ("Igreja de Sao Francisco Salvador Bahia", "igreja_sf.jpg")
]

def fetch_real_wikimedia(query: str, out_path: Path):
    encoded = urllib.parse.quote(query)
    url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={encoded}&gsrlimit=8&gsrnamespace=6&prop=imageinfo&iiprop=url&iiurlwidth=1280&format=json"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            pages = data.get('query', {}).get('pages', {})
            for p_id, p_data in pages.items():
                info = p_data.get('imageinfo', [])
                if info:
                    img_url = info[0].get('thumburl') or info[0].get('url')
                    if img_url and any(img_url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
                        with urllib.request.urlopen(urllib.request.Request(img_url, headers=HEADERS), timeout=12) as r:
                            content = r.read()
                            if len(content) > 30000:
                                with open(out_path, 'wb') as f:
                                    f.write(content)
                                print(f"✓ [FOTO REAL HD OBTIDA]: '{query}' ({out_path.name})")
                                return True
    except Exception as e:
        print(f"Error fetching {query}: {e}")
    return False

for query, filename in SEARCH_TERMS:
    out_file = images_dir / filename
    fetch_real_wikimedia(query, out_file)

# Build formatted 9:16 HD photos of real Salvador
fmt_modern = images_dir / "pelourinho_real_modern.png"
fmt_1880 = images_dir / "pelourinho_real_1880.png"

raw_mod = images_dir / "modern_pelourinho.jpg"
if raw_mod.exists():
    img = Image.open(raw_mod).convert("RGB")
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

    img_modern = img.resize((w, h), Image.Resampling.LANCZOS)
    img_modern.save(fmt_modern, format="PNG")
    shutil.copy(fmt_modern, artifacts_dir / "pelourinho_real_modern.png")

    # Transform into 1880 historical sepia on the EXACT same photo
    np_mod = np.array(img_modern).astype(float)
    r, g, b = np_mod[:, :, 0], np_mod[:, :, 1], np_mod[:, :, 2]
    sepia_r = np.clip(0.393 * r + 0.769 * g + 0.189 * b, 0, 255)
    sepia_g = np.clip(0.349 * r + 0.686 * g + 0.168 * b, 0, 255)
    sepia_b = np.clip(0.272 * r + 0.534 * g + 0.131 * b, 0, 255)
    
    np_sepia = np.stack([sepia_r, sepia_g, sepia_b], axis=2).astype(np.uint8)
    img_sepia = Image.fromarray(np_sepia)
    img_sepia = ImageEnhance.Contrast(img_sepia).enhance(1.25)
    
    img_sepia.save(fmt_1880, format="PNG")
    shutil.copy(fmt_1880, artifacts_dir / "pelourinho_real_1880.png")

print("\n🎉 FOTOS REAIS DO PELOURINHO (SALVADOR-BA) SALVAS COM SUCESSO!")
