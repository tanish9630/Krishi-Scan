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
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

  /* Global */
  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
  }

  /* Dark background */
  .stApp {
    background: linear-gradient(135deg, #0f172a 0%, #064e3b 50%, #020617 100%);
    color: #f8fafc;
  }

  /* Header Navbar */
  .navbar {
    background: rgba(15, 23, 42, 0.7);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid rgba(74, 222, 128, 0.2);
    padding: 1.5rem 2rem;
    margin: -4rem -4rem 2rem -4rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .navbar h1 {
    margin: 0;
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #4ade80, #38bdf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .navbar span { color: #94a3b8; font-weight: 500; }

  /* Premium Cards */
  .premium-card {
    background: rgba(30, 41, 59, 0.4);
    border: 1px solid rgba(148, 163, 184, 0.15);
    border-radius: 20px;
    padding: 1.8rem;
    backdrop-filter: blur(16px);
    box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5);
    margin-bottom: 1.5rem;
  }

  /* Diagnosis Header Hero */
  .diagnosis-hero {
    background: linear-gradient(135deg, rgba(20, 83, 45, 0.8), rgba(2, 44, 34, 0.8));
    border: 1px solid #4ade80;
    border-radius: 24px;
    padding: 2.5rem;
    text-align: left;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .diagnosis-hero h2 {
    font-size: 3.5rem;
    font-weight: 800;
    color: #4ade80;
    margin: 0;
    line-height: 1.1;
  }
  .diagnosis-hero.warning {
    background: linear-gradient(135deg, rgba(127, 29, 29, 0.8), rgba(69, 10, 10, 0.8));
    border-color: #f87171;
  }
  .diagnosis-hero.warning h2 { color: #f87171; }
  .diagnosis-icon { font-size: 5rem; }

  /* Upload area override */
  [data-testid="stFileUploader"] {
    background: rgba(15, 23, 42, 0.5);
    border: 2px dashed rgba(74, 222, 128, 0.3);
    border-radius: 16px;
    padding: 1.5rem;
    transition: border-color 0.3s ease;
  }
  [data-testid="stFileUploader"]:hover { border-color: #4ade80; }

  /* Primary Button */
  .stButton > button {
    background: linear-gradient(135deg, #16a34a, #059669) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 1rem 2rem !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    width: 100% !important;
    transition: transform 0.2s, box-shadow 0.2s !important;
    box-shadow: 0 4px 15px rgba(22, 163, 74, 0.4) !important;
  }
  .stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(22, 163, 74, 0.6) !important;
  }

  /* Tabs */
  .stTabs [data-baseweb="tab"] {
    background: rgba(30, 41, 59, 0.6) !important;
    border-radius: 12px 12px 0 0 !important;
    color: #cbd5e1 !important;
    font-weight: 600 !important;
    padding: 1rem 2rem !important;
    border: 1px solid rgba(148, 163, 184, 0.1) !important;
    border-bottom: none !important;
  }
  .stTabs [aria-selected="true"] {
    background: rgba(20, 83, 45, 0.6) !important;
    color: #4ade80 !important;
    border-color: rgba(74, 222, 128, 0.3) !important;
  }

  /* Metrics styling inside cards */
  .metric-label { font-size: 0.9rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem; font-weight: 600; }
  .metric-value { font-size: 2.2rem; font-weight: 800; color: #f8fafc; }
  .metric-sub { font-size: 1rem; color: #cbd5e1; }

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
    # Navbar Header
    st.markdown("""
    <div class="navbar">
      <h1>🌿 Krishi Scan</h1>
      <span>AI Disease Detection Dashboard</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Main Layout: 1/3 Sidebar Panel, 2/3 Results Board ─────────────────────
    col_panel, spacer, col_dashboard = st.columns([1.2, 0.1, 2.7])

    # ── LEFT PANEL: Controls & Input ──────────────────────────────────────────
    with col_panel:
        st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
        st.markdown("### 📍 Location Context")
        
        lat, lon = get_browser_location()
        if lat and lon:
            weather_preview = fetch_weather(lat, lon)
            if weather_preview:
                city = weather_preview.get('city', 'Unknown')
                st.markdown(f"**GPS Locked:** {city}")
                st.success("Geolocation active for localized advice.")
            else:
                st.success(f"GPS locked: {lat:.3f}, {lon:.3f}")
        else:
            st.warning("⚠️ Location not available.")
            st.markdown("<small style='color:#94a3b8;'>Allow browser location for weather-aware AI advice, or enter city manually:</small>", unsafe_allow_html=True)
            city_fallback = st.text_input("", placeholder="e.g., Nashik, Gujarat...")
            lat, lon = None, None

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
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
        st.markdown("</div>", unsafe_allow_html=True)

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
            
            hero_class = "diagnosis-hero" if is_healthy else "diagnosis-hero warning"
            icon = "✅" if is_healthy else "⚠️"

            # 1. Top Section: Huge Diagnosis Hero
            st.markdown(f"""
            <div class="{hero_class}">
              <div>
                <div class="metric-label" style="color: rgba(255,255,255,0.7);">Primary AI Diagnosis</div>
                <h2>{disease}</h2>
              </div>
              <div class="diagnosis-icon">{icon}</div>
            </div>
            """, unsafe_allow_html=True)

            # 2. Middle Grid: Confidence (L) + Weather (R)
            mid_l, mid_r = st.columns(2)
            
            with mid_l:
                st.markdown("<div class='premium-card' style='height:140px;'>", unsafe_allow_html=True)
                st.markdown("<div class='metric-label'>Model Confidence</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='metric-value'>{confidence:.1f}%</div>", unsafe_allow_html=True)
                st.progress(min(confidence / 100, 1.0))
                st.markdown("</div>", unsafe_allow_html=True)

            with mid_r:
                st.markdown("<div class='premium-card' style='height:140px;'>", unsafe_allow_html=True)
                st.markdown("<div class='metric-label'>Local Conditions</div>", unsafe_allow_html=True)
                if weather:
                    w_icon = get_weather_icon(weather.get("description", ""))
                    st.markdown(f"""
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                      <div>
                        <div class='metric-value'>{weather.get("temperature")}°C</div>
                        <div class='metric-sub'>{weather.get("humidity")}% Humidity • {weather.get("city")}</div>
                      </div>
                      <div style="font-size:3rem;">{w_icon}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("<div class='metric-value'>—</div>", unsafe_allow_html=True)
                    st.markdown("<div class='metric-sub'>Weather data unavailable</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            # 3. Bottom Section: Trilingual Advice Board
            advice_text = result.get("ai_advice", "")
            if advice_text:
                st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
                st.markdown("<div class='metric-label' style='margin-bottom:1rem;'>Expert Agronomist Report</div>", unsafe_allow_html=True)
                
                lang_sections = parse_advice(advice_text)
                tab_en, tab_hi, tab_gu = st.tabs(["🇬🇧 English", "🇮🇳 Hindi", "🏛️ Gujarati"])

                with tab_en:
                    st.markdown(lang_sections.get("English", "Not available."))
                with tab_hi:
                    st.markdown(lang_sections.get("Hindi", "Not available."))
                with tab_gu:
                    st.markdown(lang_sections.get("Gujarati", "Not available."))
                
                st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
