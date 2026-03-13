from fastapi import APIRouter, HTTPException, Query
from schemas import WeatherData
from services.weather_service import weather_service

router = APIRouter(tags=["Weather"])


@router.get("/weather", response_model=WeatherData)
async def get_weather(
    lat: float = Query(..., description="GPS latitude"),
    lon: float = Query(..., description="GPS longitude"),
):
    """
    Fetch current weather by GPS coordinates using OpenWeatherMap.
    Used by the frontend to display contextual weather and city name.
    """
    weather = await weather_service.get_weather_by_coords(lat, lon)

    if weather is None:
        raise HTTPException(
            status_code=503,
            detail="Could not fetch weather data. Check your OPENWEATHER_API_KEY.",
        )

    return weather
