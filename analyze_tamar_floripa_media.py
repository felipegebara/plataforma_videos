import os
import sys
import zipfile
from pathlib import Path
import cv2

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

tamar_dir = Path(r"c:\Users\fgeba\Documents\quizz\lendas e historia\output\tamar floripa")
zip_file = tamar_dir / "WhatsApp Unknown 2026-08-08 at 17.38.58.zip"
extract_dir = tamar_dir / "extracted_zip"

# Unzip zip file if it exists and extract_dir doesn't exist
if zip_file.exists() and not extract_dir.exists():
    extract_dir.mkdir(parents=True, exist_ok=True)
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        print(f"✓ Zip extraído em: {extract_dir}")
    except Exception as e:
        print(f"Error unzipping: {e}")

# Scan all media files
all_videos = list(tamar_dir.glob("*.mp4")) + list(extract_dir.rglob("*.mp4")) + list(tamar_dir.glob("*.mov")) + list(extract_dir.rglob("*.mov"))
all_images = list(tamar_dir.glob("*.jpg")) + list(tamar_dir.glob("*.jpeg")) + list(tamar_dir.glob("*.png")) + list(extract_dir.rglob("*.jpg")) + list(extract_dir.rglob("*.jpeg")) + list(extract_dir.rglob("*.png"))

video_info = []
total_vid_dur = 0.0

for vp in set(all_videos):
    try:
        cap = cv2.VideoCapture(str(vp))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        dur = frames / fps if fps > 0 else 0
        cap.release()

        total_vid_dur += dur
        is_vertical = h > w
        video_info.append({
            "path": vp,
            "name": vp.name,
            "duration": dur,
            "width": w,
            "height": h,
            "orientation": "9:16 Vertical" if is_vertical else "16:9 Horizontal"
        })
    except Exception:
        pass

print("\n==========================================")
print(f"📊 RELATÓRIO DE MÍDIAS DO PROJETO TAMAR FLORIPA")
print("==========================================")
print(f"📷 Total de Fotos: {len(set(all_images))}")
print(f"🎥 Total de Vídeos: {len(video_info)}")
print(f"⏱️ Duração Total Somada dos Vídeos: {total_vid_dur:.1f} segundos ({total_vid_dur/60.0:.2f} minutos)")
print("\n--- DETALHAMENTO DOS VÍDEOS ---")
for idx, v in enumerate(sorted(video_info, key=lambda x: x["duration"], reverse=True), 1):
    print(f"{idx:02d}. {v['name']} | Duração: {v['duration']:.1f}s | Resolução: {v['width']}x{v['height']} ({v['orientation']})")

print("\n--- ANÁLISE DE PROPOSIÇÃO DE CONTEÚDO ---")
vert_vids = [v for v in video_info if v["orientation"] == "9:16 Vertical"]
horiz_vids = [v for v in video_info if v["orientation"] == "16:9 Horizontal"]
print(f"• Vídeos Verticais (Shorts): {len(vert_vids)}")
print(f"• Vídeos Horizontais (Vídeo Longo): {len(horiz_vids)}")
