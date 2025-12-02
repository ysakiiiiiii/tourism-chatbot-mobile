from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.config import API_TITLE, API_VERSION, API_DESCRIPTION
from app.database import init_db
from app.routes import chatbot, spots, cuisine, location
from app.services.excel_to_prolog import convert_excel_to_prolog
from app.services.prolog_service import get_prolog_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print("🚀 Starting Ilocos Tourism Chatbot API...")
    
    # Initialize database
    await init_db()
    print("✓ Database initialized")
    
    # Convert Excel to Prolog
    try:
        convert_excel_to_prolog()
        print("✓ Prolog KB generated")
    except Exception as e:
        print(f"⚠ Warning: Could not generate Prolog KB: {e}")
    
    # Initialize Prolog service
    try:
        get_prolog_service()
        print("✓ Prolog service initialized")
    except Exception as e:
        print(f"⚠ Warning: Could not initialize Prolog service: {e}")
    
    print("✓ API ready!")
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")

# Create FastAPI app
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chatbot.router)
app.include_router(spots.router)
app.include_router(cuisine.router)
app.include_router(location.router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Ilocos Tourism Chatbot API",
        "version": API_VERSION,
        "endpoints": {
            "chat": "/api/chat",
            "tourist_spots": "/api/spots",
            "cuisine": "/api/cuisine",
            "location": "/api/location",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)