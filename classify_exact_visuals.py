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

audit_dir = r"c:\Users\fgeba\Documents\quizz\lendas e historia\scratch\full_audit"
img_files = sorted(glob.glob(audit_dir + "/*.jpg"))

video_groups = {}
for img_p in img_files:
    fname = os.path.basename(img_p)
    v_tag = fname.split("_pct")[0]
    if v_tag not in video_groups:
        video_groups[v_tag] = []
    video_groups[v_tag].append(img_p)

print(f"=== CLASSIFICAÇÃO VISUAL RIGOROSA DE {len(video_groups)} VÍDEOS BRUTOS ===\n")

mapping_results = []

for v_tag, imgs in video_groups.items():
    avg_blue = 0
    avg_green = 0
    avg_red = 0
    avg_yellow = 0
    avg_bright = 0

    for img_p in imgs:
        img = cv2.imread(img_p)
        if img is None:
            continue
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h, s, v = hsv[:,:,0], hsv[:,:,1], hsv[:,:,2]

        blue_m = (h >= 90) & (h <= 130) & (s >= 50) & (v >= 50)
        green_m = (h >= 35) & (h <= 85) & (s >= 40) & (v >= 40)
        red_m = ((h <= 10) | (h >= 170)) & (s >= 70) & (v >= 70)
        yellow_m = (h >= 20) & (h <= 34) & (s >= 100) & (v >= 100)

        total_px = float(img.shape[0] * img.shape[1])
        avg_blue += np.sum(blue_m) / total_px
        avg_green += np.sum(green_m) / total_px
        avg_red += np.sum(red_m) / total_px
        avg_yellow += np.sum(yellow_m) / total_px
        avg_bright += np.mean(v)

    n = max(1, len(imgs))
    b_pct = (avg_blue / n) * 100
    g_pct = (avg_green / n) * 100
    r_pct = (avg_red / n) * 100
    y_pct = (avg_yellow / n) * 100
    br_avg = avg_bright / n

    descr = "Outros / Cenario Geral"
    if r_pct > 12.0:
        descr = "NINJAGO WORLD (Portal vermelho, estatuas ninja)"
    elif y_pct > 12.0 and r_pct > 2.0:
        descr = "BANDA DO CAPITAO JACK SPARROW (Palco de piratas de Lego)"
    elif b_pct > 30.0:
        descr = "PORTO DE COPENHAGEM / NYHAVN (Agua e casinhas coloridas)"
    elif b_pct > 15.0 and y_pct > 4.0:
        descr = "BARCOS INTERATIVOS / ECLUSAS COM AGUA REAL"
    elif g_pct > 30.0:
        descr = "MONTANHA-RUSSA DRAGON COASTER / CASTELO MEDIEVAL"
    elif y_pct > 6.0 and g_pct > 15.0:
        descr = "MINI CITY DE LEGO / CIDADES E PREDIOS"
    elif br_avg < 60:
        descr = "ATRACAO SUBMARINA / FUNDO DO MAR / ESCULTURAS"

    clean_v_tag = v_tag.replace("WhatsApp_Video_2026-08-12_at_18.", "").replace("v", "Vid ")
    print(f"  - {clean_v_tag:<35} -> {descr}")
    mapping_results.append((v_tag, descr))
