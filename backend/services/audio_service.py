import io
import base64
import tempfile
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import librosa
from PIL import Image
from pathlib import Path

MODEL_PATH = Path(__file__).parent.parent / "models" / "audio_cnn.pth"


class AudioCNN(nn.Module):
    """Lightweight CNN that classifies 128x128 mel-spectrograms as real or fake."""

    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=1), nn.BatchNorm2d(32), nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1), nn.BatchNorm2d(64), nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1), nn.BatchNorm2d(128), nn.ReLU(),
            nn.AdaptiveAvgPool2d((4, 4)),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(0.5),
            nn.Linear(128 * 16, 256),
            nn.ReLU(),
            nn.Linear(256, 2),
        )

    def forward(self, x):
        return self.classifier(self.features(x))


class AudioDetectionService:
    TARGET_SR = 16_000
    N_MELS = 128
    FIXED_FRAMES = 128

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self._load_model()
        self.model.eval()

    def _load_model(self) -> nn.Module:
        model = AudioCNN().to(self.device)
        if MODEL_PATH.exists():
            state = torch.load(MODEL_PATH, map_location=self.device, weights_only=True)
            model.load_state_dict(state)
            print(f"[KYROS Audio] Loaded weights -> {MODEL_PATH}")
        else:
            print("[KYROS Audio] No trained weights found. Run: python -m training.train_audio")
        return model

    def analyze(self, audio_bytes: bytes, filename: str) -> dict:
        suffix = Path(filename).suffix or ".wav"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
            f.write(audio_bytes)
            tmp_path = Path(f.name)

        try:
            y, sr = librosa.load(str(tmp_path), sr=self.TARGET_SR, mono=True)
        finally:
            tmp_path.unlink(missing_ok=True)

        duration = len(y) / self.TARGET_SR
        mel = librosa.feature.melspectrogram(y=y, sr=self.TARGET_SR, n_mels=self.N_MELS, fmax=8000)
        mel_db = librosa.power_to_db(mel, ref=np.max)

        mel_norm = self._resize_and_normalize(mel_db)
        tensor = torch.FloatTensor(mel_norm).unsqueeze(0).unsqueeze(0).to(self.device)  # (1,1,128,128)

        with torch.no_grad():
            logits = self.model(tensor)
            probs = torch.softmax(logits, dim=1)
            fake_prob = float(probs[0, 1])
            real_prob = float(probs[0, 0])

        spectrogram_b64 = self._render_spectrogram(mel_db, fake_prob)
        is_deepfake = fake_prob >= 0.5
        confidence = round((fake_prob if is_deepfake else real_prob) * 100, 1)

        return {
            "isDeepfake": is_deepfake,
            "confidence": confidence,
            "spectrogramImage": spectrogram_b64,
            "details": [
                {"label": "Model", "value": "Mel-Spectrogram CNN"},
                {"label": "XAI Method", "value": "Spectrogram visualization"},
                {"label": "Sample Rate", "value": f"{self.TARGET_SR:,} Hz"},
                {"label": "Duration", "value": f"{duration:.1f}s"},
                {"label": "Mel Bands", "value": str(self.N_MELS)},
                {"label": "Fake Probability", "value": f"{fake_prob * 100:.1f}%"},
            ],
        }

    def _resize_and_normalize(self, mel_db: np.ndarray) -> np.ndarray:
        img = Image.fromarray(mel_db.astype(np.float32))
        img = img.resize((self.FIXED_FRAMES, self.N_MELS), Image.BILINEAR)
        arr = np.array(img, dtype=np.float32)
        arr = (arr - arr.min()) / (arr.max() - arr.min() + 1e-8)
        return arr

    @staticmethod
    def _render_spectrogram(mel_db: np.ndarray, fake_prob: float) -> str:
        verdict = "FAKE" if fake_prob >= 0.5 else "REAL"
        cmap = "Reds" if fake_prob >= 0.5 else "Blues_r"
        fig, ax = plt.subplots(figsize=(8, 3.5))
        img = ax.imshow(mel_db, aspect="auto", origin="lower", cmap=cmap)
        ax.set_xlabel("Time frames")
        ax.set_ylabel("Mel frequency bands")
        ax.set_title(f"Mel-Spectrogram - {verdict}  ({fake_prob * 100:.1f}% fake probability)")
        plt.colorbar(img, ax=ax, format="%+2.0f dB")
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        return "data:image/png;base64," + base64.b64encode(buf.read()).decode()
