import google.generativeai as genai
from config import settings
from schemas import WeatherData
from typing import Optional


class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def _build_prompt(
        self,
        disease_name: str,
        confidence: float,
        weather: Optional[WeatherData],
    ) -> str:
        weather_context = ""
        if weather:
            weather_context = (
                f"Current weather in {weather.city}: "
                f"{weather.temperature}°C, {weather.humidity}% humidity, "
                f"{weather.description}."
            )
        else:
            weather_context = "Weather data unavailable."

        return f"""You are an expert agricultural scientist and friendly advisor for Indian farmers.

A farmer has uploaded a plant leaf image. The AI model detected:
- Disease: {disease_name}
- Confidence: {confidence:.1f}%
- {weather_context}

Provide structured advice in exactly THREE languages in this order: English → Hindi → Gujarati.
For EACH language, give ALL FOUR sections listed below, formatted with clear headers.

Use this exact structure (repeat for all 3 languages):

---
## [Language Name]

### 🔬 Diagnosis Summary
(2 sentences: what the disease is + whether current weather makes it worse)

### 🌿 Organic Control (Desi Way)
(2 natural methods — e.g., neem spray, copper sulfate wash, pruning infected leaves)

### 💊 Chemical Prescription
(Name EXACTLY ONE Indian commercial product — e.g., **Mancozeb 75 WP** — with dosage in **Xg/Litre** or **Xml/Litre**)

### 💡 Farmer's Pro-Tip
(1 prevention tip for the next crop cycle)
---

Tone: Friendly local scientist. Bold the medicine name and dosage. Keep each section to 2–3 lines max.
If the detected label contains "Healthy", reassure the farmer and give maintenance tips instead.
"""

    async def get_advice(
        self,
        disease_name: str,
        confidence: float,
        weather: Optional[WeatherData],
    ) -> str:
        """Generate trilingual structured farming advice using Gemini."""
        if not settings.GEMINI_API_KEY:
            return (
                "⚠️ Gemini API key not configured. "
                "Please add GEMINI_API_KEY to your .env file to receive AI-powered advice."
            )

        try:
            prompt = self._build_prompt(disease_name, confidence, weather)
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"[GeminiService] Failed to generate advice: {e}")
            return f"⚠️ Could not generate AI advice at this time. Error: {str(e)}"


# Singleton
gemini_service = GeminiService()
