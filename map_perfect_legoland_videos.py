import os
import glob
import cv2
from pathlib import Path

p = r"c:\Users\fgeba\Documents\quizz\lendas e historia\output\legoland"
videos = sorted(glob.glob(p + "/*.mp4"))

insp_dir = Path(__file__).resolve().parent / "scratch" / "vids_inspect"
insp_dir.mkdir(parents=True, exist_ok=True)

print(f"Extraindo amostras visuais de {len(videos)} vídeos...")

for v_path in videos:
    v_name = os.path.basename(v_path)
    cap = cv2.VideoCapture(v_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    dur = total_frames / float(fps)

    clean_name = v_name.replace(".mp4", "").replace(" ", "_").replace("(", "").replace(")", "")

    # Save frame at 4s if video is longer than 4s, else mid frame
    sample_sec = 4.0 if dur > 4.0 else dur / 2.0
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(sample_sec * fps))
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(str(insp_dir / f"{clean_name}.jpg"), frame)

    cap.release()

print("Amostras visuais salvas em:", insp_dir)
