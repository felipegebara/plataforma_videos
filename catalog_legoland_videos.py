import os
import sys
import glob
import cv2
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

p = r"c:\Users\fgeba\Documents\quizz\lendas e historia\output\legoland"
videos = sorted(glob.glob(p + "/*.mp4"))

cat_dir = Path(__file__).resolve().parent / "scratch" / "legoland_catalog"
cat_dir.mkdir(parents=True, exist_ok=True)

print(f"Catalogando {len(videos)} vídeos da Legoland...")

for v_path in videos:
    v_name = os.path.basename(v_path)
    cap = cv2.VideoCapture(v_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    dur = total_frames / float(fps)

    clean_name = v_name.replace(".mp4", "").replace(" ", "_").replace("(", "").replace(")", "")

    saved_frames = []
    for sec in [3, 6, 10, 15]:
        if sec < dur:
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(sec * fps))
            ret, frame = cap.read()
            if ret:
                f_path = cat_dir / f"{clean_name}_sec{sec}.jpg"
                cv2.imwrite(str(f_path), frame)
                saved_frames.append(str(f_path))

    cap.release()
    print(f"  - {v_name} | Duração: {dur:.1f}s | Frames salvos: {len(saved_frames)}")

print("\nCatalogação completa salva em:", cat_dir)
