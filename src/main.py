"""
Main FastAPI application for the Intelligent Entrepreneurial Orientation Engine
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes.diagnostic import router as diagnostic_router
from src.api.routes.scoring import router as scoring_router
from src.api.routes.roadmap import router as roadmap_router

# Create FastAPI app
app = FastAPI(
    title="Intelligent Entrepreneurial Orientation Engine",
    description="AI-powered system for entrepreneurial assessment and guidance",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(diagnostic_router)
app.include_router(scoring_router)
app.include_router(roadmap_router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Intelligent Entrepreneurial Orientation Engine API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}