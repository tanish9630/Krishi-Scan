import os
import requests
import streamlit as st
from PIL import Image
import io
import json

# ─── Config ───────────────────────────────────────────────────────────────────
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Krishi Scan 🌿",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* Clean up the default Streamlit UI a bit without heavy themes */
  .main .block-container {
    padding-top: 2rem;
  }
  
  /* Primary Button */
  .stButton > button {
    background-color: #16a34a !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.5rem 1rem !important;
    font-weight: 600 !important;
  }
  .stButton > button:hover {
    background-color: #15803d !important;
  }

  /* Simple Header */
  .navbar-container {
    padding-bottom: 1rem;
    border-bottom: 2px solid #e5e7eb;
    margin-bottom: 2rem;
  }
  
  .navbar-container h1 {
    color: #16a34a;
    margin-bottom: 0.2rem;
  }

  /* Simple Cards for Results */
  .result-card {
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    color: #1e293b;
  }
  
  .result-card h3 {
    margin-top: 0;
    color: #0f172a;
  }
  
  /* Dark mode overrides for cards */
  @media (prefers-color-scheme: dark) {
    .result-card {
      background-color: #1e293b;
      border-color: #334155;
      color: #f8fafc;
    }
    .result-card h3 {
      color: #f1f5f9;
    }
    .navbar-container {
      border-bottom-color: #334155;
    }
  }
</style>
""", unsafe_allow_html=True)


# ─── Helper: Geolocation via JS injection ─────────────────────────────────────
def get_browser_location():
    try:
        from streamlit_js_eval import get_geolocation
        loc = get_geolocation()
        if loc and "coords" in loc:
            lat = loc["coords"].get("latitude")
            lon = loc["coords"].get("longitude")
            return lat, lon
    except Exception:
        pass
    return None, None


# ─── Helper: Call backend /api/weather ────────────────────────────────────────
def fetch_weather(lat: float, lon: float):
    try:
        resp = requests.get(
            f"{BACKEND_URL}/api/weather",
            params={"lat": lat, "lon": lon},
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None


# ─── Helper: Call backend /api/predict ───────────────────────────────────────
def run_prediction(image_bytes: bytes, lat, lon):
    data = {}
    if lat is not None:
        data["lat"] = str(lat)
    if lon is not None:
        data["lon"] = str(lon)

    files = {"image": ("leaf.jpg", image_bytes, "image/jpeg")}
    resp = requests.post(
        f"{BACKEND_URL}/api/predict",
        files=files,
        data=data,
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()


# ─── Helper: Parse trilingual advice into sections ────────────────────────────
def parse_advice(advice_text: str) -> dict:
    sections = {"English": "", "Hindi": "", "Gujarati": ""}
    current_lang = None
    buffer = []

    for line in advice_text.splitlines():
        stripped = line.strip()
        lower = stripped.lower()
        
        is_english = lower.startswith("##") and "english" in lower
        is_hindi = lower.startswith("##") and ("hindi" in lower or "हिंदी" in lower)
        is_gujarati = lower.startswith("##") and ("gujarati" in lower or "ગુજરાત" in lower)

        if is_english:
            if current_lang and buffer:
                sections[current_lang] = "\n".join(buffer).strip()
            current_lang = "English"
            buffer = []
        elif is_hindi:
            if current_lang and buffer:
                sections[current_lang] = "\n".join(buffer).strip()
            current_lang = "Hindi"
            buffer = []
        elif is_gujarati:
            if current_lang and buffer:
                sections[current_lang] = "\n".join(buffer).strip()
            current_lang = "Gujarati"
            buffer = []
        elif current_lang:
            buffer.append(line)

    if current_lang and buffer:
        sections[current_lang] = "\n".join(buffer).strip()

    if not any(sections.values()):
        sections["English"] = advice_text

    return sections


# ─── Weather display helper ───────────────────────────────────────────────────
WEATHER_ICONS = {
    "clear": "☀️", "cloud": "☁️", "rain": "🌧️",
    "drizzle": "🌦️", "thunder": "⛈️", "snow": "❄️",
    "mist": "🌫️", "haze": "🌫️", "fog": "🌫️",
}

def get_weather_icon(description: str) -> str:
    desc_lower = description.lower()
    for key, icon in WEATHER_ICONS.items():
        if key in desc_lower:
            return icon
    return "🌡️"


# ─── Main App ────────────────────────────────────────────────────────────────
def main():
    st.markdown("""
    <div class="navbar-container">
      <h1>🌿 Krishi Scan</h1>
      <p style="color: #64748b;">Crop Disease Detection & Trilingual Expert Advice</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Main Layout: 1/3 Sidebar Panel, 2/3 Results Board ─────────────────────
    col_panel, spacer, col_dashboard = st.columns([1.2, 0.1, 2.7])

    # ── LEFT PANEL: Controls & Input ──────────────────────────────────────────
    with col_panel:
        st.markdown("### 📍 Location Context")
        
        lat, lon = get_browser_location()
        if lat and lon:
            weather_preview = fetch_weather(lat, lon)
            if weather_preview:
                city = weather_preview.get('city', 'Unknown')
                st.success(f"**GPS Locked:** {city}")
            else:
                st.success(f"GPS locked: {lat:.3f}, {lon:.3f}")
        else:
            st.warning("Location not available. Enter city manually:")
            city_fallback = st.text_input("", placeholder="e.g., Nashik, Gujarat...")
            lat, lon = None, None

        st.markdown("---")
        st.markdown("### 📸 Crop Image")
        uploaded_file = st.file_uploader(
            "Upload leaf photo for AI analysis",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed"
        )

        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Ready for scan", use_column_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        scan_btn = st.button("🔬 Analyze Crop Data", disabled=(uploaded_file is None))

    # ── RIGHT PANEL: Results Dashboard ────────────────────────────────────────
    with col_dashboard:
        if not uploaded_file:
            st.markdown("""
            <div style="height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; opacity: 0.5; padding-top: 5rem;">
              <div style="font-size: 6rem; margin-bottom: 1rem;">🍃</div>
              <h2>Awaiting Crop Data...</h2>
              <p>Upload a leaf image on the left panel to begin analysis.</p>
            </div>
            """, unsafe_allow_html=True)

        elif scan_btn:
            with st.spinner("🔬 Running MobileNetV2 Vision Inference & Gemini AI..."):
                try:
                    image_bytes = uploaded_file.getvalue()
                    result = run_prediction(image_bytes, lat, lon)
                except Exception as e:
                    st.error(f"❌ Analysis failed: {str(e)}")
                    st.stop()

            # Result parsing
            disease = result.get("disease_name", "Unknown")
            confidence = result.get("confidence", 0.0)
            is_healthy = "healthy" in disease.lower()
            weather = result.get("weather_context")
            
            icon = "✅" if is_healthy else "⚠️"

            # 1. Top Section: Diagnosis
            st.markdown(f"""
            <div class="result-card">
              <h3>{icon} AI Diagnosis: {disease}</h3>
              <p style="margin: 0; color: #64748b;">Confidence Score: <b>{confidence:.1f}%</b></p>
            </div>
            """, unsafe_allow_html=True)
            st.progress(min(confidence / 100, 1.0))

            # 2. Middle Grid: Weather
            if weather:
                w_icon = get_weather_icon(weather.get("description", ""))
                st.markdown(f"""
                <div class="result-card">
                  <h4 style="margin-top:0;">{w_icon} Local Weather ({weather.get("city")})</h4>
                  <p style="margin:0;">{weather.get("temperature")}°C | {weather.get("humidity")}% Humidity | {weather.get("description", "").title()}</p>
                </div>
                """, unsafe_allow_html=True)

            # 3. Bottom Section: Trilingual Advice Board
            advice_text = result.get("ai_advice", "")
            if advice_text:
                st.markdown("### 📋 Expert Agronomist Report")
                
                lang_sections = parse_advice(advice_text)
                tab_en, tab_hi, tab_gu = st.tabs(["🇬🇧 English", "🇮🇳 Hindi", "🏛️ Gujarati"])

                with tab_en:
                    st.markdown(lang_sections.get("English", "Not available."))
                with tab_hi:
                    st.markdown(lang_sections.get("Hindi", "Not available."))
                with tab_gu:
                    st.markdown(lang_sections.get("Gujarati", "Not available."))


if __name__ == "__main__":
    main()
