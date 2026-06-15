import time
from fastapi import APIRouter, File, HTTPException, UploadFile
from services.audio_service import AudioDetectionService

router = APIRouter()
_service: AudioDetectionService | None = None


def get_service() -> AudioDetectionService:
    global _service
    if _service is None:
        _service = AudioDetectionService()
    return _service


@router.post("/audio")
async def detect_audio(file: UploadFile = File(...)):
    if file.content_type and not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="File must be an audio file (mp3, wav, m4a, ogg)")

    contents = await file.read()
    if len(contents) > 20 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Audio must be under 20 MB")

    start = time.perf_counter()
    try:
        result = get_service().analyze(contents, file.filename or "audio.wav")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}")

    result["processingTime"] = round(time.perf_counter() - start, 2)
    return result
