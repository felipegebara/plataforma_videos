import os
import glob
import cv2
from pathlib import Path

p = r"c:\Users\fgeba\Documents\quizz\lendas e historia\output\legoland"
out_scratch = Path(__file__).resolve().parent / "scratch"
out_scratch.mkdir(exist_ok=True)

candidate_vids = [
    "WhatsApp Video 2026-08-12 at 18.49.44 (5).mp4",
    "WhatsApp Video 2026-08-12 at 18.49.44 (6).mp4",
    "WhatsApp Video 2026-08-12 at 18.49.45 (10).mp4",
    "WhatsApp Video 2026-08-12 at 18.49.44.mp4",
    "WhatsApp Video 2026-08-12 at 18.49.45 (2).mp4",
    "WhatsApp Video 2026-08-12 at 18.49.45 (8).mp4"
]

for vname in candidate_vids:
    vpath = os.path.join(p, vname)
    if os.path.exists(vpath):
        cap = cv2.VideoCapture(vpath)
        cap.set(cv2.CAP_PROP_POS_FRAMES, 90)
        ret, frame = cap.read()
        if ret:
            clean_name = vname.replace(".mp4", "").replace(" ", "_").replace("(", "").replace(")", "")
            save_p = out_scratch / f"{clean_name}.jpg"
            cv2.imwrite(str(save_p), frame)
            print(f"Saved: {save_p}")
        cap.release()
