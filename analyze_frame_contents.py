import cv2
import numpy as np
from pathlib import Path

tamar_dir = Path(r"c:\Users\fgeba\Documents\quizz\lendas e historia\output\tamar floripa")
raw_vids = sorted([f for f in tamar_dir.glob("*.mp4") if not f.name.startswith("._")])

def inspect_video_details(v_path: Path):
    cap = cv2.VideoCapture(str(v_path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_f = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    dur = total_f / fps if fps > 0 else 0

    blue_green_ratios = []
    brightness_levels = []

    f_idx = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        if f_idx % 15 == 0: # Sample every half second
            b, g, r = cv2.split(frame)
            bg_ratio = (np.mean(b) + np.mean(g)) / (np.mean(r) + 1.0)
            bright = np.mean(frame)
            blue_green_ratios.append(bg_ratio)
            brightness_levels.append(bright)
        
        f_idx += 1

    cap.release()
    avg_bg = np.mean(blue_green_ratios) if blue_green_ratios else 0
    avg_br = np.mean(brightness_levels) if brightness_levels else 0

    return dur, avg_bg, avg_br

print("=== Mapeamento Técnico de Conteúdo ===")
for idx, vp in enumerate(raw_vids, 1):
    dur, bg, br = inspect_video_details(vp)
    print(f"Vídeo {idx:02d}: {vp.name} | Duração: {dur:.1f}s | Water/Pool Blue Ratio: {bg:.2f} | Brightness: {br:.1f}")
