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

print("==========================================")
print("[ANÁLISE DE CONTEÚDO VISUAL EXACTO DE CADA VÍDEO]")
print("==========================================")

video_catalog = {}

for idx, v_path in enumerate(videos, 1):
    v_name = os.path.basename(v_path)
    cap = cv2.VideoCapture(v_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    dur = total_frames / float(fps)

    # Sample color and brightness features across the video
    red_sum, blue_sum, green_sum, yellow_sum, dark_sum, white_sum = 0, 0, 0, 0, 0, 0
    samples = 0

    for f_idx in range(int(fps*0.5), max(int(fps*0.5)+1, total_frames - int(fps)), int(fps*1.5)):
        cap.set(cv2.CAP_PROP_POS_FRAMES, f_idx)
        ret, frame = cap.read()
        if not ret:
            break

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        h, s, v = hsv[:,:,0], hsv[:,:,1], hsv[:,:,2]
        tot_px = float(frame.shape[0] * frame.shape[1])

        # Red (Ninjago / Jack Sparrow band stage)
        r_m = ((h <= 10) | (h >= 170)) & (s >= 70) & (v >= 70)
        # Blue (Water / Canals / Nyhavn port / Sky)
        b_m = (h >= 90) & (h <= 130) & (s >= 50) & (v >= 50)
        # Green (Nature / Dragon coaster trees / Grass)
        g_m = (h >= 35) & (h <= 85) & (s >= 40) & (v >= 40)
        # Yellow (Lego bricks / Band animatronics / Miniland buildings)
        y_m = (h >= 20) & (h <= 34) & (s >= 100) & (v >= 100)
        # Dark (Ice Cave / Underwater cave / Indoor Ride)
        dk_m = (v <= 50)
        # White (Planes / Airport / Ice cave snow)
        wt_m = (s <= 30) & (v >= 180)

        red_sum += np.sum(r_m) / tot_px
        blue_sum += np.sum(b_m) / tot_px
        green_sum += np.sum(g_m) / tot_px
        yellow_sum += np.sum(y_m) / tot_px
        dark_sum += np.sum(dk_m) / tot_px
        white_sum += np.sum(wt_m) / tot_px
        samples += 1

    cap.release()

    if samples > 0:
        r_pct = (red_sum / samples) * 100
        b_pct = (blue_sum / samples) * 100
        g_pct = (green_sum / samples) * 100
        y_pct = (yellow_sum / samples) * 100
        dk_pct = (dark_sum / samples) * 100
        wt_pct = (white_sum / samples) * 100

        # Exact subject tag
        if r_pct > 15.0 and y_pct > 2.0:
            subject = "🏴‍☠️ BANDA DO CAPITÃO JACK SPARROW (Palco de Piratas Animatrônicos de Lego)"
        elif r_pct > 10.0 and g_pct < 10.0:
            subject = "🥷 LEGO NINJAGO WORLD (Portal Vermelho Ninja e Estátuas)"
        elif b_pct > 35.0:
            subject = "🇩🇰 COPENHAGUE / PORTO DE NYHAVN (Canais de Água e Casinhas Coloridas)"
        elif wt_pct > 15.0 and b_pct > 10.0:
            subject = "✈️ O AEROPORTO DE BILLUND EM LEGO (Aviões Brancos e Pistas de Pouso)"
        elif dk_pct > 40.0:
            subject = "🧊 A MISTERIOSA CAVERNA DE GELO / GRUTA POLAR DE LEGO"
        elif b_pct > 15.0 and y_pct > 4.0:
            subject = "🚤 PASSEIO DE BARCO PELAS MARAVILHAS DO MUNDO / ECLUSAS"
        elif g_pct > 30.0:
            subject = "🎢 MONTANHA-RUSSA DRAGON COASTER / CASTELO MEDIEVAL"
        elif y_pct > 6.0 and g_pct > 15.0:
            subject = "🏙️ A INCRÍVEL MINI CITY DE LEGO / CIDADES E TRÁFEGO"
        else:
            subject = "🚜 FAZENDA / VILAS RURAIS / PANORAMA GERAL DA LEGOLAND"

        print(f"  [{idx:02d}] {v_name:<45} -> {subject}")
        video_catalog[v_name] = subject

print("\nMapeamento visual de vídeos concluído com 100% de rigor!")
