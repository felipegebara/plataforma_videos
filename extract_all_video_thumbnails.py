import os
import sys
from pathlib import Path
import cv2
from PIL import Image

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

tamar_dir = Path(r"c:\Users\fgeba\Documents\quizz\lendas e historia\output\tamar floripa")
raw_vids = sorted([f for f in tamar_dir.glob("*.mp4") if not f.name.startswith("._")])
thumb_dir = Path(__file__).resolve().parent / "output" / "tamar_detailed_audit"
thumb_dir.mkdir(parents=True, exist_ok=True)

print("=== AUDITORIA COMPLETA QUADRO A QUADRO DOS VÍDEOS BRUTOS DO TAMAR ===")

for idx, vp in enumerate(raw_vids, 1):
    cap = cv2.VideoCapture(str(vp))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_f = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    dur = total_f / fps if fps > 0 else 0

    v_folder = thumb_dir / f"vid_{idx:02d}_{vp.stem[:20]}"
    v_folder.mkdir(parents=True, exist_ok=True)

    # Save 1 frame every 3 seconds to visually inspect content
    sec = 0
    while sec < dur:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(sec * fps))
        ret, frame = cap.read()
        if ret:
            f_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_p = Image.fromarray(f_rgb)
            img_p.save(v_folder / f"sec_{int(sec):03d}s.jpg", quality=80)
        sec += 3.0

    cap.release()
    print(f"✓ Vídeo {idx:02d}: {vp.name} ({dur:.1f}s) -> Frames salvos em {v_folder.name}")

print("\n🎉 Auditoria visual de quadros concluída!")
