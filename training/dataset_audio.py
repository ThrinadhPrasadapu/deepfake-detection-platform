"""
Audio dataset loader for deepfake detection training.

Expected folder structure (works with ASVspoof 2019 LA extracted files):

    data/audio/
    ├── train/
    │   ├── real/    ← genuine speech (.wav/.flac/.mp3)
    │   └── fake/    ← TTS / voice-cloned / GAN-synthesized speech
    └── val/
        ├── real/
        └── fake/

Recommended datasets:
  - ASVspoof 2019 LA  : https://datashare.ed.ac.uk/handle/10283/3336  (free)
  - FakeAVCeleb       : https://github.com/DASH-Lab/FakeAVCeleb       (free)
  - WaveFake          : https://github.com/RUB-SysSec/WaveFake         (free)
"""
import random
import numpy as np
import librosa
import torch
from torch.utils.data import Dataset
from pathlib import Path
from PIL import Image


class DeepfakeAudioDataset(Dataset):
    EXTENSIONS = {".wav", ".flac", ".mp3", ".ogg", ".m4a"}
    TARGET_SR = 16_000
    N_MELS = 128
    FIXED_FRAMES = 128  # time axis fixed length

    def __init__(self, root: Path, augment: bool = False):
        self.augment = augment
        self.samples: list[tuple[Path, int]] = []

        for label, folder in [(0, "real"), (1, "fake")]:
            folder_path = root / folder
            if not folder_path.exists():
                raise FileNotFoundError(
                    f"Missing folder: {folder_path}\n"
                    "Create data/audio/train/real/ and data/audio/train/fake/ "
                    "with .wav/.flac files from ASVspoof 2019 or WaveFake."
                )
            for p in folder_path.iterdir():
                if p.suffix.lower() in self.EXTENSIONS:
                    self.samples.append((p, label))

        real_n = sum(1 for _, l in self.samples if l == 0)
        fake_n = len(self.samples) - real_n
        print(f"[AudioDataset] {root.name}: {real_n} real, {fake_n} fake  (total={len(self.samples)})")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        audio_path, label = self.samples[idx]

        try:
            y, sr = librosa.load(str(audio_path), sr=self.TARGET_SR, mono=True)
        except Exception as e:
            # Return silence on corrupt file — rare but avoids crashing a long training run
            y = np.zeros(self.TARGET_SR, dtype=np.float32)

        if self.augment:
            y = self._augment(y)

        mel = librosa.feature.melspectrogram(y=y, sr=self.TARGET_SR, n_mels=self.N_MELS, fmax=8000)
        mel_db = librosa.power_to_db(mel, ref=np.max)
        mel_norm = self._resize_and_normalize(mel_db)

        tensor = torch.FloatTensor(mel_norm).unsqueeze(0)  # (1, 128, 128)
        return tensor, label

    # ── augmentation helpers ───────────────────────────────────────────────────

    def _augment(self, y: np.ndarray) -> np.ndarray:
        """Light augmentations that preserve speech authenticity cues."""
        # Time stretch (±10%)
        if random.random() < 0.4:
            rate = random.uniform(0.9, 1.1)
            y = librosa.effects.time_stretch(y, rate=rate)

        # Pitch shift (±2 semitones)
        if random.random() < 0.4:
            steps = random.uniform(-2, 2)
            y = librosa.effects.pitch_shift(y, sr=self.TARGET_SR, n_steps=steps)

        # Add Gaussian noise (SNR ~20-40 dB)
        if random.random() < 0.3:
            noise_amp = 0.001 * np.std(y)
            y = y + noise_amp * np.random.randn(len(y))

        return y.astype(np.float32)

    def _resize_and_normalize(self, mel_db: np.ndarray) -> np.ndarray:
        img = Image.fromarray(mel_db.astype(np.float32))
        img = img.resize((self.FIXED_FRAMES, self.N_MELS), Image.BILINEAR)
        arr = np.array(img, dtype=np.float32)
        arr = (arr - arr.min()) / (arr.max() - arr.min() + 1e-8)
        return arr
