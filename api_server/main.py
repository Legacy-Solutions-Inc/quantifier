"""
FastAPI server for RSB Combinator Web API
Main entry point for the web application
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn
import os
from typing import List, Optional
import pandas as pd
import json
from pathlib import Path

# Load environment variables from .env file in parent directory
parent_dir = Path(__file__).parent.parent
env_file = parent_dir / ".env"
if env_file.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(env_file)
        print(f"✅ Loaded environment from {env_file}")
    except ImportError:
        print("⚠️  python-dotenv not installed, loading environment manually")
        # Manual .env loading
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print(f"✅ Loaded environment from {env_file}")
else:
    print(f"⚠️  .env file not found at {env_file}")
    print("   Using default/placeholder values")

# Import our core modules
import sys
sys.path.append(str(parent_dir))
from src.core.combinator import Combinator, CombinatorConfig, CombinationResult
from src.core.combinator_manager import CombinatorManager
from src.core.stockpile import StockpileManager

# Import API modules
try:
    from api_server.routers import auth, projects, calculations, files
    from api_server.database import get_db
    from api_server.models import schemas
    from api_server.auth.supabase_auth import verify_token
except ImportError as e:
    print(f"⚠️  Import error: {e}")
    print("   Some API modules may not be available")
    # Create dummy modules to prevent crashes
    class DummyRouter:
        router = None
    auth = DummyRouter()
    projects = DummyRouter()
    calculations = DummyRouter()
    files = DummyRouter()

# Initialize FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 RSB Combinator API Server Starting...")
    yield
    # Shutdown
    print("🛑 RSB Combinator API Server Shutting down...")

app = FastAPI(
    title="RSB Combinator API",
    description="Web API for RSB (Reinforcement Steel Bar) cutting optimization",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
try:
    if hasattr(auth, 'router') and auth.router:
        app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
    if hasattr(projects, 'router') and projects.router:
        app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
    if hasattr(calculations, 'router') and calculations.router:
        app.include_router(calculations.router, prefix="/api/calculations", tags=["Calculations"])
    if hasattr(files, 'router') and files.router:
        app.include_router(files.router, prefix="/api/files", tags=["File Management"])
except Exception as e:
    print(f"⚠️  Router inclusion error: {e}")
    print("   API will start with basic endpoints only")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "RSB Combinator API Server",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "rsb-combinator-api"}

# Dependency for authentication
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    try:
        token = credentials.credentials
        user = await verify_token(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
