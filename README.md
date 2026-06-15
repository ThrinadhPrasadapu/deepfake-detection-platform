# KYROS — AI-Powered Deepfake Detection Platform

KYROS is a full-stack deepfake detection platform that uses real neural networks to analyze images, videos, and audio for AI-generated or manipulated content. It provides confidence scores and explainable AI visualizations so users can see *why* the model flagged something as fake.

---

## Features

- **Image Detection** — ResNet50 (fine-tuned) + MTCNN face crop + GradCAM heatmap overlay
- **Video Detection** — OpenCV frame extraction + per-frame CNN scoring + timeline chart
- **Audio Detection** — Mel-spectrogram CNN + colored spectrogram visualization
- **Explainable AI** — GradCAM highlights exactly which facial region triggered the fake verdict
- **PDF Reports** — Downloadable analysis report for image detections
- **Professional UI** — Next.js 14 + TypeScript + Tailwind CSS + shadcn/ui

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, shadcn/ui |
| Backend | FastAPI, Uvicorn, Python 3.12 |
| Image AI | ResNet50 (PyTorch), MTCNN (facenet-pytorch), GradCAM |
| Video AI | OpenCV, ResNet50 frame scorer |
| Audio AI | librosa, custom AudioCNN (PyTorch) |
| Visualization | matplotlib, reportlab |

---

## Project Structure

```
KYROS/
├── app/                          # Next.js App Router
│   ├── api/detect/               # Proxy routes → FastAPI
│   │   ├── image/route.ts
│   │   ├── video/route.ts
│   │   └── audio/route.ts
│   ├── detect/                   # Detection pages
│   │   ├── image/page.tsx
│   │   ├── video/page.tsx
│   │   └── audio/page.tsx
│   ├── globals.css
│   └── layout.tsx
├── components/                   # Reusable UI components
│   ├── analysis-result.tsx       # Result card + visualizations
│   ├── file-upload.tsx
│   └── navigation.tsx
├── backend/                      # FastAPI Python backend
│   ├── main.py                   # App entry point + CORS
│   ├── routers/
│   │   ├── image.py              # POST /detect/image
│   │   ├── video.py              # POST /detect/video
│   │   └── audio.py              # POST /detect/audio
│   ├── services/
│   │   ├── image_service.py      # ResNet50 + GradCAM pipeline
│   │   ├── video_service.py      # Frame extraction + scoring
│   │   └── audio_service.py      # Mel-spectrogram + AudioCNN
│   ├── utils/
│   │   ├── gradcam.py            # GradCAM implementation
│   │   └── report.py             # PDF report generation
│   ├── models/                   # Trained .pth weights go here
│   └── requirements.txt
└── training/                     # Model training scripts
    ├── train_image.py            # ResNet50 fine-tuning
    ├── train_audio.py            # AudioCNN training
    ├── prepare_celebdf.py        # CelebDF-v2 data preparation
    ├── dataset.py
    ├── dataset_audio.py
    └── config.py
```

---

## How It Works

### Image Detection
```
Upload Image → MTCNN face crop → ResNet50 inference → GradCAM backward pass → Heatmap overlay
```
ResNet50 is pretrained on ImageNet and fine-tuned on deepfake data. Only the last residual block (`layer4`) and FC head are trainable — the rest is frozen for efficient transfer learning. GradCAM hooks into `layer4[-1]` to capture gradients and activations, producing a heatmap of which pixels drove the prediction.

### Video Detection
```
Upload Video → OpenCV extracts 20 frames → ResNet50 scores each frame → Aggregate → Timeline chart
```

### Audio Detection
```
Upload Audio → librosa mel-spectrogram (128x128) → AudioCNN classify → Colored spectrogram PNG
```
The 1D audio signal is converted into a 2D mel-spectrogram image, allowing a standard CNN to classify it without architectural modifications.

---

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.12 (via [Miniforge](https://github.com/conda-forge/miniforge) recommended — system Python 3.14 is not supported by PyTorch)

### 1. Install frontend dependencies

```bash
npm install
```

### 2. Install backend dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Run the backend

```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8001
```

Wait for:
```
INFO: Application startup complete.
INFO: Uvicorn running on http://0.0.0.0:8001
```

### 4. Run the frontend

```bash
npm run dev
```

Open **http://localhost:3000**

> **Note:** The models ship with random weights until trained. Results will be unreliable until you train on a real dataset (see below).

---

## Training on Real Data

### Download CelebDF-v2

1. Go to https://github.com/yuezunli/celeb-deepfakeforensics
2. Fill the Google Form to get the download link
3. Download `Celeb-real/`, `Celeb-synthesis/`, `YouTube-real/`
4. Extract into one folder, e.g. `C:/CelebDF-v2/`

### Prepare face crops

```bash
python -m training.prepare_celebdf --root "C:/CelebDF-v2"
```

This extracts 15 face crops per video and saves them to `data/image/train/` and `data/image/val/`.

### Train the image model

```bash
python -m training.train_image
```

Trains for 20 epochs. Best checkpoint saved to `backend/models/resnet50_deepfake.pth` — the backend auto-loads it on next start.

### Train the audio model

```bash
python -m training.train_audio
```

Expects audio files in `data/audio/train/real/` and `data/audio/train/fake/`.

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/detect/image` | Analyze image file |
| `POST` | `/detect/image/report` | Download PDF report |
| `POST` | `/detect/video` | Analyze video file |
| `POST` | `/detect/audio` | Analyze audio file |

All detection endpoints accept `multipart/form-data` with a `file` field and return:

```json
{
  "isDeepfake": true,
  "confidence": 94.3,
  "processingTime": 1.2,
  "details": [{ "label": "Model", "value": "ResNet50 (fine-tuned)" }],
  "gradcamImage": "data:image/png;base64,..."
}
```

---

## Key Technical Decisions

**Why ResNet50?** — ImageNet pretraining already encodes texture and edge features useful for detecting deepfake artifacts. Transfer learning needs far less data than training from scratch.

**Why freeze early layers?** — Layers 1-3 detect generic features (edges, colours) that don't need retraining. Only `layer4` and the FC head adapt to the deepfake task.

**Why GradCAM?** — Makes predictions interpretable. Users can see which facial region caused the fake verdict, building trust in the system.

**Why mel-spectrogram for audio?** — Converts 1D audio into a 2D image, letting a standard image CNN classify it without architectural changes.

**Why Next.js API Routes as proxy?** — The browser never calls Python directly. Backend URL is hidden from the client and can be changed via one environment variable.

---

## Environment Variables

Create a `.env.local` in the project root to override the backend URL:

```env
BACKEND_URL=http://localhost:8001
```

---

## Author

**Thrinadh Prasadapu**

Built as a full-stack AI portfolio project demonstrating transfer learning, explainable AI, and production-ready API design.
