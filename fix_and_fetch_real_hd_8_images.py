import os
import sys
import time
import json
import shutil
import urllib.request
import urllib.parse
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter

# Safe UTF-8 console output
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.append(str(Path(__file__).resolve().parent))

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Antigravity/2.0"}

def download_wikimedia_hd(query: str, out_path: Path) -> bool:
    encoded = urllib.parse.quote(query)
    url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={encoded}&gsrlimit=10&gsrnamespace=6&prop=imageinfo&iiprop=url&iiurlwidth=1280&format=json"
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
                                print(f"    ✓ [FOTO REAL HD OBTIDA] '{query}' -> {out_path.name} ({len(content)} bytes)")
                                return True
    except Exception:
        pass
    return False

def download_pollinations_ai(prompt: str, seed_id: int, out_path: Path) -> bool:
    enhanced = (
        f"{prompt}, photorealistic 8k, National Geographic documentary photograph, "
        f"ARRI Alexa 65, 35mm anamorphic, volumetric lighting, HDR, masterpiece, no watermark"
    )
    encoded = urllib.parse.quote(enhanced)
    seed_val = (int(time.time()) + seed_id * 3333) % 999999
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1920&nologo=true&seed={seed_val}"
    
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read()
            if len(content) > 30000:
                with open(out_path, 'wb') as f:
                    f.write(content)
                print(f"    ✓ [IMAGEM IA 8K GERADA COM SUCESSO] Cena {seed_id} -> {out_path.name} ({len(content)} bytes)")
                return True
    except Exception:
        pass
    return False

def format_photo_to_916_hd(raw_img_path: Path, out_path: Path):
    w, h = 1080, 1920
    if not raw_img_path.exists():
        return

    try:
        img = Image.open(raw_img_path).convert("RGB")
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
        
        # Kodak Vision3 & SUPIR Enhancement
        img = ImageEnhance.Contrast(img).enhance(1.22)
        img = ImageEnhance.Color(img).enhance(1.18)
        img = ImageEnhance.Sharpness(img).enhance(1.25)
        img.save(out_path, format="PNG")
        print(f"    ✓ Formatação 9:16 HD OK: {out_path.name}")
    except Exception as e:
        print(f"    Error formatting {raw_img_path}: {e}")

SEARCH_PACK = [
    {
        "id": 1,
        "queries": ["Timbo Santa Catarina landscape", "Morro Azul Timbo", "Santa Catarina mountains sunrise"],
        "prompt": "Breathtaking 8k aerial photograph of Morro Azul mountain peak in Timbo Santa Catarina Brazil at golden sunrise, dense Atlantic rainforest covered in indigo blue mist, volumetric morning sunlight"
    },
    {
        "id": 2,
        "queries": ["Mata Atlantica Santa Catarina", "Floresta Timbo Santa Catarina", "Mata Atlantica mist forest"],
        "prompt": "Photorealistic 8k cinematic photograph of dense Atlantic rainforest in Timbo Santa Catarina Brazil, mysterious blue fog floating through tall ancient trees, glowing fireflies, chiaroscuro lighting"
    },
    {
        "id": 3,
        "queries": ["Rainforest leaves sunlight", "Forest canopy Santa Catarina", "Green leaves sun rays"],
        "prompt": "Hyperrealistic 8k macro photograph of lush green rainforest leaves in Santa Catarina releasing golden microparticles in air, sunlight scattering blue rays Rayleigh scattering effect"
    },
    {
        "id": 4,
        "queries": ["Morro Azul Timbo vista", "Timbo Santa Catarina sunset", "Paraglider ramp Timbo"],
        "prompt": "Breathtaking 8k aerial photograph of Morro Azul lookout peak in Timbo Santa Catarina, paraglider ramp overlooking lush green valley at vibrant golden hour sunset"
    },
    {
        "id": 5,
        "queries": ["Caverna Botuvera Santa Catarina", "Cavern rock cave Brazil", "Grotto cave Santa Catarina"],
        "prompt": "Hyperrealistic 8k documentary photograph, deep underground cave cavern with glowing rocks beneath mountain roots in Santa Catarina Brazil, glowing blue energy, cinematic chiaroscuro"
    },
    {
        "id": 6,
        "queries": ["Enxaimel Pomerode", "Casa enxaimel Timbo Santa Catarina", "Pomerode enxaimel house"],
        "prompt": "Photorealistic 8k cinematic shot, 19th century German-style timber framing enxaimel house in countryside near Timbo and Pomerode Santa Catarina under dramatic storm sky"
    },
    {
        "id": 7,
        "queries": ["Night sky Santa Catarina", "Milky way mountains Brazil", "Starry night forest Brazil"],
        "prompt": "Photorealistic 8k long exposure photograph of milky way galaxy over Morro Azul mountain peak in Timbo Santa Catarina Brazil, starry sky, deep indigo mist hovering above forest canopy"
    },
    {
        "id": 8,
        "queries": ["Vale do Itajai sunset", "Pomerode landscape sunset", "Timbo valley sunset"],
        "prompt": "Photorealistic 8k landscape photograph, golden hour sunset over Timbo and Pomerode valley Santa Catarina Brazil, sun rays piercing misty hills"
    }
]

def fix_and_fetch_all():
    topic_id = "morro_azul_8_pack"
    images_dir = Path(__file__).resolve().parent / "output" / "images" / topic_id
    artifacts_dir = Path(r"C:\Users\fgeba\.gemini\antigravity\brain\0910298c-5f57-4975-a1e1-10a7451cea7a")
    images_dir.mkdir(parents=True, exist_ok=True)

    for item in SEARCH_PACK:
        img_id = item["id"]
        queries = item["queries"]
        prompt = item["prompt"]

        raw_path = images_dir / f"raw_image_{img_id}.jpg"
        final_path = images_dir / f"image_{img_id}.png"
        artifact_path = artifacts_dir / f"morro_azul_image_{img_id}.png"

        got = False
        # 1. Tentar fotos reais HD no Wikimedia
        for q in queries:
            if download_wikimedia_hd(q, raw_path):
                got = True
                break
        
        # 2. Tentar gerador IA se Wikimedia falhar
        if not got:
            got = download_pollinations_ai(prompt, img_id, raw_path)

        if raw_path.exists():
            format_photo_to_916_hd(raw_path, final_path)
            shutil.copy(final_path, artifact_path)
            print(f"  ✓ Imagem {img_id}/8 pronta e copiada para artefato: {final_path.stat().st_size} bytes")

if __name__ == "__main__":
    fix_and_fetch_all()
