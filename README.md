# 🌿 Krishi Scan

> AI-powered plant disease detection & trilingual expert advice for Indian farmers

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29-red.svg)](https://streamlit.io)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docker.com)

---

## 🎯 What It Does

Krishi Scan helps farmers detect crop diseases instantly using AI:

1. 📸 **Upload** a leaf photo via the web app
2. 🔬 **AI detects** the disease using MobileNetV2 (trained on PlantVillage — 38 disease classes)
3. 🌤️ **Weather context** is auto-fetched using your GPS location
4. 💡 **Gemini AI** generates structured treatment advice in **English + Hindi + Gujarati**

---

## 🏗️ Architecture

```
Farmer → Streamlit UI → FastAPI Backend ─→ MobileNetV2 (HuggingFace)
              ↑                           ├→ OpenWeatherMap API
  Browser Geolocation                    └→ Gemini API → Trilingual Advice
  (auto lat/lon → city)
```

---

## 🧰 Tech Stack

| Layer        | Technology |
|--------------|------------|
| Frontend     | Streamlit (dark-mode dashboard) |
| Backend      | FastAPI (async) |
| Vision Model | `linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification` |
| AI Brain     | Google Gemini `gemini-1.5-flash` |
| Weather      | OpenWeatherMap Current Weather API |
| Location     | Browser Geolocation API (auto lat/lon) |
| Deploy       | Docker + Docker Compose |

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/tanish9630/Krishi-Scan.git
cd Krishi-Scan
```

### 2. Set up API keys
```bash
cp .env.example .env
# Edit .env with your keys:
# GEMINI_API_KEY     → https://aistudio.google.com
# OPENWEATHER_API_KEY → https://openweathermap.org/api
```

### 3. Run with Docker Compose
```bash
docker-compose up --build
```

- 🌐 **Frontend** → http://localhost:8501
- ⚙️ **Backend API** → http://localhost:8000
- 📖 **API Docs** → http://localhost:8000/docs

---

## 📂 Project Structure

```
Krishi Scan/
├── .env.example               ← API key template
├── docker-compose.yml         ← Docker orchestration
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                ← FastAPI entrypoint
│   ├── config.py              ← Settings & env vars
│   ├── schemas.py             ← Pydantic models
│   ├── routers/
│   │   ├── predict.py         ← POST /api/predict
│   │   └── weather.py         ← GET /api/weather
│   └── services/
│       ├── model_service.py   ← MobileNetV2 inference
│       ├── weather_service.py ← OpenWeatherMap integration
│       └── gemini_service.py  ← Trilingual Gemini advice
└── frontend/
    ├── Dockerfile
    ├── requirements.txt
    └── app.py                 ← Streamlit dashboard
```

---

## 🌾 Supported Crops & Diseases

Powered by the PlantVillage dataset — detects **38 classes** across:
Apple, Blueberry, Cherry, Corn/Maize, Grape, Orange, Peach, Pepper, Potato, Raspberry, Soybean, Squash, Strawberry, **Tomato**, and more.

---

## 📋 AI Advice Format

Each scan produces advice in 3 languages, structured as:

| Section | Content |
|---------|---------|
| 🔬 Diagnosis Summary | Disease description + weather impact |
| 🌿 Organic Control | 2 natural/desi remedies |
| 💊 Chemical Prescription | Exact Indian product + dosage |
| 💡 Farmer's Pro-Tip | 1 prevention tip for next season |

---

## 📜 License

MIT License — free to use, modify, and distribute.

---

*Built with ❤️ for Indian farmers 🇮🇳*
