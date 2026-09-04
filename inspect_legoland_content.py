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

print("=== IDENTIFICAÇÃO VISUAL DE CADA VÍDEO DA LEGOLAND ===")

for v_path in videos:
    v_name = os.path.basename(v_path)
    cap = cv2.VideoCapture(v_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    dur = total_frames / float(fps)

    blue_water_sum = 0
    green_nature_sum = 0
    red_ninja_sum = 0
    yellow_lego_sum = 0

    samples = 0
    for f_idx in range(int(fps), max(int(fps) + 1, total_frames - int(fps)), int(fps*2)):
        cap.set(cv2.CAP_PROP_POS_FRAMES, f_idx)
        ret, frame = cap.read()
        if not ret:
            break

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        b_mask = cv2.inRange(hsv, np.array([90, 50, 50]), np.array([130, 255, 255]))
        g_mask = cv2.inRange(hsv, np.array([35, 40, 40]), np.array([85, 255, 255]))
        r_mask = cv2.inRange(hsv, np.array([0, 70, 70]), np.array([10, 255, 255]))
        y_mask = cv2.inRange(hsv, np.array([20, 100, 100]), np.array([34, 255, 255]))

        blue_water_sum += np.sum(b_mask > 0) / float(frame.shape[0]*frame.shape[1])
        green_nature_sum += np.sum(g_mask > 0) / float(frame.shape[0]*frame.shape[1])
        red_ninja_sum += np.sum(r_mask > 0) / float(frame.shape[0]*frame.shape[1])
        yellow_lego_sum += np.sum(y_mask > 0) / float(frame.shape[0]*frame.shape[1])
        samples += 1

    cap.release()

    if samples > 0:
        b_avg = (blue_water_sum / samples) * 100
        g_avg = (green_nature_sum / samples) * 100
        r_avg = (red_ninja_sum / samples) * 100
        y_avg = (yellow_lego_sum / samples) * 100

        tag = "Geral"
        if b_avg > 15:
            tag = "Canais / Agua / Barcos"
        elif g_avg > 25:
            tag = "Natureza / Castelo / Parque"
        elif r_avg > 6:
            tag = "Ninjago / Piratas"
        elif y_avg > 5:
            tag = "Edificios de Lego / Miniland"

        print(f"  • {v_name} ({dur:.1f}s) -> Tag: {tag} [B:{b_avg:.1f}%, G:{g_avg:.1f}%, R:{r_avg:.1f}%, Y:{y_avg:.1f}%]")
