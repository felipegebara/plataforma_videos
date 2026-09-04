import os
from pathlib import Path
from PIL import Image

audit_dir = Path(__file__).resolve().parent / "output" / "tamar_detailed_audit"

for v_dir in sorted(list(audit_dir.glob("vid_*"))):
    frames = sorted(list(v_dir.glob("*.jpg")))
    print(f"\n📁 {v_dir.name} ({len(frames)} frames):")
    for f in frames[:5]:
        img = Image.open(f)
        print(f"   • {f.name} -> Size: {img.size}")
