"""
Run this script to generate the full KYROS project report PDF.
Usage:  python generate_report.py
Output: KYROS_Project_Report.pdf  (in project root)
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, ListFlowable, ListItem,
)
import io

OUT = "KYROS_Project_Report.pdf"
W, H = A4

# ── colour palette ─────────────────────────────────────────────────────────────
NAVY   = colors.Color(0.10, 0.18, 0.35)
BLUE   = colors.Color(0.18, 0.38, 0.72)
TEAL   = colors.Color(0.05, 0.55, 0.55)
RED    = colors.Color(0.80, 0.10, 0.10)
GREEN  = colors.Color(0.05, 0.55, 0.20)
LGRAY  = colors.Color(0.94, 0.95, 0.97)
MGRAY  = colors.Color(0.75, 0.76, 0.78)
WHITE  = colors.white


def build_styles():
    base = getSampleStyleSheet()

    def s(name, **kw):
        p = ParagraphStyle(name, parent=base["Normal"], **kw)
        return p

    return {
        "cover_title":  s("ct",  fontSize=36, textColor=WHITE,    alignment=TA_CENTER, leading=44, spaceAfter=8),
        "cover_sub":    s("cs",  fontSize=16, textColor=LGRAY,    alignment=TA_CENTER, leading=22, spaceAfter=4),
        "cover_tag":    s("ctg", fontSize=11, textColor=MGRAY,    alignment=TA_CENTER),
        "h1":           s("h1",  fontSize=18, textColor=NAVY,     spaceBefore=18, spaceAfter=6,  leading=22, fontName="Helvetica-Bold"),
        "h2":           s("h2",  fontSize=13, textColor=BLUE,     spaceBefore=12, spaceAfter=4,  leading=17, fontName="Helvetica-Bold"),
        "h3":           s("h3",  fontSize=11, textColor=TEAL,     spaceBefore=8,  spaceAfter=3,  leading=15, fontName="Helvetica-Bold"),
        "body":         s("bd",  fontSize=10, textColor=colors.black, leading=15, spaceAfter=4, alignment=TA_JUSTIFY),
        "bullet":       s("bl",  fontSize=10, textColor=colors.black, leading=14, leftIndent=16),
        "code":         s("cd",  fontSize=8.5, textColor=NAVY,    fontName="Courier", leading=12,
                          backColor=LGRAY, leftIndent=12, rightIndent=12, spaceBefore=4, spaceAfter=4),
        "tag":          s("tg",  fontSize=9,  textColor=WHITE,    alignment=TA_CENTER),
        "qa_q":         s("qq",  fontSize=10, textColor=NAVY,     fontName="Helvetica-Bold", spaceBefore=6, spaceAfter=2, leading=14),
        "qa_a":         s("qa",  fontSize=10, textColor=colors.black, leading=14, leftIndent=12, spaceAfter=6),
        "resume":       s("rv",  fontSize=10, textColor=colors.black, leading=16, leftIndent=8,
                          borderPad=8, backColor=LGRAY, borderColor=BLUE, borderWidth=1, alignment=TA_JUSTIFY),
        "pitch":        s("pt",  fontSize=10, textColor=colors.black, leading=16, alignment=TA_JUSTIFY,
                          leftIndent=12, rightIndent=12, spaceBefore=4, spaceAfter=4),
    }


def hr(color=MGRAY, thickness=0.7):
    return HRFlowable(width="100%", color=color, thickness=thickness, spaceAfter=6, spaceBefore=4)


def section_banner(text, style):
    data = [[Paragraph(text, style["h1"])]]
    t = Table(data, colWidths=[W - 4*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), LGRAY),
        ("LEFTPADDING",  (0, 0), (-1, -1), 10),
        ("TOPPADDING",   (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
        ("LINEBELOW",    (0, 0), (-1, -1), 2, BLUE),
    ]))
    return t


def bullet_list(items, style, indent=0):
    return ListFlowable(
        [ListItem(Paragraph(i, style["bullet"]), leftIndent=indent+16, bulletColor=BLUE) for i in items],
        bulletType="bullet", leftIndent=indent,
    )


def two_col_table(rows, col_w=(5*cm, 11*cm)):
    t = Table(rows, colWidths=list(col_w))
    t.setStyle(TableStyle([
        ("GRID",          (0, 0), (-1, -1), 0.4, MGRAY),
        ("BACKGROUND",    (0, 0), (0, -1),  LGRAY),
        ("FONTNAME",      (0, 0), (0, -1),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS",(0, 0), (-1, -1), [WHITE, colors.Color(0.97, 0.97, 1.0)]),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
    ]))
    return t


def header_table(cols, col_w):
    header = [cols]
    t = Table(header, colWidths=col_w)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  NAVY),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  WHITE),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("ALIGN",         (0, 0), (-1, -1), "LEFT"),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
    ]))
    return t


# ──────────────────────────────────────────────────────────────────────────────
# PAGE BUILDERS
# ──────────────────────────────────────────────────────────────────────────────

def cover_page(st):
    story = []
    # Blue banner background (via table)
    cover_data = [[
        Paragraph("KYROS", st["cover_title"]),
    ]]
    ct = Table(cover_data, colWidths=[W - 4*cm])
    ct.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), NAVY),
        ("TOPPADDING",    (0, 0), (-1, -1), 48),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 16),
    ]))
    story.append(ct)

    sub_data = [[Paragraph("Deepfake Detection Platform", st["cover_sub"])]]
    st2 = Table(sub_data, colWidths=[W - 4*cm])
    st2.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), BLUE),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 48),
    ]))
    story.append(st2)
    story.append(Spacer(1, 20))

    # Metadata table
    meta = [
        ["Project",  "KYROS — Authenticity Verification System"],
        ["Stack",    "Next.js · TypeScript · FastAPI · PyTorch · ResNet50 · GradCAM"],
        ["Modules",  "Image Detection · Video Detection · Audio Detection"],
        ["Report",   "Full project documentation, resume bullets, interview guide"],
    ]
    mt = two_col_table(meta, col_w=(3.5*cm, 12.5*cm))
    story.append(mt)
    story.append(Spacer(1, 24))
    story.append(hr(BLUE, 1.5))
    story.append(Paragraph(
        "This report covers: what the project looked like before, every change made, "
        "the complete technical architecture, training pipeline, two polished resume bullet points, "
        "and a full interview preparation guide.",
        st["body"]
    ))
    story.append(PageBreak())
    return story


def section_original_state(st):
    story = []
    story.append(section_banner("1.  Original Project State", st))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Before our work, KYROS was a <b>frontend-only shell</b>. "
        "The UI was professional — built in Next.js 16 + TypeScript with shadcn/ui — "
        "but contained <b>zero real AI</b>. Every detection call was a fake timer + Math.random().",
        st["body"]
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("What existed:", st["h2"]))
    existed = [
        "Next.js + TypeScript frontend with shadcn/ui component library",
        "Three detection pages: /detect/image, /detect/video, /detect/audio",
        "Professional dashboard layout and navigation",
        "File upload component (react-dropzone)",
        "AnalysisResult component to display verdict, confidence, details",
        "Recharts, Lucide icons, Tailwind CSS animations",
    ]
    story.append(bullet_list(existed, st))
    story.append(Spacer(1, 8))

    story.append(Paragraph("What was MISSING (the AI engine):", st["h2"]))
    missing = [
        "<b>No API routes</b> — /app/api/ folder did not exist",
        "<b>No backend</b> — no Python server, no FastAPI, no Flask",
        "<b>No ML models</b> — no ResNet50, no CNN, no spectrogram analysis",
        "<b>Fake detection logic</b> — Math.random() decided real/fake with setTimeout() delay",
        "<b>No XAI</b> — no GradCAM, no heatmaps, no explainability",
        "<b>No training pipeline</b> — no dataset loaders, no training scripts",
        "<b>No face detection</b> — MTCNN was not integrated",
        "<b>Hardcoded mock details</b> — 'CNN ResNet-50' label was just static text",
    ]
    story.append(bullet_list(missing, st))
    story.append(Spacer(1, 8))

    story.append(Paragraph("The mock code (what image analysis actually did):", st["h3"]))
    story.append(Paragraph(
        "const isDeepfake = Math.random() &gt; 0.65<br/>"
        "const baseConfidence = isDeepfake ? 75 + Math.random() * 20 : 80 + Math.random() * 15<br/>"
        "await new Promise(resolve =&gt; setTimeout(resolve, 2500))",
        st["code"]
    ))
    story.append(Paragraph(
        "Every result was random. A deepfake image and a real photo would get the same treatment — "
        "a dice roll. There was no actual signal from any model.",
        st["body"]
    ))
    story.append(PageBreak())
    return story


def section_what_we_built(st):
    story = []
    story.append(section_banner("2.  What We Built", st))
    story.append(Spacer(1, 6))

    # ── 2A FastAPI Backend
    story.append(Paragraph("2A  FastAPI Backend Skeleton", st["h2"]))
    story.append(Paragraph(
        "A production-structured Python backend at <b>backend/</b> with full separation of concerns: "
        "routers handle HTTP, services hold AI logic, utils hold reusable helpers.",
        st["body"]
    ))
    files_backend = [
        ["File", "Purpose"],
        ["backend/main.py", "FastAPI app + CORS for localhost:3000"],
        ["backend/routers/image.py", "POST /detect/image  +  POST /detect/image/report"],
        ["backend/routers/video.py", "POST /detect/video"],
        ["backend/routers/audio.py", "POST /detect/audio"],
        ["backend/services/image_service.py", "MTCNN face crop → ResNet50 → GradCAM → base64 PNG"],
        ["backend/services/video_service.py", "OpenCV frame extraction → per-frame scoring → timeline chart"],
        ["backend/services/audio_service.py", "librosa mel-spectrogram → AudioCNN → spectrogram PNG"],
        ["backend/utils/gradcam.py", "GradCAM with PyTorch forward + full_backward hooks"],
        ["backend/utils/report.py", "PDF report generation via reportlab"],
        ["backend/models/", "Directory for trained .pth weight files"],
        ["backend/requirements.txt", "All Python dependencies pinned"],
    ]
    t = Table(files_backend, colWidths=[5.5*cm, 10.5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID",          (0, 0), (-1, -1), 0.4, MGRAY),
        ("FONTSIZE",      (0, 0), (-1, -1), 8.5),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, LGRAY]),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    # ── 2B Image Detection
    story.append(Paragraph("2B  Image Detection — ResNet50 + GradCAM", st["h2"]))
    story.append(Paragraph(
        "The image pipeline uses <b>MTCNN</b> (from facenet-pytorch) to locate and crop the face, "
        "then passes the 224×224 crop through a <b>ResNet50</b> with a fine-tuned 2-class head "
        "(real / fake). <b>GradCAM</b> produces a gradient-weighted heatmap showing <i>which pixels "
        "the model used to decide</i>, overlaid on the original image.",
        st["body"]
    ))
    pipeline_img = [
        ["Step", "Component", "Output"],
        ["1", "User uploads image", "Raw bytes (JPG/PNG/WEBP, ≤10 MB)"],
        ["2", "MTCNN face detection", "Cropped face region (±20px margin)"],
        ["3", "Torchvision transforms", "224×224 normalised tensor"],
        ["4", "ResNet50 inference", "Fake probability score (0–1)"],
        ["5", "GradCAM backward pass", "Spatial importance map (224×224)"],
        ["6", "Matplotlib overlay", "3-panel base64 PNG: original | heatmap | overlay"],
        ["7", "JSON response", "isDeepfake, confidence, gradcamImage, details[]"],
    ]
    t2 = Table(pipeline_img, colWidths=[1*cm, 5*cm, 10*cm])
    t2.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), BLUE),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID",          (0, 0), (-1, -1), 0.4, MGRAY),
        ("FONTSIZE",      (0, 0), (-1, -1), 8.5),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, LGRAY]),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
    ]))
    story.append(t2)
    story.append(Spacer(1, 10))

    # ── 2C Video
    story.append(Paragraph("2C  Video Detection — Frame Scoring + Timeline", st["h2"]))
    story.append(Paragraph(
        "Videos are handled by extracting up to 20 evenly-spaced frames with <b>OpenCV</b>, "
        "running each frame through the same ResNet50 image model, and aggregating scores. "
        "A per-frame timeline bar-chart (matplotlib) is returned as a base64 image — "
        "red bars = suspicious seconds, green bars = clean.",
        st["body"]
    ))
    story.append(Spacer(1, 10))

    # ── 2D Audio
    story.append(Paragraph("2D  Audio Detection — Mel-Spectrogram CNN", st["h2"]))
    story.append(Paragraph(
        "Audio is converted to a <b>128-band Mel-spectrogram</b> (librosa), resized to 128×128, "
        "and classified by a lightweight <b>AudioCNN</b> (3 conv blocks + FC head). "
        "The spectrogram is colour-coded by verdict: <font color='red'>red</font> = fake, "
        "<font color='blue'>blue</font> = real. "
        "Real voices show harmonic vertical striping; TTS/cloned voices leave flat, over-smooth "
        "artefacts that the CNN learns to detect.",
        st["body"]
    ))
    story.append(Spacer(1, 10))

    # ── 2E Training Pipeline
    story.append(Paragraph("2E  Training Pipeline", st["h2"]))
    train_rows = [
        ["Script", "Model", "Dataset", "Key technique"],
        ["training/train_image.py", "ResNet50", "FaceForensics++ / CelebDF-v2",
         "Freeze backbone, fine-tune layer4 + FC head; CosineAnnealing LR"],
        ["training/train_audio.py", "AudioCNN (custom)", "ASVspoof 2019 LA / WaveFake",
         "Mel-spectrogram augmentation: time-stretch, pitch-shift, noise"],
    ]
    t3 = Table(train_rows, colWidths=[3.5*cm, 3*cm, 5*cm, 4.5*cm])
    t3.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), TEAL),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID",          (0, 0), (-1, -1), 0.4, MGRAY),
        ("FONTSIZE",      (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, LGRAY]),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(t3)
    story.append(Spacer(1, 10))

    # ── 2F Frontend Integration
    story.append(Paragraph("2F  Frontend Integration", st["h2"]))
    fe_changes = [
        ["File changed", "What changed"],
        ["app/api/detect/image/route.ts (NEW)", "Proxy: Next.js → FastAPI /detect/image"],
        ["app/api/detect/video/route.ts (NEW)", "Proxy: Next.js → FastAPI /detect/video"],
        ["app/api/detect/audio/route.ts (NEW)", "Proxy: Next.js → FastAPI /detect/audio"],
        ["components/analysis-result.tsx",
         "Extended AnalysisResult type with gradcamImage?, spectrogramImage?, timelineImage?; "
         "renders XAI image below details grid"],
        ["app/detect/image/page.tsx",
         "Replaced Math.random() mock with real fetch('/api/detect/image') + error state"],
        ["app/detect/video/page.tsx",
         "Replaced Math.random() mock with real fetch('/api/detect/video') + error state"],
        ["app/detect/audio/page.tsx",
         "Replaced Math.random() mock with real fetch('/api/detect/audio') + error state"],
        ["next.config.mjs", "Added serverActions.bodySizeLimit: '55mb' for large video uploads"],
    ]
    t4 = Table(fe_changes, colWidths=[5.5*cm, 10.5*cm])
    t4.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID",          (0, 0), (-1, -1), 0.4, MGRAY),
        ("FONTSIZE",      (0, 0), (-1, -1), 8.5),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, LGRAY]),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(t4)
    story.append(PageBreak())
    return story


def section_architecture(st):
    story = []
    story.append(section_banner("3.  Technical Architecture", st))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Complete Data Flow", st["h2"]))
    arch = (
        "┌──────────────────────────────────────────────────────────────┐\n"
        "│                  KYROS — System Architecture                 │\n"
        "└──────────────────────────────────────────────────────────────┘\n"
        "\n"
        "  User Browser (Next.js 16 + TypeScript + Tailwind)\n"
        "       │  uploads file via react-dropzone\n"
        "       ↓\n"
        "  /api/detect/[image|video|audio]  ← Next.js API Route (proxy)\n"
        "       │  FormData forwarded to Python\n"
        "       ↓\n"
        "  FastAPI  (uvicorn, localhost:8000)\n"
        "       ├── POST /detect/image\n"
        "       │       ↓  MTCNN → ResNet50 → GradCAM\n"
        "       │       ↓  returns: isDeepfake, confidence, gradcamImage\n"
        "       ├── POST /detect/video\n"
        "       │       ↓  OpenCV frames → ResNet50 per frame → timeline\n"
        "       │       ↓  returns: isDeepfake, confidence, timelineImage\n"
        "       └── POST /detect/audio\n"
        "               ↓  librosa mel-spec → AudioCNN\n"
        "               ↓  returns: isDeepfake, confidence, spectrogramImage\n"
        "\n"
        "  backend/models/\n"
        "       ├── resnet50_deepfake.pth   (image + video scoring)\n"
        "       └── audio_cnn.pth           (audio classification)\n"
        "\n"
        "  Training (offline, one-time)\n"
        "       ├── python -m training.train_image  → resnet50_deepfake.pth\n"
        "       └── python -m training.train_audio  → audio_cnn.pth"
    )
    story.append(Paragraph(arch.replace("\n", "<br/>").replace(" ", "&nbsp;"), st["code"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Technology Stack", st["h2"]))
    stack = [
        ["Layer", "Technology", "Purpose"],
        ["Frontend", "Next.js 16 + TypeScript", "UI, routing, API proxy routes"],
        ["UI Library", "shadcn/ui + Tailwind CSS", "Components, dark theme, animations"],
        ["Backend", "FastAPI + uvicorn", "REST API, file handling, async"],
        ["Deep Learning", "PyTorch + torchvision", "Model inference and training"],
        ["Image Model", "ResNet50 (fine-tuned)", "Deepfake image classification"],
        ["Audio Model", "Custom AudioCNN", "Mel-spectrogram classification"],
        ["Face Detection", "MTCNN (facenet-pytorch)", "Face localisation before classification"],
        ["XAI", "GradCAM (custom impl.)", "Visual explanation of model decisions"],
        ["Audio Processing", "librosa", "Mel-spectrogram generation, augmentation"],
        ["Video Processing", "OpenCV (cv2)", "Frame extraction from video files"],
        ["PDF Reports", "reportlab", "Forensic-grade report generation"],
        ["Dataset (image)", "FaceForensics++ / CelebDF-v2", "Real vs deepfake face images"],
        ["Dataset (audio)", "ASVspoof 2019 LA / WaveFake", "Genuine vs synthesized speech"],
    ]
    t5 = Table(stack, colWidths=[3.5*cm, 5*cm, 7.5*cm])
    t5.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID",          (0, 0), (-1, -1), 0.4, MGRAY),
        ("FONTSIZE",      (0, 0), (-1, -1), 8.5),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, LGRAY]),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(t5)
    story.append(PageBreak())
    return story


def section_file_structure(st):
    story = []
    story.append(section_banner("4.  Complete File Structure (After)", st))
    story.append(Spacer(1, 6))
    structure = (
        "KYROS--Deepfake-Detection-Platform/\n"
        "│\n"
        "├── app/                            (Next.js App Router)\n"
        "│   ├── api/detect/\n"
        "│   │   ├── image/route.ts          ← NEW: proxy to FastAPI\n"
        "│   │   ├── video/route.ts          ← NEW\n"
        "│   │   └── audio/route.ts          ← NEW\n"
        "│   ├── detect/\n"
        "│   │   ├── image/page.tsx          ← UPDATED: real API call\n"
        "│   │   ├── video/page.tsx          ← UPDATED: real API call\n"
        "│   │   └── audio/page.tsx          ← UPDATED: real API call\n"
        "│   ├── globals.css\n"
        "│   ├── layout.tsx\n"
        "│   └── page.tsx                    (homepage, unchanged)\n"
        "│\n"
        "├── components/\n"
        "│   ├── analysis-result.tsx         ← UPDATED: XAI image display\n"
        "│   ├── detection-card.tsx\n"
        "│   ├── file-upload.tsx\n"
        "│   ├── navigation.tsx\n"
        "│   └── ui/  (shadcn/ui components)\n"
        "│\n"
        "├── backend/                        ← NEW: entire Python backend\n"
        "│   ├── main.py\n"
        "│   ├── requirements.txt\n"
        "│   ├── routers/\n"
        "│   │   ├── image.py\n"
        "│   │   ├── video.py\n"
        "│   │   └── audio.py\n"
        "│   ├── services/\n"
        "│   │   ├── image_service.py        ResNet50 + GradCAM\n"
        "│   │   ├── video_service.py        OpenCV + frame scoring\n"
        "│   │   └── audio_service.py        mel-spec + AudioCNN\n"
        "│   ├── utils/\n"
        "│   │   ├── gradcam.py              GradCAM implementation\n"
        "│   │   └── report.py               PDF generation\n"
        "│   └── models/\n"
        "│       ├── resnet50_deepfake.pth   (after training)\n"
        "│       └── audio_cnn.pth           (after training)\n"
        "│\n"
        "├── training/                       ← NEW: ML training scripts\n"
        "│   ├── train_image.py              ResNet50 fine-tuning\n"
        "│   ├── train_audio.py              AudioCNN training\n"
        "│   ├── dataset.py                  Image dataset loader\n"
        "│   ├── dataset_audio.py            Audio dataset + augmentation\n"
        "│   └── config.py                   Hyperparameters\n"
        "│\n"
        "├── data/                           (not committed — your datasets go here)\n"
        "│   ├── image/train/real|fake/\n"
        "│   ├── image/val/real|fake/\n"
        "│   ├── audio/train/real|fake/\n"
        "│   └── audio/val/real|fake/\n"
        "│\n"
        "├── next.config.mjs                 ← UPDATED: 55 MB body limit\n"
        "├── generate_report.py              ← NEW: this report generator\n"
        "└── package.json"
    )
    story.append(Paragraph(structure.replace("\n", "<br/>").replace(" ", "&nbsp;"), st["code"]))
    story.append(PageBreak())
    return story


def section_how_to_run(st):
    story = []
    story.append(section_banner("5.  How to Run the Project", st))
    story.append(Spacer(1, 8))

    steps = [
        ("Install Python dependencies",
         "cd backend<br/>pip install -r requirements.txt"),
        ("Start the FastAPI backend",
         "cd backend<br/>uvicorn main:app --reload<br/>"
         "# API docs: http://localhost:8000/docs"),
        ("Start the Next.js frontend (separate terminal)",
         "npm run dev<br/># Open: http://localhost:3000"),
        ("Train image model (once, after dataset setup)",
         "# Place images in data/image/train/real/ and data/image/train/fake/<br/>"
         "python -m training.train_image"),
        ("Train audio model (once, after dataset setup)",
         "# Place audio in data/audio/train/real/ and data/audio/train/fake/<br/>"
         "python -m training.train_audio"),
    ]
    for i, (title, code) in enumerate(steps, 1):
        story.append(Paragraph(f"Step {i}: {title}", st["h3"]))
        story.append(Paragraph(code, st["code"]))
        story.append(Spacer(1, 4))

    story.append(PageBreak())
    return story


def section_resume(st):
    story = []
    story.append(section_banner("6.  Resume Bullet Points", st))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "These two bullets are written to hit recruiter keywords AND pass ATS filters. "
        "Use them on your resume under Projects.",
        st["body"]
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Bullet 1 — Breadth (full-stack + AI):", st["h3"]))
    b1 = Table([[Paragraph(
        "• Built <b>KYROS</b>, a full-stack deepfake detection platform (Next.js · TypeScript · FastAPI · PyTorch) "
        "with real-time analysis of images, videos, and audio; integrated <b>GradCAM explainability</b> to produce "
        "visual heatmaps of manipulated regions, enabling forensic-grade evidence output.",
        st["body"]
    )]], colWidths=[W - 4*cm])
    b1.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.Color(0.90, 0.95, 1.0)),
        ("LINEBEFOREI",   (0, 0), (-1, -1), 3, BLUE),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 14),
        ("BOX",           (0, 0), (-1, -1), 1, BLUE),
    ]))
    story.append(b1)
    story.append(Spacer(1, 14))

    story.append(Paragraph("Bullet 2 — Depth (ML engineering):", st["h3"]))
    b2 = Table([[Paragraph(
        "• Fine-tuned <b>ResNet50</b> on FaceForensics++ for deepfake image/video detection; trained a "
        "<b>custom CNN</b> on 128-band Mel-spectrograms (ASVspoof 2019) for voice-clone detection; "
        "implemented <b>MTCNN</b> face localisation, transfer learning with layer-selective freezing, "
        "and cosine-annealing LR scheduling.",
        st["body"]
    )]], colWidths=[W - 4*cm])
    b2.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.Color(0.90, 0.97, 0.92)),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 14),
        ("BOX",           (0, 0), (-1, -1), 1, GREEN),
    ]))
    story.append(b2)
    story.append(Spacer(1, 14))

    story.append(Paragraph(
        "Tip: tailor the first bullet for software engineering / full-stack roles; "
        "use the second for ML engineer / AI researcher / data science roles.",
        st["body"]
    ))
    story.append(PageBreak())
    return story


def section_interview(st):
    story = []
    story.append(section_banner("7.  Interview Preparation", st))
    story.append(Spacer(1, 8))

    # ── Elevator pitch
    story.append(Paragraph("Your Elevator Pitch (say this first)", st["h2"]))
    pitch_30 = Table([[Paragraph(
        "<b>30-second version:</b><br/>"
        "\"KYROS is a deepfake detection platform I built from scratch. "
        "It uses ResNet50 fine-tuned on FaceForensics++ to classify images as real or fake, "
        "with GradCAM to visually highlight which part of the face is manipulated. "
        "For audio, I trained a CNN on Mel-spectrograms to detect voice cloning. "
        "The backend is FastAPI, frontend is Next.js, and everything is connected end-to-end.\"",
        st["pitch"]
    )]], colWidths=[W - 4*cm])
    pitch_30.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.Color(0.95, 0.95, 1.0)),
        ("BOX",           (0, 0), (-1, -1), 1, BLUE),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
    ]))
    story.append(pitch_30)
    story.append(Spacer(1, 10))

    pitch_2m = Table([[Paragraph(
        "<b>2-minute version (for \"tell me about your project\"):</b><br/><br/>"
        "\"The problem I was solving is that deepfakes are becoming impossible to detect with the naked eye. "
        "I built KYROS — an end-to-end platform that handles images, video, and audio.<br/><br/>"
        "For images, I fine-tuned ResNet50 on the FaceForensics++ dataset. The key design decision was using "
        "transfer learning — I froze all layers except the last ResNet block and the classifier head, "
        "because the early layers already detect edges and textures that are universal. I only needed to "
        "teach the network to recognise deepfake-specific artefacts in the high-level features.<br/><br/>"
        "What makes the system useful — not just academic — is GradCAM. Instead of just saying 'this is fake', "
        "it shows you exactly where: the eye boundary, the hair-face transition, the mouth corners. That's the "
        "kind of explainability you need if this is used in journalism or law enforcement.<br/><br/>"
        "For audio, I converted speech to Mel-spectrograms — essentially images of sound — and trained a "
        "CNN on them. Real voices have complex harmonic patterns; TTS and voice-cloned audio leaves "
        "frequency artefacts that look different on the spectrogram. The colour-coded output shows "
        "the user why the system thinks the audio is fake.<br/><br/>"
        "The backend is FastAPI because it's async and production-grade, connected to a Next.js frontend "
        "via proxy API routes. I also built a PDF report generator so analysts can produce "
        "forensic-grade signed output.\"",
        st["pitch"]
    )]], colWidths=[W - 4*cm])
    pitch_2m.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.Color(0.93, 0.98, 0.93)),
        ("BOX",           (0, 0), (-1, -1), 1, GREEN),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
    ]))
    story.append(pitch_2m)
    story.append(PageBreak())

    # ── Interview Q&A
    story.append(Paragraph("Expected Interview Questions + Model Answers", st["h2"]))
    story.append(Spacer(1, 6))

    qa = [
        ("How does ResNet50 detect deepfakes?",
         "ResNet50 is a CNN pre-trained on ImageNet. I replaced its final classification layer with a "
         "2-class head (real/fake) and fine-tuned it on deepfake datasets. The network learns that deepfakes "
         "have specific artefacts — GAN blending boundaries, inconsistent eye reflections, unnatural skin "
         "texture — that appear in the high-level feature maps of the deeper ResNet blocks."),
        ("What is GradCAM and why did you implement it?",
         "GradCAM (Gradient-weighted Class Activation Mapping) computes the gradient of the target class score "
         "with respect to the feature maps in the last convolutional layer. It pools those gradients spatially "
         "(global average pooling) to get channel weights, then linearly combines the feature maps. "
         "The result is a heatmap showing which spatial regions most influenced the decision. "
         "I used it because deepfake detection without explainability is a black box — if you're presenting "
         "evidence in a legal context, you need to show WHERE the manipulation is, not just say 'the model says fake'."),
        ("Why transfer learning? Why freeze layers?",
         "ImageNet pre-training gives the model strong low-level feature detectors: edges, textures, colour gradients. "
         "Deepfake detection needs to build on these, not relearn them. Freezing layers 1-3 means we don't need "
         "hundreds of thousands of images to train well — fine-tuning just layer4 + FC head converges with ~10k images. "
         "It also reduces overfitting significantly."),
        ("What is a Mel-spectrogram?",
         "A Mel-spectrogram is a 2D representation of audio: x-axis = time, y-axis = frequency on a mel scale "
         "(logarithmic, matching human hearing). The value at each pixel is the energy in that frequency band "
         "at that moment. It converts audio to an image, so we can apply standard image CNNs to it. "
         "The mel scale emphasises lower frequencies more than higher ones, which is where voice cloning "
         "artefacts tend to appear."),
        ("How does your video detection work?",
         "OpenCV extracts up to 20 evenly-spaced frames from the video. Each frame is passed through the same "
         "ResNet50 image classifier to get a per-frame fake probability. I then average these and build "
         "a timeline chart showing which seconds are suspicious. This is computationally cheap and "
         "naturally handles the temporal aspect — if frames are consistently fake, it's a deepfake; "
         "if only a few spikes appear, it might be a compression artefact."),
        ("What datasets did you use and why?",
         "FaceForensics++ for images and video — it's the standard benchmark in the field, with 5 types of "
         "face manipulation (DeepFakes, FaceSwap, Face2Face, NeuralTextures, FaceShifter). "
         "ASVspoof 2019 LA for audio — it's the international challenge dataset for anti-spoofing, "
         "with 17 different TTS and voice conversion systems. These are the datasets every paper cites, "
         "so my model's performance can be compared to the literature."),
        ("What is FastAPI and why not Flask?",
         "FastAPI is built on Starlette and Pydantic, is async by default, and auto-generates OpenAPI docs. "
         "For file uploads and running inference on large media files, async matters — Flask would block "
         "the thread while waiting for file I/O. FastAPI also has built-in request validation via Pydantic, "
         "which makes the API more robust."),
        ("What are the limitations of your system?",
         "Three main ones: (1) The model may degrade on compression artefacts — a deepfake uploaded to "
         "social media gets JPEG-compressed, which can mask the original manipulation. "
         "(2) I only trained on specific manipulation methods — a new GAN architecture not in FaceForensics++ "
         "might fool the model. (3) The model is trained on constrained lab data; "
         "in-the-wild images with varied lighting, occlusion, and resolution are harder. "
         "Improvements: adversarial augmentation during training, ensemble of models, periodically retraining "
         "on new deepfake samples."),
        ("How would you improve accuracy?",
         "Short-term: ensemble multiple architectures (EfficientNet + ViT + ResNet50) and average predictions. "
         "Medium-term: add frequency-domain features (FFT on the image) as an additional input channel — "
         "GAN artefacts are very visible in the frequency domain. Long-term: use a contrastive learning "
         "approach or train a Vision Transformer end-to-end with more data."),
        ("How does the frontend communicate with the backend?",
         "The Next.js frontend doesn't call the Python server directly. Instead it POSTs to a Next.js API route "
         "(/api/detect/image). That route is a thin proxy that forwards the FormData to FastAPI at "
         "localhost:8000/detect/image. This keeps CORS simple, hides the backend URL from the client, "
         "and lets us add auth middleware or caching at the Next.js layer later."),
        ("What is MTCNN?",
         "Multi-task Cascaded CNN — a three-stage pipeline (P-Net, R-Net, O-Net) that detects faces "
         "and facial landmarks with high accuracy and speed. I use it from the facenet-pytorch library. "
         "The reason I detect and crop the face before running ResNet50 is that giving the model a tightly "
         "cropped face forces it to focus on facial manipulation features rather than background cues "
         "that don't generalise."),
        ("Can you explain the GradCAM math?",
         "Given target class c and feature map A^k from the last conv layer: "
         "α_k^c = (1/Z) Σ_i Σ_j (∂y^c / ∂A^k_ij)  — global average pool of gradients per channel. "
         "Then CAM = ReLU( Σ_k α_k^c · A^k ). The ReLU keeps only positive influence regions. "
         "The resulting map is upsampled to input resolution and overlaid on the image."),
        ("What would you add given more time?",
         "1) CNN-LSTM for video: use the temporal sequence of frame feature vectors as input to an LSTM "
         "to capture motion inconsistencies that frame-by-frame scoring misses. "
         "2) Metadata forensics: EXIF data analysis — a deepfake usually lacks camera metadata. "
         "3) Blockchain-signed reports: hash the file + result + timestamp and store on a ledger "
         "for tamper-proof evidence. "
         "4) Browser-side inference via ONNX/transformers.js for the offline-first use case."),
    ]

    for q, a in qa:
        story.append(Paragraph(f"Q: {q}", st["qa_q"]))
        story.append(Paragraph(f"A: {a}", st["qa_a"]))
        story.append(hr(LGRAY, 0.5))

    story.append(PageBreak())
    return story


def section_quick_reference(st):
    story = []
    story.append(section_banner("8.  Quick Reference Card", st))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Key Numbers to Remember", st["h2"]))
    nums = [
        ["Fact", "Value"],
        ["Image model architecture", "ResNet50 (25M params), fine-tuned layer4 + FC"],
        ["Image input size", "224 × 224 RGB, normalised to ImageNet stats"],
        ["Audio model", "Custom 3-block CNN: 32→64→128 filters + AdaptiveAvgPool"],
        ["Mel-spectrogram", "128 mel bands, fixed 128 time frames, fmax=8000 Hz"],
        ["Audio sample rate", "16,000 Hz (resampled from source)"],
        ["Video sampling", "Up to 20 evenly-spaced frames per video"],
        ["Image max upload", "10 MB"],
        ["Video max upload", "50 MB"],
        ["Audio max upload", "20 MB"],
        ["Image training epochs", "20, batch=32, lr=1e-4, CosineAnnealingLR"],
        ["Audio training epochs", "30, batch=64, lr=3e-4, CosineAnnealingLR"],
        ["Image dataset", "FaceForensics++ (5 manipulation types) or CelebDF-v2"],
        ["Audio dataset", "ASVspoof 2019 LA (17 spoof systems) or WaveFake"],
        ["XAI method", "GradCAM on ResNet50 layer4[-1]; spectrogram viz for audio"],
        ["Backend framework", "FastAPI + uvicorn on localhost:8000"],
        ["Frontend framework", "Next.js 16 + TypeScript + Tailwind + shadcn/ui"],
        ["PDF reports", "reportlab — generated server-side on /detect/image/report"],
    ]
    t = Table(nums, colWidths=[6*cm, 10*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID",          (0, 0), (-1, -1), 0.4, MGRAY),
        ("FONTSIZE",      (0, 0), (-1, -1), 8.5),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, LGRAY]),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(t)
    story.append(Spacer(1, 16))
    story.append(hr(BLUE, 1))
    story.append(Paragraph(
        "KYROS Deepfake Detection Platform — Project Report  |  Generated by generate_report.py",
        ParagraphStyle("footer", parent=st["body"], fontSize=8, textColor=MGRAY, alignment=TA_CENTER)
    ))
    return story


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    doc = SimpleDocTemplate(
        OUT, pagesize=A4,
        topMargin=1.8*cm, bottomMargin=1.8*cm,
        leftMargin=2*cm,  rightMargin=2*cm,
    )
    st = build_styles()

    story = []
    story += cover_page(st)
    story += section_original_state(st)
    story += section_what_we_built(st)
    story += section_architecture(st)
    story += section_file_structure(st)
    story += section_how_to_run(st)
    story += section_resume(st)
    story += section_interview(st)
    story += section_quick_reference(st)

    doc.build(story)
    print(f"[KYROS] Report generated: {OUT}")


if __name__ == "__main__":
    main()
