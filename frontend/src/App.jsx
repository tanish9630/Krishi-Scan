import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Leaf, MapPin, UploadCloud, Thermometer, Droplets, Cloud, FileText } from 'lucide-react';

const BACKEND_URL = "http://localhost:8000";

function App() {
  const [location, setLocation] = useState(null);
  const [weatherPreview, setWeatherPreview] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  
  const [activeTab, setActiveTab] = useState('English');
  const [cityInput, setCityInput] = useState('');
  const [cityError, setCityError] = useState(null);
  const [isLocating, setIsLocating] = useState(false);

  const handleManualCity = async () => {
    if (!cityInput.trim()) return;
    setIsLocating(true);
    setCityError(null);
    try {
      const res = await axios.get(`${BACKEND_URL}/api/geocode`, { params: { city: cityInput.trim() } });
      if (res.data.lat && res.data.lon) {
        const lat = res.data.lat;
        const lon = res.data.lon;
        setLocation({ lat, lon });
        const weatherRes = await axios.get(`${BACKEND_URL}/api/weather`, { params: { lat, lon } });
        setWeatherPreview(weatherRes.data);
        setCityInput('');
      } else {
        setCityError(res.data.error || "City not found. Try again.");
      }
    } catch (err) {
      setCityError("Could not find that city. Try a different spelling.");
    } finally {
      setIsLocating(false);
    }
  };

  useEffect(() => {
    const fetchIpLocation = async () => {
      try {
        const res = await axios.get(`${BACKEND_URL}/api/location`);
        if (res.data.lat && res.data.lon) {
          const lat = res.data.lat;
          const lon = res.data.lon;
          setLocation({ lat, lon });
          
          // Fetch weather context immediately
          const weatherRes = await axios.get(`${BACKEND_URL}/api/weather`, { params: { lat, lon } });
          setWeatherPreview(weatherRes.data);
        } else {
          console.error("Backend proxy failed to fetch location.");
        }
      } catch (err) {
        console.error("Failed to fetch location from IP:", err);
      }
    };

    // Fetch Location
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(async (position) => {
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;
        setLocation({ lat, lon });
        
        // Fetch weather immediately for location context
        try {
          const res = await axios.get(`${BACKEND_URL}/api/weather`, { params: { lat, lon } });
          setWeatherPreview(res.data);
        } catch (err) {
          console.error("Failed to fetch weather context.");
        }
      }, (err) => {
        console.warn("Geolocation denied or unavailable. Trying IP fallback...");
        fetchIpLocation();
      });
    } else {
      fetchIpLocation();
    }
  }, []);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setResult(null); // Clear previous results
    }
  };

  const parseAdvice = (adviceText) => {
    const sections = { English: "", Hindi: "", Gujarati: "" };
    let currentLang = null;
    let buffer = [];

    const lines = adviceText.split('\n');
    for (const line of lines) {
      const lower = line.trim().toLowerCase();
      const isEnglish = lower.startsWith("##") && lower.includes("english");
      const isHindi = lower.startsWith("##") && (lower.includes("hindi") || lower.includes("हिंदी"));
      const isGujarati = lower.startsWith("##") && (lower.includes("gujarati") || lower.includes("ગુજરાત"));

      if (isEnglish) {
        if (currentLang) sections[currentLang] = buffer.join('\n').trim();
        currentLang = "English";
        buffer = [];
      } else if (isHindi) {
        if (currentLang) sections[currentLang] = buffer.join('\n').trim();
        currentLang = "Hindi";
        buffer = [];
      } else if (isGujarati) {
        if (currentLang) sections[currentLang] = buffer.join('\n').trim();
        currentLang = "Gujarati";
        buffer = [];
      } else if (currentLang) {
        buffer.push(line);
      }
    }
    
    if (currentLang) sections[currentLang] = buffer.join('\n').trim();
    if (!sections.English && !sections.Hindi && !sections.Gujarati) {
      sections.English = adviceText;
    }
    return sections;
  };

  const handleScan = async () => {
    if (!selectedFile) return;
    setIsLoading(true);
    setError(null);
    
    const formData = new FormData();
    formData.append("image", selectedFile);
    if (location) {
      formData.append("lat", location.lat);
      formData.append("lon", location.lon);
    }

    try {
      const res = await axios.post(`${BACKEND_URL}/api/predict`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Analysis failed to connect to backend.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-6 max-w-7xl mx-auto">
      {/* Navbar */}
      <div className="text-center pb-6 mb-10 bg-white/5 backdrop-blur-md rounded-3xl border border-white/10 p-10 shadow-sm">
        <h1 className="text-emerald-500 font-bold text-5xl mb-2 flex items-center justify-center gap-3">
          <Leaf className="w-12 h-12" /> Krishi Scan
        </h1>
        <p className="text-xl text-slate-500">Next-Generation Crop Disease Detection & Trilingual Expert Advice</p>
      </div>

      {/* Main Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
        
        {/* Left Panel */}
        <div className="space-y-6">
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
            <h3 className="text-center font-semibold text-xl mb-4 flex justify-center items-center gap-2">
              <MapPin className="w-5 h-5 text-emerald-600" /> Location Context
            </h3>
            {weatherPreview ? (
              <div className="bg-emerald-50 text-emerald-800 p-4 rounded-xl border border-emerald-100 flex items-center gap-3 font-medium">
                <span className="text-2xl">✅</span> GPS Locked: {weatherPreview.city}
              </div>
            ) : location ? (
              <div className="bg-emerald-50 text-emerald-800 p-4 rounded-xl border border-emerald-100 flex items-center gap-3 font-medium">
                <span className="text-2xl">✅</span> GPS locked: {location.lat.toFixed(3)}, {location.lon.toFixed(3)}
              </div>
            ) : (
              <div className="space-y-3">
                <div className="bg-amber-50 text-amber-800 p-3 rounded-xl border border-amber-100 text-sm font-medium">
                  📍 Auto-location unavailable. Enter your city below.
                </div>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={cityInput}
                    onChange={(e) => setCityInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleManualCity()}
                    placeholder="e.g. Mumbai, Delhi, Surat..."
                    className="flex-1 border border-slate-300 rounded-xl px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400"
                  />
                  <button
                    onClick={handleManualCity}
                    disabled={isLocating || !cityInput.trim()}
                    className="bg-emerald-500 hover:bg-emerald-600 text-white font-semibold px-4 py-2 rounded-xl text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isLocating ? '...' : 'Set'}
                  </button>
                </div>
                {cityError && <p className="text-red-500 text-sm">{cityError}</p>}
              </div>
            )}
            {/* Manual override if already set */}
            {weatherPreview && (
              <div className="mt-3 flex gap-2">
                <input
                  type="text"
                  value={cityInput}
                  onChange={(e) => setCityInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleManualCity()}
                  placeholder="Change city..."
                  className="flex-1 border border-slate-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400 text-slate-600"
                />
                <button
                  onClick={handleManualCity}
                  disabled={isLocating || !cityInput.trim()}
                  className="bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold px-3 py-2 rounded-xl text-sm disabled:opacity-50"
                >
                  {isLocating ? '...' : 'Change'}
                </button>
              </div>
            )}
          </div>

          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
            <h3 className="text-center font-semibold text-xl mb-4 flex justify-center items-center gap-2">
              <UploadCloud className="w-5 h-5 text-emerald-600" /> Crop Image
            </h3>
            
            <label className="border-2 border-dashed border-slate-300 bg-slate-50 hover:bg-slate-100 transition-colors rounded-xl cursor-pointer flex flex-col items-center justify-center p-8 mb-4 min-h-[250px]">
              <input type="file" accept="image/jpeg, image/png, image/webp" className="hidden" onChange={handleFileChange} />
              {previewUrl ? (
                <img src={previewUrl} alt="Crop Preview" className="max-h-[300px] object-contain rounded-lg shadow-sm" />
              ) : (
                <>
                  <UploadCloud className="w-12 h-12 text-slate-400 mb-3" />
                  <p className="text-slate-500 font-medium">Click to upload leaf photo</p>
                  <p className="text-slate-400 text-sm mt-1">Supports JPG, PNG, WEBP</p>
                </>
              )}
            </label>

            <button 
              onClick={handleScan}
              disabled={!selectedFile || isLoading}
              className="w-full bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white font-semibold py-4 px-6 rounded-xl shadow-[0_4px_15px_rgba(16,185,129,0.3)] transition-all hover:-translate-y-1 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
            >
              {isLoading ? "🔬 Running AI Analysis..." : "🔬 Analyze Crop Data"}
            </button>
            {error && <p className="text-red-500 mt-4 text-center font-medium">❌ {error}</p>}
          </div>
        </div>

        {/* Right Panel */}
        <div className="h-full">
          {!result && !isLoading ? (
             <div className="empty-state">
               <div className="text-8xl mb-4 animate-bounce">🍃</div>
               <h2 className="text-3xl font-bold text-emerald-500 mb-2">Awaiting Data</h2>
               <p className="text-slate-500 text-lg">Upload a leaf image on the left side to begin diagnosis.</p>
             </div>
          ) : isLoading ? (
             <div className="empty-state">
               <div className="w-16 h-16 border-4 border-emerald-200 border-t-emerald-500 rounded-full animate-spin mb-6"></div>
               <h2 className="text-2xl font-bold text-emerald-600">Analyzing Cell Structure...</h2>
             </div>
          ) : (
             <div className="space-y-6">
                {/* 1. Diagnosis */}
                <div className={`glass-card border-l-8 ${result?.disease_name?.toLowerCase().includes('healthy') ? 'border-l-emerald-500' : 'border-l-red-500'}`}>
                  <h3 className="text-2xl font-bold flex items-center gap-3 mb-2">
                    <span className="text-3xl">{result?.disease_name?.toLowerCase().includes('healthy') ? '✅' : '⚠️'}</span>
                    {result?.disease_name || "Unknown"}
                  </h3>
                  <p className="text-slate-600 mb-4 font-medium">
                    Confidence: <b className="text-slate-900">{(result?.confidence || 0).toFixed(1)}%</b> AI Match
                  </p>
                  <div className="w-full bg-slate-200 rounded-full h-3">
                    <div className="bg-emerald-500 h-3 rounded-full" style={{ width: `${Math.min(result?.confidence || 0, 100)}%` }}></div>
                  </div>
                </div>

                {/* 2. Weather Context */}
                {result?.weather_context && (
                  <div className="glass-card">
                    <h4 className="text-xl font-bold mb-4 flex items-center gap-2">
                      <Cloud className="text-sky-500" /> Environment: {result.weather_context.city}
                    </h4>
                    <div className="grid grid-cols-3 gap-4 text-center">
                      <div className="bg-slate-50 p-4 rounded-xl border border-slate-100 flex flex-col items-center">
                        <Thermometer className="text-orange-500 mb-2" />
                        <span className="font-semibold text-lg">{result.weather_context.temperature}°C</span>
                      </div>
                      <div className="bg-slate-50 p-4 rounded-xl border border-slate-100 flex flex-col items-center">
                        <Droplets className="text-blue-500 mb-2" />
                        <span className="font-semibold text-lg">{result.weather_context.humidity}%</span>
                        <span className="text-slate-500 text-sm">Humidity</span>
                      </div>
                      <div className="bg-slate-50 p-4 rounded-xl border border-slate-100 flex flex-col items-center justify-center">
                         <span className="font-semibold capitalize text-slate-700">{result.weather_context.description}</span>
                      </div>
                    </div>
                  </div>
                )}

                {/* 3. Advice */}
                {result?.ai_advice && (
                  <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm">
                    <div className="bg-slate-50 p-4 border-b border-slate-200">
                      <h4 className="font-bold text-xl flex items-center justify-center gap-2 text-slate-800">
                        <FileText className="text-emerald-600" /> Expert Agronomist Report
                      </h4>
                    </div>
                    
                    {(() => {
                      const sections = parseAdvice(result.ai_advice);
                      return (
                        <div>
                          <div className="flex border-b border-slate-200">
                            {['English', 'Hindi', 'Gujarati'].map((lang) => (
                              <button
                                key={lang}
                                onClick={() => setActiveTab(lang)}
                                className={`flex-1 py-3 font-semibold transition-colors ${activeTab === lang ? 'bg-emerald-50 text-emerald-700 border-b-2 border-emerald-500' : 'text-slate-500 hover:bg-slate-50'}`}
                              >
                                {lang === 'English' ? '🇬🇧 English' : lang === 'Hindi' ? '🇮🇳 Hindi' : '🏛️ Gujarati'}
                              </button>
                            ))}
                          </div>
                          <div className="p-6 prose max-w-none text-slate-700">
                            <div className="whitespace-pre-wrap font-medium leading-relaxed">
                              {sections[activeTab] || "Advice not available in this language."}
                            </div>
                          </div>
                        </div>
                      );
                    })()}

                  </div>
                )}

             </div>
          )}
        </div>

      </div>

      {/* Footer */}
      <footer className="mt-16 border-t border-slate-200 pt-8 pb-6 text-center text-slate-500 text-sm">
        <div className="flex items-center justify-center gap-2 mb-2">
          <span className="text-emerald-500 text-xl">🌿</span>
          <span className="font-semibold text-slate-700 text-base">Krishi Scan</span>
        </div>
        <p className="mb-1">AI-powered plant disease detection & trilingual expert advice for Indian farmers 🇮🇳</p>
        <p className="text-xs text-slate-400">
          Built with <span className="text-emerald-500 font-medium">FastAPI</span> · <span className="text-blue-500 font-medium">React</span> · <span className="text-purple-500 font-medium">MobileNetV2</span> · <span className="text-orange-500 font-medium">Gemini AI</span>
        </p>
        <p className="text-xs text-slate-400 mt-2">© {new Date().getFullYear()} Krishi Scan · MIT License</p>
      </footer>
    </div>
  );
}

export default App;
