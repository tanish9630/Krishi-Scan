from pydantic import BaseModel
from typing import Optional

class WeatherData(BaseModel):
    city: str
    temperature: float
    humidity: int
    description: str

class PredictResponse(BaseModel):
    disease_name: str
    confidence: float
    weather_context: Optional[WeatherData] = None
    ai_advice: str

class ErrorResponse(BaseModel):
    detail: str
