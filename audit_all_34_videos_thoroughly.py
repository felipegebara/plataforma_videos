import os
import glob
import cv2
import json
from pathlib import Path

p = r"c:\Users\fgeba\Documents\quizz\lendas e historia\output\legoland"
videos = sorted(glob.glob(p + "/*.mp4"))

audit_dir = Path(__file__).resolve().parent / "scratch" / "full_audit"
audit_dir.mkdir(parents=True, exist_ok=True)

print(f"Auditando visualmente {len(videos)} vídeos brutos da Legoland...")

video_report = []

for idx, v_path in enumerate(videos, 1):
    v_name = os.path.basename(v_path)
    cap = cv2.VideoCapture(v_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    dur = total_frames / float(fps)

    clean_name = v_name.replace(".mp4", "").replace(" ", "_").replace("(", "").replace(")", "").replace("@", "")

    # Save frames at 30%, 50%, 70% of video duration
    frames_info = []
    for pct in [0.3, 0.5, 0.7]:
        sec = dur * pct
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(sec * fps))
        ret, frame = cap.read()
        if ret:
            img_fname = f"v{idx:02d}_{clean_name}_pct{int(pct*100)}.jpg"
            img_fpath = audit_dir / img_fname
            cv2.imwrite(str(img_fpath), frame)
            frames_info.append(str(img_fpath))

    cap.release()
    print(f"  [{idx:02d}/34] {v_name} | Duração: {dur:.1f}s | {len(frames_info)} quadros extraídos")

print("\nAuditoria visual concluída! Imagens salvas em:", audit_dir)
