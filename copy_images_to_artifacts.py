import shutil
from pathlib import Path

src_dir = Path(r"c:\Users\fgeba\Documents\quizz\lendas e historia\output\images\morro_azul_8_pack")
dst_dir = Path(r"C:\Users\fgeba\.gemini\antigravity\brain\0910298c-5f57-4975-a1e1-10a7451cea7a")

copied_files = []
for i in range(1, 9):
    src = src_dir / f"image_{i}.png"
    dst = dst_dir / f"morro_azul_image_{i}.png"
    if src.exists():
        shutil.copy(src, dst)
        copied_files.append(dst)
        print(f"Copied {src.name} -> {dst.name}")
