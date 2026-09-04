import os
import glob
import cv2
import numpy as np

p = r"c:\Users\fgeba\Documents\quizz\lendas e historia\output\legoland"
videos = sorted(glob.glob(p + "/*.mp4"))

print("Procurando o vídeo do NINJAGO World...")

for v_path in videos:
    cap = cv2.VideoCapture(v_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    v_name = os.path.basename(v_path)
    dur = total_frames / float(fps if fps > 0 else 30)

    # Sample frame at 3 seconds
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(3 * fps))
    ret, frame = cap.read()
    if ret:
        # Check red/green/yellow dominant colors typical of Ninjago characters or asian temples
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # Red/green Ninja colors
        red_mask = cv2.inRange(hsv, np.array([0, 100, 100]), np.array([10, 255, 255]))
        green_mask = cv2.inRange(hsv, np.array([35, 100, 100]), np.array([85, 255, 255]))

        r_ratio = np.sum(red_mask > 0) / float(frame.shape[0]*frame.shape[1])
        g_ratio = np.sum(green_mask > 0) / float(frame.shape[0]*frame.shape[1])

        print(f" {v_name} | Dur: {dur:.1f}s | Red: {r_ratio*100:.1f}% | Green: {g_ratio*100:.1f}%")

    cap.release()
