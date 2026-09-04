import os
import sys
from pathlib import Path
from moviepy import VideoFileClip
from PIL import Image

sys.path.append(str(Path(__file__).resolve().parent))

odense_dir = Path(r"c:\Users\fgeba\Documents\quizz\lendas e historia\output\odense")

videos = sorted(list(odense_dir.glob("*.mp4")))
images = sorted(list(odense_dir.glob("*.jpeg")) + list(odense_dir.glob("*.jpg")))

print("=== ANÁLISE DE MÍDIAS DA PASTA ODENSE ===")
print(f"Total de Vídeos: {len(videos)}")
print(f"Total de Imagens: {len(images)}\n")

print("--- VÍDEOS DETALHADOS ---")
total_vid_dur = 0.0
for idx, v in enumerate(videos, 1):
    try:
        clip = VideoFileClip(str(v))
        dur = clip.duration
        total_vid_dur += dur
        w, h = clip.w, clip.h
        clip.close()
        print(f"Vídeo {idx:02d}: {v.name} | Duração: {dur:.2f}s | Resolução: {w}x{h}")
    except Exception as e:
        print(f"Vídeo {idx:02d}: {v.name} | Erro ao analisar: {e}")

print(f"\nDuração Total Somada dos Vídeos: {total_vid_dur:.2f}s ({total_vid_dur/60.0:.2f} min)\n")

print("--- IMAGENS DETALHADAS ---")
for idx, img in enumerate(images, 1):
    try:
        im = Image.open(img)
        w, h = im.size
        print(f"Imagem {idx:02d}: {img.name} | Dimensão: {w}x{h}")
    except Exception as e:
        print(f"Imagem {idx:02d}: {img.name} | Erro ao analisar: {e}")
