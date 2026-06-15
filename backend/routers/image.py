import time
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response
from services.image_service import ImageDetectionService
from utils.report import generate_pdf_report

router = APIRouter()
_service: ImageDetectionService | None = None


def get_service() -> ImageDetectionService:
    global _service
    if _service is None:
        _service = ImageDetectionService()
    return _service


@router.post("/image")
async def detect_image(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image (jpg, png, webp)")

    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image must be under 10 MB")

    start = time.perf_counter()
    try:
        result = get_service().analyze(contents, file.filename or "image.jpg")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}")

    result["processingTime"] = round(time.perf_counter() - start, 2)
    return result


@router.post("/image/report")
async def image_report(file: UploadFile = File(...)):
    contents = await file.read()
    start = time.perf_counter()
    result = get_service().analyze(contents, file.filename or "image.jpg")
    result["processingTime"] = round(time.perf_counter() - start, 2)

    pdf_bytes = generate_pdf_report(result, file.filename or "image.jpg", "Image")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=kyros_image_report.pdf"},
    )
