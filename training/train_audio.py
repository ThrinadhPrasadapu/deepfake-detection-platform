"""
Train the Mel-Spectrogram CNN for deepfake audio detection.

Usage (run from project root):
    python -m training.train_audio

Dataset setup:
    Option A — WaveFake (easiest, fully free):
        pip install wavefake
        python -c "import wavefake; wavefake.download('data/audio')"
        Then organise into data/audio/train/real|fake/ and data/audio/val/real|fake/

    Option B — ASVspoof 2019 LA (research standard):
        Register at https://datashare.ed.ac.uk/handle/10283/3336
        Download LA.zip, extract, then copy:
          LA/ASVspoof2019_LA_train/flac/  → data/audio/train/real/ (genuine) + fake/ (spoof)
        Use the protocol file (LA/ASVspoof2019.LA.cm.train.trn.txt) to split genuine/spoof.

    Option C — Simple folder (any .wav files you have):
        data/audio/train/real/  ← real human voices
        data/audio/train/fake/  ← AI-generated / cloned voices
        data/audio/val/real/
        data/audio/val/fake/
"""
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from pathlib import Path

from training.dataset_audio import DeepfakeAudioDataset


# ── Model (must match backend/services/audio_service.py AudioCNN) ─────────────

class AudioCNN(nn.Module):
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


# ── Hyperparameters ────────────────────────────────────────────────────────────

DATA_ROOT      = Path("data/audio")
MODEL_SAVE     = Path("backend/models/audio_cnn.pth")
EPOCHS         = 30
BATCH_SIZE     = 64
LR             = 3e-4
WEIGHT_DECAY   = 1e-4
NUM_WORKERS    = 4


# ── Training loop ──────────────────────────────────────────────────────────────

def train():
    MODEL_SAVE.parent.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[KYROS Audio Train] Device: {device}")

    train_ds = DeepfakeAudioDataset(DATA_ROOT / "train", augment=True)
    val_ds   = DeepfakeAudioDataset(DATA_ROOT / "val",   augment=False)

    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True,
                              num_workers=NUM_WORKERS, pin_memory=True)
    val_loader   = DataLoader(val_ds,   batch_size=BATCH_SIZE, shuffle=False,
                              num_workers=NUM_WORKERS, pin_memory=True)

    model     = AudioCNN().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS)
    criterion = nn.CrossEntropyLoss()

    best_val_acc = 0.0

    for epoch in range(1, EPOCHS + 1):
        # ── Train ──────────────────────────────────────────────────────────────
        model.train()
        running_loss = correct = total = 0
        for specs, labels in train_loader:
            specs, labels = specs.to(device), labels.to(device)
            optimizer.zero_grad()
            logits = model(specs)
            loss = criterion(logits, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * specs.size(0)
            correct += (logits.argmax(1) == labels).sum().item()
            total   += labels.size(0)

        train_acc = correct / total * 100

        # ── Validate ───────────────────────────────────────────────────────────
        model.eval()
        val_correct = val_total = 0
        with torch.no_grad():
            for specs, labels in val_loader:
                specs, labels = specs.to(device), labels.to(device)
                val_correct += (model(specs).argmax(1) == labels).sum().item()
                val_total   += labels.size(0)

        val_acc = val_correct / val_total * 100
        scheduler.step()

        print(f"Epoch {epoch:>3}/{EPOCHS}  "
              f"loss={running_loss/total:.4f}  "
              f"train={train_acc:.2f}%  val={val_acc:.2f}%")

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), MODEL_SAVE)
            print(f"  ✓ Saved best model  (val={val_acc:.2f}%)")

    print(f"\nTraining complete. Best val accuracy: {best_val_acc:.2f}%")
    print(f"Weights saved to: {MODEL_SAVE}")


if __name__ == "__main__":
    train()
