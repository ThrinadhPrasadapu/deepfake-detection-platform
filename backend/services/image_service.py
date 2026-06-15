import io
import base64
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.cm as cm_lib
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
from pathlib import Path
from utils.gradcam import GradCAM

MODEL_PATH = Path(__file__).parent.parent / "models" / "resnet50_deepfake.pth"

TRANSFORM = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])


def _build_resnet50() -> nn.Module:
    model = models.resnet50(weights=None)
    model.fc = nn.Sequential(
        nn.Dropout(0.5),
        nn.Linear(model.fc.in_features, 2),
    )
    return model


class ImageDetectionService:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self._load_model()
        self.model.eval()
        self.gradcam = GradCAM(self.model, self.model.layer4[-1])
        self._mtcnn = None  # lazy-loaded

    def _load_model(self) -> nn.Module:
        model = _build_resnet50().to(self.device)
        if MODEL_PATH.exists():
            state = torch.load(MODEL_PATH, map_location=self.device, weights_only=True)
            model.load_state_dict(state)
            print(f"[KYROS Image] Loaded weights -> {MODEL_PATH}")
        else:
            print("[KYROS Image] No trained weights found. Run: python -m training.train_image")
        return model

    def _get_mtcnn(self):
        if self._mtcnn is None:
            try:
                from facenet_pytorch import MTCNN
                self._mtcnn = MTCNN(keep_all=False, device=self.device, post_process=False)
            except ImportError:
                self._mtcnn = False
        return None if self._mtcnn is False else self._mtcnn

    def _detect_face(self, image: Image.Image) -> tuple[Image.Image | None, bool]:
        mtcnn = self._get_mtcnn()
        if mtcnn is None:
            return None, False
        try:
            boxes, _ = mtcnn.detect(image)
            if boxes is not None and len(boxes) > 0:
                b = boxes[0].astype(int)
                w, h = image.size
                x1, y1 = max(0, b[0] - 20), max(0, b[1] - 20)
                x2, y2 = min(w, b[2] + 20), min(h, b[3] + 20)
                return image.crop((x1, y1, x2, y2)), True
        except Exception:
            pass
        return None, False

    def analyze(self, image_bytes: bytes, filename: str) -> dict:
        pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        w, h = pil_img.size

        face_crop, face_found = self._detect_face(pil_img)
        analysis_img = face_crop if face_crop else pil_img

        tensor = TRANSFORM(analysis_img).unsqueeze(0).to(self.device)

        # Prediction (no_grad - fast inference)
        with torch.no_grad():
            logits = self.model(tensor)
            probs = torch.softmax(logits, dim=1)
            fake_prob = float(probs[0, 1])
            real_prob = float(probs[0, 0])

        # GradCAM - requires its own forward+backward pass WITH gradients
        cam = self.gradcam.generate(tensor, target_class=1)
        gradcam_b64 = self._overlay_heatmap(analysis_img, cam)

        is_deepfake = fake_prob >= 0.5
        confidence = round((fake_prob if is_deepfake else real_prob) * 100, 1)

        return {
            "isDeepfake": is_deepfake,
            "confidence": confidence,
            "gradcamImage": gradcam_b64,
            "details": [
                {"label": "Model", "value": "ResNet50 (fine-tuned)"},
                {"label": "XAI Method", "value": "GradCAM"},
                {"label": "Resolution", "value": f"{w}x{h}"},
                {"label": "Face Detected", "value": "Yes" if face_found else "No (full image used)"},
                {"label": "Fake Probability", "value": f"{fake_prob * 100:.1f}%"},
                {"label": "Real Probability", "value": f"{real_prob * 100:.1f}%"},
            ],
        }

    @staticmethod
    def _overlay_heatmap(image: Image.Image, cam: np.ndarray) -> str:
        img_arr = np.array(image.resize((224, 224))).astype(np.float32) / 255.0
        heatmap = cm_lib.jet(cam)[:, :, :3]
        overlay = np.clip(0.55 * img_arr + 0.45 * heatmap, 0.0, 1.0)

        fig, axes = plt.subplots(1, 3, figsize=(11, 3.5))
        axes[0].imshow(img_arr);  axes[0].set_title("Original");  axes[0].axis("off")
        axes[1].imshow(heatmap);  axes[1].set_title("GradCAM");   axes[1].axis("off")
        axes[2].imshow(overlay);  axes[2].set_title("Overlay");   axes[2].axis("off")
        plt.tight_layout(pad=0.5)

        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        return "data:image/png;base64," + base64.b64encode(buf.read()).decode()
