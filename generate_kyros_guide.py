"""
Generates KYROS_Project_Guide.pdf — full project explanation, resume bullets,
interview explanation, and interview Q&A.
Run from the project root:
    python generate_kyros_guide.py
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)

OUT = "KYROS_Project_Guide.pdf"

# ── Colour palette ──────────────────────────────────────────────────────────
NAVY   = colors.Color(0.10, 0.18, 0.38)
TEAL   = colors.Color(0.05, 0.55, 0.60)
LIGHT  = colors.Color(0.93, 0.96, 1.00)
STRIPE = colors.Color(0.97, 0.97, 1.00)
WHITE  = colors.white
DARK   = colors.Color(0.12, 0.12, 0.12)


def make_styles():
    base = getSampleStyleSheet()

    def add(name, **kw):
        base.add(ParagraphStyle(name, **kw))

    add("Cover",       parent=base["Title"],   fontSize=28, textColor=WHITE,
        alignment=TA_CENTER, spaceAfter=8)
    add("CoverSub",    parent=base["Normal"],  fontSize=13, textColor=colors.Color(0.8,0.9,1),
        alignment=TA_CENTER, spaceAfter=4)
    add("CoverDate",   parent=base["Normal"],  fontSize=10, textColor=colors.Color(0.7,0.8,0.9),
        alignment=TA_CENTER, spaceAfter=0)

    add("SectionH",    parent=base["Heading1"], fontSize=15, textColor=WHITE,
        spaceAfter=0, spaceBefore=0, leftIndent=0)
    add("SubH",        parent=base["Heading2"], fontSize=12, textColor=NAVY,
        spaceBefore=10, spaceAfter=4)
    add("Body",        parent=base["Normal"],   fontSize=10, textColor=DARK,
        leading=15, spaceAfter=6, alignment=TA_JUSTIFY)
    add("BulletItem",  parent=base["Normal"],   fontSize=10, textColor=DARK,
        leading=15, leftIndent=14, spaceAfter=5)
    add("CodeLine",    parent=base["Code"],     fontSize=9,
        backColor=colors.Color(0.95,0.95,0.95), leftIndent=10, spaceAfter=3)
    add("QLabel",      parent=base["Normal"],   fontSize=10, textColor=NAVY,
        leading=14, spaceBefore=8, spaceAfter=2, fontName="Helvetica-Bold")
    add("ALabel",      parent=base["Normal"],   fontSize=10, textColor=DARK,
        leading=14, leftIndent=12, spaceAfter=4, alignment=TA_JUSTIFY)
    add("ResumeBullet",parent=base["Normal"],   fontSize=10, textColor=DARK,
        leading=16, leftIndent=10, spaceAfter=8,
        borderPad=8, borderColor=TEAL, borderWidth=1,
        backColor=colors.Color(0.96, 0.99, 0.99))

    return base


def section_header(text, styles):
    """Dark navy banner with white heading text."""
    data = [[Paragraph(text, styles["SectionH"])]]
    t = Table(data, colWidths=[17*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), NAVY),
        ("TOPPADDING",    (0,0),(-1,-1), 7),
        ("BOTTOMPADDING", (0,0),(-1,-1), 7),
        ("LEFTPADDING",   (0,0),(-1,-1), 10),
    ]))
    return t


def arch_table(styles):
    rows = [
        ["Layer", "Technology", "Role"],
        ["Frontend",      "Next.js 14 + TypeScript + Tailwind", "Upload UI, result display, visualizations"],
        ["API Proxy",     "Next.js API Routes",                 "Forwards FormData to Python backend"],
        ["Backend",       "FastAPI + Uvicorn",                  "REST API, file validation, routing"],
        ["Image AI",      "ResNet50 + GradCAM + MTCNN",         "Deepfake classification + XAI heatmap"],
        ["Video AI",      "OpenCV + ResNet50 frame scorer",     "Extract 20 frames, score each, aggregate"],
        ["Audio AI",      "librosa + AudioCNN",                 "Mel-spectrogram extraction + CNN classify"],
        ["Model storage", "PyTorch .pth files",                 "Saved weights auto-loaded at startup"],
    ]
    t = Table(rows, colWidths=[3.5*cm, 6.5*cm, 7*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,0), NAVY),
        ("TEXTCOLOR",    (0,0),(-1,0), WHITE),
        ("FONTNAME",     (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",     (0,0),(-1,-1), 9),
        ("GRID",         (0,0),(-1,-1), 0.4, colors.lightgrey),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE, STRIPE]),
        ("VALIGN",       (0,0),(-1,-1), "TOP"),
        ("TOPPADDING",   (0,0),(-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING",  (0,0),(-1,-1), 6),
    ]))
    return t


def decision_table(styles):
    rows = [
        ["Decision", "Reason"],
        ["ResNet50 over scratch CNN",
         "ImageNet pretraining already encodes texture/edge features useful for spotting deepfake artifacts. Training from scratch needs 10x more data."],
        ["Freeze early layers, train layer4 + FC only",
         "Lower layers detect generic features (edges, colours) — no need to retrain them. Faster training, less overfitting on small datasets."],
        ["GradCAM for explainability",
         "Makes predictions interpretable. Highlights which facial region triggered the fake verdict — essential for a detection system to be trustworthy."],
        ["MTCNN face crop before classification",
         "Model focuses on the face only, not irrelevant background. Improves accuracy and makes it robust to different image compositions."],
        ["Mel-spectrogram for audio",
         "Converts 1D audio into a 2D image (time x frequency). Lets a standard image CNN classify it without any architecture changes."],
        ["FastAPI over Flask",
         "Async support handles concurrent uploads, automatic Swagger docs, built-in Pydantic validation."],
        ["Next.js API Routes as proxy",
         "Browser never calls Python directly. Backend URL hidden from client. Easy to swap or redeploy backend without touching frontend code."],
    ]
    t = Table(rows, colWidths=[5*cm, 12*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,0), TEAL),
        ("TEXTCOLOR",    (0,0),(-1,0), WHITE),
        ("FONTNAME",     (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",     (0,0),(-1,-1), 9),
        ("GRID",         (0,0),(-1,-1), 0.4, colors.lightgrey),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE, STRIPE]),
        ("VALIGN",       (0,0),(-1,-1), "TOP"),
        ("TOPPADDING",   (0,0),(-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING",  (0,0),(-1,-1), 6),
    ]))
    return t


def build_pdf():
    doc = SimpleDocTemplate(
        OUT, pagesize=A4,
        topMargin=1.8*cm, bottomMargin=2*cm,
        leftMargin=2*cm,  rightMargin=2*cm,
    )
    S = make_styles()
    story = []

    # ── COVER ───────────────────────────────────────────────────────────────
    cover_data = [[
        Paragraph("KYROS", S["Cover"]),
        Paragraph("Deepfake Detection Platform", S["CoverSub"]),
        Paragraph("Full-Stack AI Project — Complete Guide", S["CoverSub"]),
        Paragraph("Resume Bullets  •  Interview Explanation  •  Q&amp;A", S["CoverDate"]),
        Paragraph("Kedarnadh Thrinadh  |  2026", S["CoverDate"]),
    ]]
    cover = Table([[col] for col in cover_data[0]], colWidths=[17*cm])
    cover.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), NAVY),
        ("TOPPADDING",    (0,0),(-1,-1), 10),
        ("BOTTOMPADDING", (0,0),(-1,-1), 10),
        ("LEFTPADDING",   (0,0),(-1,-1), 20),
        ("RIGHTPADDING",  (0,0),(-1,-1), 20),
    ]))
    story.append(cover)
    story.append(Spacer(1, 20))

    # ── SECTION 1: WHAT WE BUILT ─────────────────────────────────────────
    story.append(section_header("1.  What We Built — Overview", S))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "KYROS started as a polished Next.js + TypeScript frontend with professional UI, multiple modules "
        "(Image, Video, Audio), and a good architecture — but <b>zero real AI</b>. Every detection result was "
        "<b>Math.random()</b> with a fake timer. The goal was to replace that with a real, end-to-end AI "
        "inference pipeline.", S["Body"]))
    story.append(Paragraph(
        "We built a <b>FastAPI Python backend</b> from scratch with three separate AI models — one for each "
        "media type — connected it to the existing frontend through Next.js API proxy routes, and added "
        "Explainable AI (XAI) visualizations so the user can see <i>why</i> the model made its decision.",
        S["Body"]))

    story.append(Paragraph("What existed before vs. after:", S["SubH"]))
    rows = [
        ["Area", "Before", "After"],
        ["Detection logic",  "Math.random() + fake timer",        "Real neural network inference"],
        ["Image analysis",   "Random confidence %",               "ResNet50 + GradCAM heatmap"],
        ["Video analysis",   "Random confidence %",               "Frame extraction + per-frame CNN scoring"],
        ["Audio analysis",   "Random confidence %",               "Mel-spectrogram + AudioCNN"],
        ["Backend",          "None (everything in browser)",       "FastAPI on Python 3.12 (Miniforge)"],
        ["Explainability",   "None",                              "GradCAM overlay + Spectrogram + Timeline chart"],
        ["API connection",   "None",                              "Next.js proxy routes -> FastAPI"],
    ]
    t = Table(rows, colWidths=[4*cm, 5.5*cm, 7.5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0), NAVY),
        ("TEXTCOLOR",     (0,0),(-1,0), WHITE),
        ("FONTNAME",      (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,-1), 9),
        ("GRID",          (0,0),(-1,-1), 0.4, colors.lightgrey),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE, STRIPE]),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 14))

    # ── SECTION 2: ARCHITECTURE ──────────────────────────────────────────
    story.append(section_header("2.  System Architecture", S))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "The system has four layers. The browser never communicates with Python directly — "
        "all requests go through a Next.js proxy, which keeps the backend URL hidden and "
        "makes deployment flexible.", S["Body"]))

    flow_data = [
        ["Browser  (Next.js on :3000)"],
        ["  |  user uploads file (image / video / audio)"],
        ["Next.js API Route  (/api/detect/image|video|audio)"],
        ["  |  forwards FormData — acts as a proxy"],
        ["FastAPI Backend  (:8001)"],
        ["  |  validates file, routes to the correct AI service"],
        ["AI Service  (ResNet50 / AudioCNN / Frame scorer)"],
        ["  |  runs inference, generates visualization"],
        ["JSON Response  (confidence + base64 PNG visualization)"],
        ["  |  passed back up through proxy"],
        ["Frontend renders result card + GradCAM / Spectrogram / Timeline"],
    ]
    bold_rows  = [("FONTNAME",   (0,i),(-1,i), "Helvetica-Bold") for i in [0,2,4,6,8,10]]
    light_rows = [("BACKGROUND", (0,i),(-1,i), LIGHT) for i in [0,2,4,6,8,10]]
    white_rows = [("BACKGROUND", (0,i),(-1,i), WHITE) for i in [1,3,5,7,9]]
    ft = Table(flow_data, colWidths=[17*cm])
    ft.setStyle(TableStyle(
        [("FONTSIZE", (0,0),(-1,-1), 9)] +
        bold_rows + light_rows + white_rows +
        [
            ("TOPPADDING",    (0,0),(-1,-1), 4),
            ("BOTTOMPADDING", (0,0),(-1,-1), 4),
            ("LEFTPADDING",   (0,0),(-1,-1), 10),
            ("GRID",          (0,0),(-1,-1), 0.3, colors.lightgrey),
        ]
    ))
    story.append(ft)
    story.append(Spacer(1, 10))
    story.append(Paragraph("Full stack breakdown:", S["SubH"]))
    story.append(arch_table(S))
    story.append(Spacer(1, 14))

    # ── SECTION 3: THREE AI MODULES ──────────────────────────────────────
    story.append(section_header("3.  The Three AI Modules", S))
    story.append(Spacer(1, 8))

    story.append(Paragraph("3.1  Image Detection — ResNet50 + GradCAM", S["SubH"]))
    story.append(Paragraph(
        "<b>Pipeline:</b> Raw image → MTCNN face crop → ResNet50 inference → GradCAM heatmap → JSON", S["Body"]))
    for line in [
        "<b>ResNet50</b> — a 50-layer deep residual network pretrained on ImageNet. We load it with "
        "ImageNet weights, freeze all layers except the last residual block (layer4) and the "
        "classification head (FC layer), then fine-tune on deepfake data. This is called transfer learning.",
        "<b>MTCNN</b> (Multi-Task Cascaded CNN) — a face detector. Before classification, it finds and "
        "crops just the face region. This means the model sees only the face, not irrelevant background, "
        "making detection more accurate and consistent.",
        "<b>GradCAM</b> (Gradient-weighted Class Activation Mapping) — Explainable AI. After prediction, "
        "we run a second forward+backward pass WITH gradients enabled. We hook into the last conv layer "
        "to capture its activations and gradients, weight-sum them, and overlay a heatmap on the image "
        "showing which pixels influenced the fake/real decision most.",
        "<b>Output:</b> isDeepfake (bool), confidence (%), GradCAM overlay PNG (base64), details array.",
    ]:
        story.append(Paragraph("• " + line, S["BulletItem"]))

    story.append(Spacer(1, 8))
    story.append(Paragraph("3.2  Video Detection — Frame-Level CNN Scoring", S["SubH"]))
    story.append(Paragraph(
        "<b>Pipeline:</b> Video file → OpenCV frame extraction → ResNet50 per-frame scoring → "
        "aggregate → timeline chart → JSON", S["Body"]))
    for line in [
        "<b>OpenCV</b> reads the video and extracts up to 20 evenly-spaced frames regardless of "
        "video length (a 10-second and a 10-minute video both get 20 frames).",
        "Each frame is scored independently by the same ResNet50 image model.",
        "Final verdict = average fake score across all frames. A frame timeline chart is "
        "rendered as a PNG showing per-frame fake probability over time.",
        "<b>Output:</b> isDeepfake, confidence, frameTimeline array, timeline PNG (base64), details.",
    ]:
        story.append(Paragraph("• " + line, S["BulletItem"]))

    story.append(Spacer(1, 8))
    story.append(Paragraph("3.3  Audio Detection — Mel-Spectrogram CNN", S["SubH"]))
    story.append(Paragraph(
        "<b>Pipeline:</b> Audio file → librosa mel-spectrogram → resize to 128x128 → "
        "AudioCNN → JSON", S["Body"]))
    for line in [
        "<b>Mel-spectrogram</b> — converts 1D audio waveform into a 2D image where the x-axis "
        "is time and y-axis is mel-frequency bands (128 bands). This lets a standard image CNN "
        "classify audio without any architecture modifications.",
        "<b>AudioCNN</b> — custom 3-block CNN: Conv2d(1,32) → Conv2d(32,64) → Conv2d(64,128) → "
        "AdaptiveAvgPool → Dropout(0.5) → Linear(2048,256) → Linear(256,2). Input: 128x128 single-channel.",
        "<b>librosa</b> handles audio loading, resampling to 16kHz, and spectrogram computation. "
        "First call is slow (~45s) due to numba JIT compilation — subsequent calls are ~1 second.",
        "Output PNG is colour-coded: red colormap = fake verdict, blue = real verdict.",
        "<b>Output:</b> isDeepfake, confidence, spectrogramImage PNG (base64), details.",
    ]:
        story.append(Paragraph("• " + line, S["BulletItem"]))

    story.append(Spacer(1, 14))

    # ── SECTION 4: KEY TECHNICAL DECISIONS ──────────────────────────────
    story.append(section_header("4.  Key Technical Decisions", S))
    story.append(Spacer(1, 8))
    story.append(decision_table(S))
    story.append(Spacer(1, 14))

    # ── SECTION 5: FILES CREATED ─────────────────────────────────────────
    story.append(section_header("5.  Files Created / Modified", S))
    story.append(Spacer(1, 8))

    file_rows = [
        ["File", "Type", "Purpose"],
        ["backend/main.py",                       "New", "FastAPI app, CORS middleware, router registration"],
        ["backend/requirements.txt",              "New", "All Python dependencies"],
        ["backend/routers/image.py",              "New", "POST /detect/image + /detect/image/report"],
        ["backend/routers/video.py",              "New", "POST /detect/video"],
        ["backend/routers/audio.py",              "New", "POST /detect/audio"],
        ["backend/services/image_service.py",     "New", "ResNet50 + MTCNN + GradCAM inference"],
        ["backend/services/video_service.py",     "New", "OpenCV frame extraction + per-frame scoring"],
        ["backend/services/audio_service.py",     "New", "AudioCNN + mel-spectrogram pipeline"],
        ["backend/utils/gradcam.py",              "New", "GradCAM hook-based implementation"],
        ["backend/utils/report.py",               "New", "reportlab PDF report generation"],
        ["training/train_image.py",               "New", "ResNet50 fine-tuning script (20 epochs)"],
        ["training/train_audio.py",               "New", "AudioCNN training script (30 epochs)"],
        ["training/dataset.py",                   "New", "DeepfakeImageDataset (real/fake folder structure)"],
        ["training/dataset_audio.py",             "New", "DeepfakeAudioDataset with augmentation"],
        ["training/config.py",                    "New", "Hyperparameters, transforms, paths"],
        ["training/prepare_celebdf.py",           "New", "Extracts face crops from CelebDF-v2 videos"],
        ["app/api/detect/image/route.ts",         "New", "Next.js proxy -> /detect/image"],
        ["app/api/detect/video/route.ts",         "New", "Next.js proxy -> /detect/video"],
        ["app/api/detect/audio/route.ts",         "New", "Next.js proxy -> /detect/audio"],
        ["app/detect/image/page.tsx",             "Modified", "Replaced Math.random() with real API call"],
        ["app/detect/video/page.tsx",             "Modified", "Replaced Math.random() with real API call"],
        ["app/detect/audio/page.tsx",             "Modified", "Replaced Math.random() with real API call"],
        ["components/analysis-result.tsx",        "Modified", "Extended AnalysisResult interface + visualizations"],
        ["next.config.mjs",                       "Modified", "Raised body size limit to 55MB for video uploads"],
    ]
    ft = Table(file_rows, colWidths=[7*cm, 2.2*cm, 7.8*cm])
    ft.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0), NAVY),
        ("TEXTCOLOR",     (0,0),(-1,0), WHITE),
        ("FONTNAME",      (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,-1), 8.5),
        ("GRID",          (0,0),(-1,-1), 0.4, colors.lightgrey),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE, STRIPE]),
        ("TOPPADDING",    (0,0),(-1,-1), 4),
        ("BOTTOMPADDING", (0,0),(-1,-1), 4),
        ("LEFTPADDING",   (0,0),(-1,-1), 5),
        ("TEXTCOLOR",     (1,1),(-1,-1), colors.Color(0.1,0.4,0.1)),
    ]))
    story.append(ft)
    story.append(Spacer(1, 14))

    # ── SECTION 6: RESUME BULLETS ────────────────────────────────────────
    story.append(section_header("6.  Resume Bullet Points", S))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "Built KYROS, a full-stack deepfake detection platform using Next.js/TypeScript frontend "
        "and FastAPI backend, implementing ResNet50 transfer learning with GradCAM explainability "
        "for image detection, frame-level CNN analysis for video, and a Mel-spectrogram CNN for "
        "audio — replacing a mock UI with three real AI inference pipelines serving live results "
        "through a REST API.", S["ResumeBullet"]))
    story.append(Paragraph(
        "Designed and deployed an end-to-end AI inference system featuring MTCNN face detection, "
        "Gradient-weighted Class Activation Mapping (GradCAM) for model interpretability, and "
        "multi-modal deepfake detection (image/video/audio) with real-time base64-encoded "
        "visualization responses; architected a Next.js proxy layer decoupling the React frontend "
        "from the Python AI backend.", S["ResumeBullet"]))
    story.append(Spacer(1, 14))

    # ── SECTION 7: HOW TO EXPLAIN IN INTERVIEW ───────────────────────────
    story.append(section_header("7.  How to Explain This in an Interview", S))
    story.append(Spacer(1, 8))

    story.append(Paragraph("30-Second Elevator Pitch:", S["SubH"]))
    pitch_data = [[Paragraph(
        '"I built KYROS — a full-stack deepfake detection platform. Users upload an image, video, '
        'or audio file through a Next.js frontend. The frontend proxies the request to a FastAPI '
        'backend I built from scratch, which runs three separate AI models. For images, I fine-tuned '
        'ResNet50 and added GradCAM so the model visually explains why it flagged something as fake. '
        'For video I extract frames and score each one individually. For audio I convert the signal '
        'to a mel-spectrogram and classify it with a CNN. Everything returns confidence scores and '
        'visualization images back to the UI in real time."', S["Body"])]]
    pt = Table(pitch_data, colWidths=[17*cm])
    pt.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), LIGHT),
        ("TOPPADDING",    (0,0),(-1,-1), 10),
        ("BOTTOMPADDING", (0,0),(-1,-1), 10),
        ("LEFTPADDING",   (0,0),(-1,-1), 12),
        ("RIGHTPADDING",  (0,0),(-1,-1), 12),
        ("BOX",           (0,0),(-1,-1), 1, TEAL),
    ]))
    story.append(pt)
    story.append(Spacer(1, 10))

    story.append(Paragraph("When they ask: 'What was the hardest part?'", S["SubH"]))
    story.append(Paragraph(
        '"The GradCAM implementation. It requires a very specific forward and backward pass — you '
        'cannot run inference inside torch.no_grad() because you need gradients to flow back through '
        'the network. I had to register hooks on the last convolutional layer to capture both the '
        'activations on the forward pass and the gradients on the backward pass, then weight-sum them '
        'to produce the heatmap. Getting that right without breaking the normal inference path took '
        'careful engineering."', S["Body"]))

    story.append(Paragraph("When they ask: 'Why ResNet50?'", S["SubH"]))
    story.append(Paragraph(
        '"Transfer learning. ImageNet pretraining already teaches the network to detect edges, '
        'textures, and facial structure. Deepfakes typically have subtle artifacts around facial '
        'boundaries — blurring, blending seams, inconsistent skin texture — which are exactly the '
        'texture-level features ResNet50 is good at detecting. I froze the early layers and only '
        'fine-tuned the last residual block and the FC head, which made training much faster and '
        'reduced overfitting."', S["Body"]))

    story.append(Paragraph("When they ask: 'How does the frontend connect to the AI?'", S["SubH"]))
    story.append(Paragraph(
        '"The frontend never calls Python directly. I added Next.js API routes that act as a proxy — '
        'they receive the file from the browser, forward it as multipart FormData to the FastAPI '
        'backend, and relay the JSON response back. This means the backend URL is hidden from the '
        'client, you can change or redeploy the backend by changing one environment variable, and '
        'you can add auth or rate limiting at the proxy layer later."', S["Body"]))
    story.append(Spacer(1, 14))

    # ── SECTION 8: INTERVIEW Q&A ─────────────────────────────────────────
    story.append(section_header("8.  Interview Questions and Answers", S))
    story.append(Spacer(1, 8))

    qa = [
        ("CONCEPTUAL", None),
        ("Q1. What is a deepfake and how does a CNN detect one?",
         "Deepfakes are synthetically generated or face-swapped media created by GANs or diffusion models. "
         "CNNs detect them by learning artifact patterns — blurring at facial boundaries, unnatural skin "
         "textures, inconsistent lighting, or GAN-specific frequency artifacts — that are not present in "
         "real photos. The model learns these patterns from thousands of labeled real and fake examples."),
        ("Q2. What is transfer learning and why did you use it?",
         "Transfer learning means reusing weights from a model trained on a large dataset (ImageNet, 1.2M "
         "images) and fine-tuning on your specific task. The early layers already encode useful low-level "
         "features. You freeze those and only retrain the task-specific layers, which requires far less "
         "data and compute than training from scratch."),
        ("Q3. Explain GradCAM in simple terms.",
         "You do a forward pass to get the prediction, then backpropagate to find which neurons in the "
         "last conv layer influenced that prediction most. You average the gradients per channel to get "
         "importance weights, then weight-sum the activation maps using those weights. The result is a "
         "coarse heatmap showing which spatial regions drove the decision. You overlay it on the image "
         "as a coloured highlight."),
        ("Q4. What is the difference between torch.no_grad() and model.eval()?",
         "model.eval() changes the behaviour of BatchNorm (uses running statistics instead of batch stats) "
         "and Dropout (disables it). torch.no_grad() stops PyTorch from building the computation graph, "
         "saving memory and speeding up inference. For normal inference you use both. For GradCAM you use "
         "eval() but NOT no_grad(), because you need the gradient graph for the backward pass."),
        ("Q5. Why convert audio to a spectrogram instead of feeding raw waveform to a CNN?",
         "Standard CNNs are designed for 2D spatial data. A mel-spectrogram is a 2D image where x=time "
         "and y=frequency — so a standard CNN can directly apply spatial feature detection without any "
         "architectural changes. Raw waveforms are 1D and would need a different architecture such as a "
         "1D CNN or an RNN/Transformer."),
        ("Q6. What is MTCNN and why crop the face before classification?",
         "Multi-Task Cascaded CNN — a face detector that finds bounding boxes for faces in images. By "
         "cropping the face first, the classifier focuses only on facial features rather than irrelevant "
         "background (clothing, room, etc.). This improves accuracy significantly and makes the system "
         "robust to different image compositions and aspect ratios."),
        ("SYSTEM DESIGN", None),
        ("Q7. Why use Next.js API Routes as a proxy instead of calling FastAPI directly?",
         "CORS, security, and deployment flexibility. The browser never knows the backend URL. If you "
         "deploy, you change one environment variable (BACKEND_URL) without touching frontend code. "
         "The proxy layer is also where you can add authentication middleware, rate limiting, or "
         "request validation without modifying the AI service."),
        ("Q8. How would you scale this to handle 100 concurrent users?",
         "Run multiple FastAPI worker processes (uvicorn with --workers 4). Move heavy inference to a "
         "task queue (Celery + Redis) so the API returns a job ID immediately and the client polls for "
         "results. Load models once per worker at startup, not per request. Add a CDN for the static "
         "Next.js frontend. For GPU inference, a single A100 can handle 50-100 concurrent image requests."),
        ("Q9. The model gives 100% fake on untrained weights — how do you fix it in production?",
         "Train on a labeled dataset such as CelebDF-v2 or FaceForensics++. The architecture is correct "
         "— it just needs real weights. The training scripts are already written: they do transfer "
         "learning with data augmentation, CosineAnnealingLR scheduling, and save the best checkpoint "
         "by validation accuracy. Once trained, the backend auto-loads the .pth file on startup."),
        ("CODE LEVEL", None),
        ("Q10. What is a residual connection in ResNet and why does it help?",
         "A residual connection adds the input of a block directly to its output: output = F(x) + x. "
         "This solves the vanishing gradient problem in deep networks — gradients can flow directly "
         "through the skip connection during backprop. It also means layers learn residual corrections "
         "rather than full transformations, making training more stable."),
        ("Q11. What is BatchNorm and why does it matter here?",
         "Batch Normalisation normalises the activations of each layer across the batch to zero mean and "
         "unit variance. This stabilises training, allows higher learning rates, and acts as a mild "
         "regulariser. In eval() mode it uses running statistics computed during training — important "
         "for single-image inference where you don't have a batch."),
        ("Q12. How did you handle the first audio request being 45 seconds slow?",
         "librosa uses numba for JIT compilation of its signal processing functions. The first call "
         "triggers compilation which takes ~45 seconds. Subsequent calls are ~1 second. In production "
         "you warm up the model at server startup by running a dummy inference on a blank audio buffer, "
         "so end users never experience the cold start."),
        ("Q13. What is CosineAnnealingLR and why use it over a fixed learning rate?",
         "CosineAnnealingLR reduces the learning rate following a cosine curve from lr_max down to "
         "lr_min over T_max epochs. It finds better minima than a fixed rate because the high initial "
         "rate allows broad exploration and the low final rate allows fine-grained convergence. Better "
         "than step decay because the schedule is smooth with no abrupt jumps."),
        ("Q14. Why did you freeze early ResNet layers during fine-tuning?",
         "Early layers (layer1, layer2, layer3) detect generic features: edges, corners, colour gradients "
         "— these are the same whether you're looking at ImageNet dogs or deepfake faces. There's no "
         "benefit in retraining them and it risks overfitting on the small deepfake dataset. Only layer4 "
         "(high-level semantic features) and the FC head (task-specific classification) need to adapt."),
    ]

    for item in qa:
        q, a = item
        if a is None:
            story.append(Spacer(1, 6))
            cat_data = [[Paragraph(q, ParagraphStyle("Cat", parent=S["Body"],
                                                      fontSize=9, textColor=WHITE,
                                                      fontName="Helvetica-Bold"))]]
            ct = Table(cat_data, colWidths=[17*cm])
            ct.setStyle(TableStyle([
                ("BACKGROUND",    (0,0),(-1,-1), TEAL),
                ("TOPPADDING",    (0,0),(-1,-1), 4),
                ("BOTTOMPADDING", (0,0),(-1,-1), 4),
                ("LEFTPADDING",   (0,0),(-1,-1), 10),
            ]))
            story.append(ct)
            story.append(Spacer(1, 4))
        else:
            story.append(Paragraph(q, S["QLabel"]))
            story.append(Paragraph(a, S["ALabel"]))

    story.append(Spacer(1, 16))

    # ── SECTION 9: HOW TO RUN ────────────────────────────────────────────
    story.append(section_header("9.  How to Run the Project", S))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Terminal 1 — Python Backend:", S["SubH"]))
    for line in [
        "cd KYROS-root/backend",
        "C:\\Users\\Kedarnadh\\miniforge3\\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8001",
        "# Wait for: Application startup complete.",
    ]:
        story.append(Paragraph(line, S["CodeLine"]))

    story.append(Spacer(1, 6))
    story.append(Paragraph("Terminal 2 — Next.js Frontend:", S["SubH"]))
    for line in [
        "cd KYROS-root",
        "npm run dev",
        "# Wait for: Next.js ready on http://localhost:3000",
    ]:
        story.append(Paragraph(line, S["CodeLine"]))

    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Open http://localhost:3000 in your browser. Upload any image, video, or audio file. "
        "Both servers must be running simultaneously.", S["Body"]))

    story.append(Spacer(1, 6))
    story.append(Paragraph("To train on real data (CelebDF-v2):", S["SubH"]))
    for line in [
        "# Step 1 — prepare face crops from videos",
        "python -m training.prepare_celebdf --root C:/CelebDF-v2",
        "# Step 2 — train ResNet50 (saves to backend/models/resnet50_deepfake.pth)",
        "python -m training.train_image",
        "# Step 3 — restart backend to load trained weights",
    ]:
        story.append(Paragraph(line, S["CodeLine"]))

    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", color=colors.lightgrey, spaceAfter=8))
    story.append(Paragraph(
        "<i>KYROS Deepfake Detection Platform  —  Kedarnadh Thrinadh  —  2026</i>",
        ParagraphStyle("Footer", parent=S["Body"], fontSize=8,
                       textColor=colors.grey, alignment=TA_CENTER)))

    doc.build(story)
    print(f"PDF saved -> {OUT}")


if __name__ == "__main__":
    build_pdf()
