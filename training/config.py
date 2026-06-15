from pathlib import Path
import torchvision.transforms as transforms


class Config:
    # Paths
    data_root = Path("data/image")
    model_save_path = Path("backend/models/resnet50_deepfake.pth")

    # Hyperparameters
    epochs = 20
    batch_size = 32
    lr = 1e-4
    weight_decay = 1e-4
    num_workers = 0  # 0 = main process only (required on Windows)

    train_transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.RandomCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.1, hue=0.05),
        transforms.RandomGrayscale(p=0.05),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
