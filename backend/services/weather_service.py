import httpx
from schemas import WeatherData
from config import settings


class WeatherService:
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

    async def get_weather_by_coords(self, lat: float, lon: float) -> WeatherData | None:
        """
        Fetches current weather from OpenWeatherMap using lat/lon.
        Returns WeatherData or None if the API call fails.
        """
        if not settings.OPENWEATHER_API_KEY:
            return None

        params = {
            "lat": lat,
            "lon": lon,
            "appid": settings.OPENWEATHER_API_KEY,
            "units": "metric",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()

            city = data.get("name", "Unknown")
            # country = data.get("sys", {}).get("country", "")
            temp = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            description = data["weather"][0]["description"].capitalize()

            return WeatherData(
                city=city,
                temperature=round(temp, 1),
                humidity=humidity,
                description=description,
            )

        except Exception as e:
            print(f"[WeatherService] Failed to fetch weather: {e}")
            return None


# Singleton
weather_service = WeatherService()
