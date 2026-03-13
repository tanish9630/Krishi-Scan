from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from typing import Optional
from schemas import PredictResponse
from services.model_service import model_service
from services.weather_service import weather_service
from services.gemini_service import gemini_service

router = APIRouter(tags=["Predict"])

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
MAX_FILE_SIZE_MB = 10


@router.post("/predict", response_model=PredictResponse)
async def predict_disease(
    image: UploadFile = File(..., description="Leaf image (JPEG/PNG/WebP)"),
    lat: Optional[float] = Form(None, description="GPS latitude"),
    lon: Optional[float] = Form(None, description="GPS longitude"),
):
    """
    Core endpoint:
    1. Validates uploaded leaf image
    2. Runs MobileNetV2 disease detection
    3. Fetches weather by GPS coords (if provided)
    4. Calls Gemini for trilingual AI advice
    5. Returns unified PredictResponse
    """
    # --- Validate image type ---
    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{image.content_type}'. Please upload JPEG, PNG, or WebP.",
        )

    # --- Read image bytes ---
    image_bytes = await image.read()

    # Guard against extremely large files
    size_mb = len(image_bytes) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=413,
            detail=f"Image too large ({size_mb:.1f} MB). Max allowed: {MAX_FILE_SIZE_MB} MB.",
        )

    # --- Step 1: Disease Detection ---
    try:
        disease_name, confidence = await model_service.predict_disease(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model inference failed: {str(e)}")

    # --- Step 2: Weather (optional, based on GPS) ---
    weather_data = None
    if lat is not None and lon is not None:
        weather_data = await weather_service.get_weather_by_coords(lat, lon)

    # --- Step 3: Gemini Advice ---
    ai_advice = await gemini_service.get_advice(disease_name, confidence, weather_data)

    return PredictResponse(
        disease_name=disease_name,
        confidence=confidence,
        weather_context=weather_data,
        ai_advice=ai_advice,
    )
