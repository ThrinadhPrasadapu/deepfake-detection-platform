import io
import base64
import tempfile
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch
import cv2
from PIL import Image
from pathlib import Path

from services.image_service import ImageDetectionService, TRANSFORM


class VideoDetectionService:
    def __init__(self):
        # Reuse the image model for per-frame scoring
        self.image_svc = ImageDetectionService()
        self.device = self.image_svc.device

    def analyze(self, video_bytes: bytes, filename: str) -> dict:
        suffix = Path(filename).suffix or ".mp4"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
            f.write(video_bytes)
            tmp_path = Path(f.name)

        try:
            cap = cv2.VideoCapture(str(tmp_path))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            duration = total_frames / fps

            # Sample up to 20 frames evenly spaced across the video
            n_samples = min(20, max(1, total_frames))
            sample_indices = {int(i * total_frames / n_samples) for i in range(n_samples)}

            frame_scores: list[dict] = []
            frame_idx = 0

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                if frame_idx in sample_indices:
                    pil_frame = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    score = self._score_frame(pil_frame)
                    frame_scores.append({
                        "frame": frame_idx,
                        "timestamp": round(frame_idx / fps, 2),
                        "fakeScore": round(float(score), 4),
                    })
                frame_idx += 1

            cap.release()
        finally:
            tmp_path.unlink(missing_ok=True)

        if not frame_scores:
            raise ValueError("No frames could be extracted from video")

        scores = [f["fakeScore"] for f in frame_scores]
        avg_score = float(np.mean(scores))
        is_deepfake = avg_score >= 0.5
        confidence = round((avg_score if is_deepfake else 1.0 - avg_score) * 100, 1)
        suspicious = sum(1 for s in scores if s >= 0.5)

        timeline_b64 = self._render_timeline(frame_scores)

        return {
            "isDeepfake": is_deepfake,
            "confidence": confidence,
            "frameTimeline": frame_scores,
            "timelineImage": timeline_b64,
            "details": [
                {"label": "Model", "value": "ResNet50 frame-scorer"},
                {"label": "Total Frames", "value": str(total_frames)},
                {"label": "Frames Analyzed", "value": str(len(frame_scores))},
                {"label": "Duration", "value": f"{duration:.1f}s"},
                {"label": "Avg Fake Score", "value": f"{avg_score * 100:.1f}%"},
                {"label": "Suspicious Frames", "value": f"{suspicious} / {len(frame_scores)}"},
            ],
        }

    def _score_frame(self, frame: Image.Image) -> float:
        tensor = TRANSFORM(frame).unsqueeze(0).to(self.device)
        with torch.no_grad():
            logits = self.image_svc.model(tensor)
            probs = torch.softmax(logits, dim=1)
        return float(probs[0, 1])

    @staticmethod
    def _render_timeline(frame_scores: list[dict]) -> str:
        timestamps = [f["timestamp"] for f in frame_scores]
        scores = [f["fakeScore"] * 100 for f in frame_scores]
        bar_colors = ["#ef4444" if s >= 50 else "#22c55e" for s in scores]

        fig, ax = plt.subplots(figsize=(9, 3.5))
        bar_width = max(timestamps) / (len(timestamps) + 1) if len(timestamps) > 1 else 1
        ax.bar(timestamps, scores, width=bar_width, color=bar_colors, edgecolor="none")
        ax.axhline(y=50, color="#f97316", linestyle="--", linewidth=1.2, label="Threshold (50%)")
        ax.fill_between(timestamps, scores, 50,
                        where=[s >= 50 for s in scores],
                        color="#ef4444", alpha=0.15)
        ax.set_xlabel("Time (seconds)", fontsize=10)
        ax.set_ylabel("Fake Score (%)", fontsize=10)
        ax.set_title("Frame-level Deepfake Score Timeline", fontsize=12)
        ax.set_ylim(0, 100)
        ax.legend(fontsize=8)
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        return "data:image/png;base64," + base64.b64encode(buf.read()).decode()
