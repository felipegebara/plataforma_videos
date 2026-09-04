import os
import glob
import cv2
from pathlib import Path

p = r"c:\Users\fgeba\Documents\quizz\lendas e historia\output\legoland"
videos = sorted(glob.glob(p + "/*.mp4"))

print("Procurando o vídeo da BANDA DO JACK SPARROW...")

for v_path in videos:
    cap = cv2.VideoCapture(v_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    v_name = os.path.basename(v_path)
    dur = total_frames / float(fps if fps > 0 else 30)

    # Check frame at 3s and 6s
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(3 * fps))
    ret, frame = cap.read()
    if ret:
        # Save sample frames of candidate pirate/band clips
        if dur > 10.0 and dur < 40.0:
            out_scratch = Path(__file__).resolve().parent / "scratch"
            out_scratch.mkdir(exist_ok=True)
            cname = v_name.replace(".mp4", "").replace(" ", "_").replace("(", "").replace(")", "")
            cv2.imwrite(str(out_scratch / f"check_band_{cname}.jpg"), frame)
            print(f" {v_name} | Dur: {dur:.1f}s -> Saved frame")

    cap.release()
