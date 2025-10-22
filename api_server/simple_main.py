"""
Simplified FastAPI server for RSB Combinator Web API
Basic version without complex dependencies
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
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

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "RSB Combinator API Server",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running",
        "environment": {
            "supabase_configured": "placeholder" not in os.getenv("SUPABASE_URL", ""),
            "supabase_url": os.getenv("SUPABASE_URL", "Not configured")[:50] + "..." if len(os.getenv("SUPABASE_URL", "")) > 50 else os.getenv("SUPABASE_URL", "Not configured")
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    return {
        "status": "healthy", 
        "service": "rsb-combinator-api",
        "environment": "production",
        "port": os.getenv("PORT", 8000),
        "host": "0.0.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "RSB Combinator API Server",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running",
        "health": "/health",
        "environment": {
            "supabase_configured": "placeholder" not in os.getenv("SUPABASE_URL", ""),
            "supabase_url": os.getenv("SUPABASE_URL", "Not configured")[:50] + "..." if len(os.getenv("SUPABASE_URL", "")) > 50 else os.getenv("SUPABASE_URL", "Not configured"),
            "port": os.getenv("PORT", 8000)
        }
    }

@app.get("/api/test")
async def test_endpoint():
    """Test endpoint to verify API is working"""
    return {
        "message": "API is working!",
        "timestamp": "2024-01-01T00:00:00Z",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "root": "/"
        }
    }

# Basic RSB calculation endpoint (without database)
@app.post("/api/calculate")
async def calculate_rsb(data: dict):
    """Basic RSB calculation endpoint"""
    try:
        # This is a placeholder - you can implement basic calculation here
        return {
            "message": "Calculation endpoint received data",
            "received_data": data,
            "note": "This is a basic endpoint. Full calculation requires database setup."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")

if __name__ == "__main__":
    # Get port from environment variable (Railway provides this)
    port = int(os.getenv("PORT", 8000))
    
    print("🌐 Starting RSB Combinator API Server...")
    print(f"📚 API Documentation: http://0.0.0.0:{port}/docs")
    print(f"🔍 Health Check: http://0.0.0.0:{port}/health")
    print(f"🧪 Test Endpoint: http://0.0.0.0:{port}/api/test")
    
    uvicorn.run(
        "simple_main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    )
