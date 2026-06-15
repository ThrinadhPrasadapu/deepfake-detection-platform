import numpy as np
import torch
import torch.nn as nn
from PIL import Image


class GradCAM:
    """Gradient-weighted Class Activation Mapping for CNN explainability."""

    def __init__(self, model: nn.Module, target_layer: nn.Module):
        self.model = model
        self._activations: torch.Tensor | None = None
        self._gradients: torch.Tensor | None = None

        self._fwd_hook = target_layer.register_forward_hook(self._capture_activation)
        self._bwd_hook = target_layer.register_full_backward_hook(self._capture_gradient)

    def _capture_activation(self, module, inp, output):
        self._activations = output

    def _capture_gradient(self, module, grad_in, grad_out):
        self._gradients = grad_out[0]

    def generate(self, tensor: torch.Tensor, target_class: int) -> np.ndarray:
        """
        Forward + backward pass -> normalized CAM heatmap (224x224 float32 in [0,1]).
        Do NOT call inside torch.no_grad().
        """
        self.model.zero_grad()
        output = self.model(tensor)
        output[0, target_class].backward()

        if self._gradients is None or self._activations is None:
            raise RuntimeError("GradCAM hooks did not fire - verify target_layer is inside the model")

        weights = self._gradients.mean(dim=(2, 3), keepdim=True)          # (1, C, 1, 1)
        cam = (weights * self._activations).sum(dim=1).squeeze()           # (H, W)
        cam = torch.relu(cam).cpu().detach().numpy()

        lo, hi = cam.min(), cam.max()
        cam = (cam - lo) / (hi - lo + 1e-8)

        cam_resized = np.array(
            Image.fromarray((cam * 255).astype(np.uint8)).resize((224, 224), Image.BILINEAR)
        ) / 255.0
        return cam_resized.astype(np.float32)

    def remove(self):
        self._fwd_hook.remove()
        self._bwd_hook.remove()
