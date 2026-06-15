"""
Train ResNet50 for deepfake image detection.

Usage (run from project root):
    python -m training.train_image

Dataset setup:
    1. Download FaceForensics++ (request at: https://github.com/ondyari/FaceForensics)
    2. Extract face crops using their provided scripts
    3. Place images under:
         data/image/train/real/   ← frames from original_sequences/
         data/image/train/fake/   ← frames from manipulated_sequences/
         data/image/val/real/
         data/image/val/fake/

    Alternatively, use CelebDF-v2 (free, no registration):
    https://github.com/yuezunli/celeb-deepfakeforensics
"""
import torch
import torch.nn as nn
import torchvision.models as models
from torch.utils.data import DataLoader

from training.config import Config
from training.dataset import DeepfakeImageDataset


def build_model(device: torch.device) -> nn.Module:
    model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)

    # Freeze backbone except layer4 — transfer-learn efficiently
    for param in model.parameters():
        param.requires_grad = False
    for param in model.layer4.parameters():
        param.requires_grad = True

    model.fc = nn.Sequential(
        nn.Dropout(0.5),
        nn.Linear(model.fc.in_features, 2),
    )
    return model.to(device)


def train():
    cfg = Config()
    cfg.model_save_path.parent.mkdir(parents=True, exist_ok=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[KYROS Train] Device: {device}")

    train_ds = DeepfakeImageDataset(cfg.data_root / "train", cfg.train_transform)
    val_ds   = DeepfakeImageDataset(cfg.data_root / "val",   cfg.val_transform)

    train_loader = DataLoader(train_ds, batch_size=cfg.batch_size, shuffle=True,
                              num_workers=cfg.num_workers, pin_memory=True)
    val_loader   = DataLoader(val_ds,   batch_size=cfg.batch_size, shuffle=False,
                              num_workers=cfg.num_workers, pin_memory=True)

    model     = build_model(device)
    optimizer = torch.optim.Adam(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=cfg.lr, weight_decay=cfg.weight_decay,
    )
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=cfg.epochs)
    criterion = nn.CrossEntropyLoss()

    best_val_acc = 0.0

    for epoch in range(1, cfg.epochs + 1):
        # ── Train ─────────────────────────────────────────────────────────
        model.train()
        running_loss = correct = total = 0
        for imgs, labels in train_loader:
            imgs, labels = imgs.to(device), labels.to(device)
            optimizer.zero_grad()
            logits = model(imgs)
            loss = criterion(logits, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * imgs.size(0)
            correct += (logits.argmax(1) == labels).sum().item()
            total   += labels.size(0)

        train_acc = correct / total * 100

        # ── Validate ──────────────────────────────────────────────────────
        model.eval()
        val_correct = val_total = 0
        with torch.no_grad():
            for imgs, labels in val_loader:
                imgs, labels = imgs.to(device), labels.to(device)
                val_correct += (model(imgs).argmax(1) == labels).sum().item()
                val_total   += labels.size(0)

        val_acc = val_correct / val_total * 100
        scheduler.step()

        print(f"Epoch {epoch:>3}/{cfg.epochs}  "
              f"loss={running_loss/total:.4f}  "
              f"train={train_acc:.2f}%  val={val_acc:.2f}%")

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), cfg.model_save_path)
            print(f"  ✓ Saved best model  (val={val_acc:.2f}%)")

    print(f"\nTraining complete. Best val accuracy: {best_val_acc:.2f}%")
    print(f"Weights saved to: {cfg.model_save_path}")


if __name__ == "__main__":
    train()
