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
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  /* Global */
  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
  }

  /* Dark background */
  .stApp {
    background: linear-gradient(135deg, #0a1a0a 0%, #0d2b0d 50%, #0a1a0a 100%);
    color: #e8f5e8;
  }

  /* Hero header */
  .hero {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
  }
  .hero h1 {
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(135deg, #4ade80, #22d3ee, #a3e635);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.4rem;
  }
  .hero p {
    color: #86efac;
    font-size: 1.1rem;
    font-weight: 300;
  }

  /* Cards */
  .card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(74,222,128,0.2);
    border-radius: 16px;
    padding: 1.5rem;
    margin: 0.8rem 0;
    backdrop-filter: blur(10px);
    transition: border-color 0.3s ease;
  }
  .card:hover { border-color: rgba(74,222,128,0.5); }

  /* Disease result badge */
  .disease-badge {
    background: linear-gradient(135deg, #166534, #14532d);
    border: 2px solid #4ade80;
    border-radius: 12px;
    padding: 1.2rem 1.8rem;
    text-align: center;
    margin: 1rem 0;
  }
  .disease-badge h2 {
    font-size: 1.8rem;
    font-weight: 700;
    color: #4ade80;
    margin: 0 0 0.3rem 0;
  }
  .disease-badge .confidence {
    font-size: 1rem;
    color: #86efac;
  }

  /* Weather widget */
  .weather-card {
    background: rgba(34,211,238,0.08);
    border: 1px solid rgba(34,211,238,0.3);
    border-radius: 12px;
    padding: 1rem 1.4rem;
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  /* Upload area override */
  [data-testid="stFileUploader"] {
    background: rgba(74,222,128,0.05);
    border: 2px dashed rgba(74,222,128,0.4);
    border-radius: 12px;
    padding: 1rem;
    transition: border-color 0.3s ease;
  }
  [data-testid="stFileUploader"]:hover {
    border-color: rgba(74,222,128,0.8);
  }

  /* Button */
  .stButton > button {
    background: linear-gradient(135deg, #16a34a, #15803d) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.7rem 2rem !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    width: 100% !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(74,222,128,0.3) !important;
  }
  .stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(74,222,128,0.5) !important;
  }

  /* Tabs */
  .stTabs [data-baseweb="tab"] {
    background: rgba(74,222,128,0.1) !important;
    border-radius: 8px 8px 0 0 !important;
    color: #86efac !important;
    font-weight: 500 !important;
    border: 1px solid rgba(74,222,128,0.2) !important;
  }
  .stTabs [aria-selected="true"] {
    background: rgba(74,222,128,0.25) !important;
    color: #4ade80 !important;
    font-weight: 600 !important;
  }

  /* Divider */
  hr { border-color: rgba(74,222,128,0.2) !important; }

  /* Progress bar */
  .stProgress > div > div {
    background: linear-gradient(90deg, #4ade80, #22d3ee) !important;
    border-radius: 4px !important;
  }

  /* Info / warning overrides */
  .stAlert { border-radius: 10px !important; }

  /* Sidebar */
  .css-1d391kg { background: #0a1a0a !important; }

  /* Spinner */
  .stSpinner > div { border-top-color: #4ade80 !important; }
</style>
""", unsafe_allow_html=True)


# ─── Helper: Geolocation via JS injection ─────────────────────────────────────
def get_browser_location():
    """
    Uses streamlit-js-eval to run JS geolocation in the browser.
    Returns (lat, lon, city) or (None, None, None).
    """
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
    """Split advice text into language sections."""
    sections = {"English": "", "Hindi": "", "Gujarati": ""}
    current_lang = None
    buffer = []

    for line in advice_text.splitlines():
        stripped = line.strip()
        lower = stripped.lower()
        
        is_english_header = lower.startswith("##") and "english" in lower
        is_hindi_header = lower.startswith("##") and ("hindi" in lower or "हिंदी" in lower)
        is_gujarati_header = lower.startswith("##") and ("gujarati" in lower or "ગુજરાત" in lower)

        if is_english_header:
            if current_lang and buffer:
                sections[current_lang] = "\n".join(buffer).strip()
            current_lang = "English"
            buffer = []
        elif is_hindi_header:
            if current_lang and buffer:
                sections[current_lang] = "\n".join(buffer).strip()
            current_lang = "Hindi"
            buffer = []
        elif is_gujarati_header:
            if current_lang and buffer:
                sections[current_lang] = "\n".join(buffer).strip()
            current_lang = "Gujarati"
            buffer = []
        elif current_lang:
            buffer.append(line)

    if current_lang and buffer:
        sections[current_lang] = "\n".join(buffer).strip()

    # If parsing fails or only returns partial, keep everything in English as fallback
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
    # Hero
    st.markdown("""
    <div class="hero">
      <h1>🌿 Krishi Scan</h1>
      <p>AI-powered crop disease detection & trilingual expert advice for Indian farmers</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Layout: Left = input, Right = output ──────────────────────────────────
    col_left, col_right = st.columns([1, 1.4], gap="large")

    with col_left:
        st.markdown("### 📍 Your Location")

        # Geolocation
        lat, lon = get_browser_location()

        if lat and lon:
            st.success(f"📡 GPS detected: `{lat:.4f}, {lon:.4f}`")
            # Optionally show city name
            weather_preview = fetch_weather(lat, lon)
            if weather_preview:
                st.info(f"📍 Location: **{weather_preview.get('city', 'Unknown')}**")
        else:
            st.warning("📡 Location not detected. Allowing location access gives weather-aware advice!")
            city_fallback = st.text_input(
                "Or enter your city name manually:",
                placeholder="e.g., Mumbai, Pune, Ahmedabad",
            )
            lat, lon = None, None

        st.markdown("---")

        st.markdown("### 🌿 Upload Leaf Image")
        uploaded_file = st.file_uploader(
            "Take a clear photo of the affected leaf",
            type=["jpg", "jpeg", "png", "webp"],
            help="Upload a close-up photo of a single leaf for best results.",
        )

        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="📸 Uploaded leaf", use_column_width=True)

        st.markdown("---")

        scan_btn = st.button("🔬 Scan for Disease", disabled=(uploaded_file is None))

    # ── RIGHT PANEL ──────────────────────────────────────────────────────────
    with col_right:
        if not uploaded_file:
            st.markdown("""
            <div class="card" style="text-align:center; padding: 3rem 2rem;">
              <div style="font-size: 4rem; margin-bottom: 1rem;">🧑‍🌾</div>
              <h3 style="color: #4ade80; margin-bottom: 0.5rem;">Ready to scan your crops</h3>
              <p style="color: #86efac; font-size: 0.95rem;">
                Upload a leaf image on the left and click <b>Scan for Disease</b>.<br><br>
                You'll receive:<br>
                🔬 Disease diagnosis with confidence<br>
                🌤️ Weather-aware context<br>
                💊 Expert treatment advice<br>
                🌐 English + Hindi + Gujarati
              </p>
            </div>
            """, unsafe_allow_html=True)

        elif scan_btn:
            with st.spinner("🔬 Analyzing leaf... This may take a few seconds on first run while the model loads."):
                try:
                    image_bytes = uploaded_file.getvalue()
                    result = run_prediction(image_bytes, lat, lon)
                except requests.exceptions.ConnectionError:
                    st.error(
                        "❌ Cannot connect to backend. "
                        "Make sure the backend is running at `http://localhost:8000`."
                    )
                    st.stop()
                except requests.exceptions.Timeout:
                    st.error("⏱️ Request timed out. The model may still be loading. Please try again in 30 seconds.")
                    st.stop()
                except Exception as e:
                    st.error(f"❌ Unexpected error: {str(e)}")
                    st.stop()

            # ── Disease Badge ─────────────────────────────────────────────────
            disease = result.get("disease_name", "Unknown")
            confidence = result.get("confidence", 0.0)
            is_healthy = "healthy" in disease.lower()

            badge_color = "#4ade80" if is_healthy else "#f87171"
            badge_bg = "#14532d" if is_healthy else "#450a0a"
            badge_border = "#4ade80" if is_healthy else "#f87171"
            badge_icon = "✅" if is_healthy else "⚠️"

            st.markdown(f"""
            <div style="
              background: {badge_bg};
              border: 2px solid {badge_border};
              border-radius: 14px;
              padding: 1.4rem 1.8rem;
              text-align: center;
              margin-bottom: 1rem;
            ">
              <div style="font-size: 2.5rem; margin-bottom: 0.3rem;">{badge_icon}</div>
              <h2 style="font-size: 1.6rem; font-weight: 700; color: {badge_color}; margin: 0 0 0.3rem 0;">
                {disease}
              </h2>
              <p style="color: #94a3b8; margin: 0; font-size: 0.95rem;">Detection Confidence</p>
            </div>
            """, unsafe_allow_html=True)

            st.progress(min(confidence / 100, 1.0))
            st.markdown(f"<p style='text-align:center; color:#86efac; margin-top:-8px;'><b>{confidence:.1f}%</b> confidence</p>", unsafe_allow_html=True)

            # ── Weather Context ───────────────────────────────────────────────
            weather = result.get("weather_context")
            if weather:
                icon = get_weather_icon(weather.get("description", ""))
                st.markdown(f"""
                <div class="card" style="margin: 0.8rem 0;">
                  <div style="display:flex; align-items:center; gap: 1rem;">
                    <span style="font-size: 2.5rem;">{icon}</span>
                    <div>
                      <div style="font-weight:600; color:#22d3ee; font-size:1.05rem;">
                        📍 {weather.get("city", "Unknown")}
                      </div>
                      <div style="color:#94a3b8; font-size:0.9rem;">
                        🌡️ {weather.get("temperature")}°C &nbsp;|&nbsp;
                        💧 {weather.get("humidity")}% humidity &nbsp;|&nbsp;
                        {weather.get("description", "")}
                      </div>
                    </div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

            # ── Trilingual Advice ─────────────────────────────────────────────
            advice_text = result.get("ai_advice", "")
            if advice_text:
                st.markdown("### 📋 Expert Advice")
                lang_sections = parse_advice(advice_text)

                tab_en, tab_hi, tab_gu = st.tabs(["🇬🇧 English", "🇮🇳 Hindi", "🏛️ Gujarati"])

                with tab_en:
                    content = lang_sections.get("English", "")
                    if content:
                        st.markdown(content)
                    else:
                        st.info("English advice not available.")

                with tab_hi:
                    content = lang_sections.get("Hindi", "")
                    if content:
                        st.markdown(content)
                    else:
                        st.info("Hindi advice not available.")

                with tab_gu:
                    content = lang_sections.get("Gujarati", "")
                    if content:
                        st.markdown(content)
                    else:
                        st.info("Gujarati advice not available.")

            # ── Raw JSON expander ─────────────────────────────────────────────
            with st.expander("🔧 Raw API Response (Debug)"):
                st.json(result)

        elif uploaded_file:
            # Image uploaded but button not clicked
            st.markdown("""
            <div class="card" style="text-align:center; padding: 2.5rem 2rem;">
              <div style="font-size: 3rem; margin-bottom: 0.8rem;">👈</div>
              <h3 style="color: #4ade80;">Click <em>Scan for Disease</em> to analyze</h3>
              <p style="color: #86efac;">Your leaf image is ready. Hit the button to get AI-powered diagnosis.</p>
            </div>
            """, unsafe_allow_html=True)

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; color: #4b5563; font-size: 0.8rem; padding: 0.5rem;">
      🌿 <b>Krishi Scan</b> — Powered by MobileNetV2 + Gemini AI + OpenWeatherMap<br>
      Built for Indian farmers 🇮🇳 | Always consult a local agronomist for critical decisions.
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
