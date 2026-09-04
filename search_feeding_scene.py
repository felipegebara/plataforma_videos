import cv2
import numpy as np
from pathlib import Path

tamar_dir = Path(r"c:\Users\fgeba\Documents\quizz\lendas e historia\output\tamar floripa")
raw_vids = sorted([f for f in tamar_dir.glob("*.mp4") if not f.name.startswith("._")])

for v_idx, vp in enumerate(raw_vids, 1):
    cap = cv2.VideoCapture(str(vp))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_f = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    dur = total_f / fps if fps > 0 else 0

    print(f"\n--- Analisando Vídeo {v_idx:02d}: {vp.name} ({dur:.1f}s) ---")
    
    # Check every 2 seconds
    for sec in range(0, int(dur), 2):
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(sec * fps))
        ret, frame = cap.read()
        if ret:
            # Detect upper region brightness / water surface / motion
            h, w, _ = frame.shape
            top_half = frame[0:int(h*0.4), :]
            bottom_half = frame[int(h*0.4):, :]

            top_bright = np.mean(top_half)
            bot_bright = np.mean(bottom_half)
            
            # Simple color check for green leaves / food / biologist clothing
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            green_mask = cv2.inRange(hsv, (35, 40, 40), (85, 255, 255))
            green_pct = (np.count_nonzero(green_mask) / (h * w)) * 100.0

            if green_pct > 2.0 or top_bright > 140:
                print(f"  [Seg {sec:02d}s] Brightness Top: {top_bright:.1f} | Green/Food Pct: {green_pct:.2f}%")

    cap.release()
