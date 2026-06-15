import time
from fastapi import APIRouter, File, HTTPException, UploadFile
from services.video_service import VideoDetectionService

router = APIRouter()
_service: VideoDetectionService | None = None


def get_service() -> VideoDetectionService:
    global _service
    if _service is None:
        _service = VideoDetectionService()
    return _service


@router.post("/video")
async def detect_video(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="File must be a video (mp4, mov, avi, webm)")

    contents = await file.read()
    if len(contents) > 50 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Video must be under 50 MB")

    start = time.perf_counter()
    try:
        result = get_service().analyze(contents, file.filename or "video.mp4")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}")

    result["processingTime"] = round(time.perf_counter() - start, 2)
    return result
