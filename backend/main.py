from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import image, video, audio

app = FastAPI(
    title="KYROS Deepfake Detection API",
    description="AI-powered deepfake detection for images, video, and audio",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(image.router, prefix="/detect", tags=["Image Detection"])
app.include_router(video.router, prefix="/detect", tags=["Video Detection"])
app.include_router(audio.router, prefix="/detect", tags=["Audio Detection"])


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "KYROS API v1.0.0"}
