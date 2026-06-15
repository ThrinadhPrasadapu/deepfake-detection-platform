"""
Prepare CelebDF-v2 dataset for KYROS training.

Usage:
    python -m training.prepare_celebdf --root "C:/path/to/CelebDF-v2"

What it does:
    1. Scans Celeb-real/ and YouTube-real/ for real videos
    2. Scans Celeb-synthesis/ for deepfake videos
    3. Extracts up to FRAMES_PER_VIDEO evenly-spaced frames per video
    4. Detects and crops faces using MTCNN
    5. Saves face crops to data/image/train/ and data/image/val/ (80/20 split)

Expected CelebDF-v2 folder layout:
    CelebDF-v2/
    ├── Celeb-real/
    ├── Celeb-synthesis/
    ├── YouTube-real/
    └── List_of_testing_videos.txt
"""

import argparse
import random
import shutil
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

FRAMES_PER_VIDEO = 15   # face crops extracted per video
VAL_SPLIT = 0.2         # 20% of videos go to val
SEED = 42
OUTPUT_ROOT = Path("data/image")


def extract_frames(video_path: Path, n: int) -> list[np.ndarray]:
    cap = cv2.VideoCapture(str(video_path))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total <= 0:
        cap.release()
        return []
    indices = np.linspace(0, total - 1, min(n, total), dtype=int)
    frames = []
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
        ok, frame = cap.read()
        if ok:
            frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    cap.release()
    return frames


def detect_faces(frames: list[np.ndarray], mtcnn):
    crops = []
    for frame in frames:
        pil = Image.fromarray(frame)
        try:
            boxes, _ = mtcnn.detect(pil)
            if boxes is not None and len(boxes) > 0:
                b = boxes[0].astype(int)
                h, w = frame.shape[:2]
                x1 = max(0, b[0] - 20)
                y1 = max(0, b[1] - 20)
                x2 = min(w, b[2] + 20)
                y2 = min(h, b[3] + 20)
                crop = pil.crop((x1, y1, x2, y2)).resize((224, 224))
                crops.append(crop)
        except Exception:
            pass
    return crops


def process_videos(video_paths: list[Path], label: str, split: str, mtcnn, out_root: Path):
    folder = out_root / split / label
    folder.mkdir(parents=True, exist_ok=True)
    saved = 0
    for vid in video_paths:
        frames = extract_frames(vid, FRAMES_PER_VIDEO)
        if not frames:
            continue
        crops = detect_faces(frames, mtcnn)
        for i, crop in enumerate(crops):
            out_path = folder / f"{vid.stem}_{i:03d}.jpg"
            crop.save(out_path, "JPEG", quality=90)
            saved += 1
        print(f"  [{split}/{label}] {vid.name}: {len(crops)} faces saved", flush=True)
    return saved


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, help="Path to CelebDF-v2 root folder")
    args = parser.parse_args()

    celebdf_root = Path(args.root)
    if not celebdf_root.exists():
        raise FileNotFoundError(f"CelebDF-v2 root not found: {celebdf_root}")

    print("Loading MTCNN face detector...")
    from facenet_pytorch import MTCNN
    import torch
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    mtcnn = MTCNN(keep_all=False, device=device, post_process=False)
    print(f"MTCNN ready on {device}")

    # Gather video paths
    real_dirs = [celebdf_root / "Celeb-real", celebdf_root / "YouTube-real"]
    fake_dirs = [celebdf_root / "Celeb-synthesis"]

    real_vids = []
    for d in real_dirs:
        if d.exists():
            real_vids += list(d.glob("*.mp4")) + list(d.glob("*.avi"))

    fake_vids = []
    for d in fake_dirs:
        if d.exists():
            fake_vids += list(d.glob("*.mp4")) + list(d.glob("*.avi"))

    print(f"\nFound: {len(real_vids)} real videos, {len(fake_vids)} fake videos")

    # Shuffle and split
    random.seed(SEED)
    random.shuffle(real_vids)
    random.shuffle(fake_vids)

    def split_list(lst):
        n_val = max(1, int(len(lst) * VAL_SPLIT))
        return lst[n_val:], lst[:n_val]

    real_train, real_val = split_list(real_vids)
    fake_train, fake_val = split_list(fake_vids)

    print(f"Split -> train: {len(real_train)} real, {len(fake_train)} fake")
    print(f"Split -> val:   {len(real_val)} real, {len(fake_val)} fake\n")

    # Clear existing output
    if OUTPUT_ROOT.exists():
        shutil.rmtree(OUTPUT_ROOT)

    total = 0
    print("=== Processing train/real ===")
    total += process_videos(real_train, "real", "train", mtcnn, OUTPUT_ROOT)
    print("=== Processing train/fake ===")
    total += process_videos(fake_train, "fake", "train", mtcnn, OUTPUT_ROOT)
    print("=== Processing val/real ===")
    total += process_videos(real_val, "real", "val", mtcnn, OUTPUT_ROOT)
    print("=== Processing val/fake ===")
    total += process_videos(fake_val, "fake", "val", mtcnn, OUTPUT_ROOT)

    print(f"\nDone! {total} face crops saved to {OUTPUT_ROOT.resolve()}")
    print("Now run:  python -m training.train_image")


if __name__ == "__main__":
    main()
