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
frames_dir = Path(__file__).resolve().parent / "output" / "tamar_frame_samples"
frames_dir.mkdir(parents=True, exist_ok=True)

raw_vids = sorted([f for f in tamar_dir.glob("*.mp4") if not f.name.startswith("._")])

print("==========================================")
print("[ANALISANDO VISUALMENTE OS VÍDEOS BRUTOS DO TAMAR]")
print("==========================================")

for v_idx, vp in enumerate(raw_vids, 1):
    cap = cv2.VideoCapture(str(vp))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_f = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    dur = total_f / fps if fps > 0 else 0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Sample 3 frames at 25%, 50%, 75% of duration
    sample_timestamps = [dur * 0.25, dur * 0.50, dur * 0.75]
    saved_samples = []

    for s_idx, ts in enumerate(sample_timestamps, 1):
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(ts * fps))
        ret, frame = cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(frame_rgb)
            img_name = f"vid_{v_idx:02d}_{vp.stem[:15]}_ts_{int(ts)}s.jpg"
            img_path = frames_dir / img_name
            img_pil.save(img_path, quality=85)
            saved_samples.append(img_name)

    cap.release()
    print(f"Vídeo {v_idx:02d}: {vp.name} ({dur:.1f}s | {w}x{h}) -> Amostras: {saved_samples}")

print("\n✓ Amostras visuais salvas em:", frames_dir)
