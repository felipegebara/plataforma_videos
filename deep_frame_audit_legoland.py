import os
import glob
import cv2
import numpy as np
from pathlib import Path

p = r"c:\Users\fgeba\Documents\quizz\lendas e historia\output\legoland"
videos = sorted(glob.glob(p + "/*.mp4"))

deep_dir = Path(__file__).resolve().parent / "scratch" / "deep_audit"
deep_dir.mkdir(parents=True, exist_ok=True)

print(f"==========================================")
print(f"[AUDITORIA VISUAL DE ALTA PRECISÃO: {len(videos)} VÍDEOS]")
print(f"==========================================")

catalog = []

for idx, v_path in enumerate(videos, 1):
    v_name = os.path.basename(v_path)
    cap = cv2.VideoCapture(v_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    dur = total_frames / float(fps)

    clean_name = v_name.replace(".mp4", "").replace(" ", "_").replace("(", "").replace(")", "").replace("@", "")

    saved_shots = []
    # Sample at 4 points across the video
    for pct in [0.2, 0.4, 0.6, 0.8]:
        sec = dur * pct
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(sec * fps))
        ret, frame = cap.read()
        if ret:
            img_fname = f"v{idx:02d}_{clean_name}_sec{sec:.1f}.jpg"
            img_fpath = deep_dir / img_fname
            cv2.imwrite(str(img_fpath), frame)
            saved_shots.append(str(img_fpath))

    cap.release()

    print(f"  [{idx:02d}/34] {v_name:<45} | Duração: {dur:5.1f}s | {len(saved_shots)} quadros gerados")
    catalog.append({
        "id": idx,
        "filename": v_name,
        "duration": dur,
        "shots": saved_shots
    })

print(f"\nQuadros salvos em: {deep_dir}")
