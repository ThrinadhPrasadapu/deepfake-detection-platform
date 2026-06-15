from pathlib import Path
from PIL import Image
from torch.utils.data import Dataset


class DeepfakeImageDataset(Dataset):
    """
    Expected folder structure (FaceForensics++ compatible):

        data/image/
        ├── train/
        │   ├── real/    ← authentic face crops (from original_sequences/)
        │   └── fake/    ← deepfake face crops  (from manipulated_sequences/)
        └── val/
            ├── real/
            └── fake/

    Label:  0 = real,  1 = fake
    """
    EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

    def __init__(self, root: Path, transform=None):
        self.transform = transform
        self.samples: list[tuple[Path, int]] = []

        for label, folder in [(0, "real"), (1, "fake")]:
            folder_path = root / folder
            if not folder_path.exists():
                raise FileNotFoundError(
                    f"Missing class folder: {folder_path}\n"
                    "Structure expected:\n"
                    "  data/image/train/real/  ← place real face images here\n"
                    "  data/image/train/fake/  ← place deepfake images here"
                )
            for p in folder_path.iterdir():
                if p.suffix.lower() in self.EXTENSIONS:
                    self.samples.append((p, label))

        real_n = sum(1 for _, l in self.samples if l == 0)
        fake_n = len(self.samples) - real_n
        print(f"[Dataset] {root.name}: {real_n} real, {fake_n} fake  (total={len(self.samples)})")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        image = Image.open(img_path).convert("RGB")
        if self.transform:
            image = self.transform(image)
        return image, label
