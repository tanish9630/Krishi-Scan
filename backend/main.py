from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import urllib.request
import json
import httpx

from routers import predict, weather
from config import settings

app = FastAPI(
    title="Krishi Scan API",
    description="AI Plant Disease Detection & Consulting API",
    version="1.0.0"
)

# Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(predict.router, prefix="/api")
app.include_router(weather.router, prefix="/api")


@app.get("/api/location")
async def get_location_proxy():
    try:
        req = urllib.request.Request("https://ipwho.is/", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if data.get("success"):
                return {"lat": data.get("latitude"), "lon": data.get("longitude")}
            return {"error": data.get("message"), "lat": None, "lon": None}
    except Exception as e:
        return {"error": str(e), "lat": None, "lon": None}


@app.get("/api/geocode")
async def geocode_city(city: str = Query(..., description="City name to geocode")):
    """Convert a city name to lat/lon using OpenWeatherMap Geocoding API."""
    if not settings.OPENWEATHER_API_KEY:
        return {"error": "OPENWEATHER_API_KEY not set", "lat": None, "lon": None}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "http://api.openweathermap.org/geo/1.0/direct",
                params={"q": city, "limit": 1, "appid": settings.OPENWEATHER_API_KEY},
            )
            resp.raise_for_status()
            results = resp.json()
            if results:
                return {"lat": results[0]["lat"], "lon": results[0]["lon"], "city": results[0].get("name")}
            return {"error": "City not found", "lat": None, "lon": None}
    except Exception as e:
        return {"error": str(e), "lat": None, "lon": None}


@app.get("/")
async def root():
    return {"message": "Welcome to Krishi Scan API"}

