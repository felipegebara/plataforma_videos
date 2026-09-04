import os
import sys
import glob
import cv2
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

p = r"c:\Users\fgeba\Documents\quizz\lendas e historia\output\legoland"
videos = sorted(glob.glob(p + "/*.mp4"))

print(f"Buscando a cena exata da mão cobrindo a câmera em {len(videos)} vídeos...")

bad_videos = []

for v_path in videos:
    cap = cv2.VideoCapture(v_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    v_name = os.path.basename(v_path)

    has_hand = False
    for f_idx in range(0, frame_count, 5):
        cap.set(cv2.CAP_PROP_POS_FRAMES, f_idx)
        ret, frame = cap.read()
        if not ret:
            break

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_skin = np.array([0, 30, 60], dtype=np.uint8)
        upper_skin = np.array([25, 255, 255], dtype=np.uint8)
        mask = cv2.inRange(hsv, lower_skin, upper_skin)

        skin_ratio = float(np.sum(mask > 0)) / (frame.shape[0] * frame.shape[1])
        if skin_ratio > 0.25:
            has_hand = True
            time_sec = f_idx / float(fps if fps > 0 else 30)
            print(f"  [ALERTA MÃO DETECTADA]: {v_name} | Tempo: {time_sec:.2f}s | Proporção: {skin_ratio*100:.1f}%")
            break

    if has_hand:
        bad_videos.append(v_name)

    cap.release()

print("\n--- VÍDEOS COM MÃO / DEDOS IDENTIFICADOS ---")
for bv in bad_videos:
    print(f" - {bv}")
