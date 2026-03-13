from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import predict, weather

app = FastAPI(
    title="Krishi Scan API",
    description="AI Plant Disease Detection & Consulting API",
    version="1.0.0"
)

# Allow Streamlit frontend to communicate with backend
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

@app.get("/")
async def root():
    return {"message": "Welcome to Krishi Scan API"}
