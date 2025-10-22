#!/usr/bin/env python3
"""
Run script for RSB Combinator API
Handles environment setup and starts the server
"""

import os
import sys
from pathlib import Path

def main():
    """Main startup function"""
    print("🚀 Starting RSB Combinator API Server")
    print("=" * 40)
    
    # Check if .env file exists in parent directory
    parent_dir = Path(__file__).parent.parent
    env_file = parent_dir / ".env"
    
    if env_file.exists():
        print(f"✅ Found .env file at {env_file}")
    else:
        print(f"⚠️  .env file not found at {env_file}")
        print("   Please create a .env file with your Supabase credentials")
        print("   Example content:")
        print("   SUPABASE_URL=your_supabase_project_url")
        print("   SUPABASE_ANON_KEY=your_supabase_anon_key")
        print("   SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key")
        return False
    
    # Import and run the main application
    try:
        print("\n🔄 Starting FastAPI server...")
        
        # Try the simple version first
        try:
            from simple_main import app
            print("✅ Using simplified API server")
        except ImportError:
            from main import app
            print("✅ Using full API server")
        
        import uvicorn
        
        print("🌐 Server will be available at: http://localhost:8000")
        print("📚 API Documentation: http://localhost:8000/docs")
        print("🔍 Health Check: http://localhost:8000/health")
        print("🧪 Test Endpoint: http://localhost:8000/api/test")
        
        # Start the server
        uvicorn.run(
            "simple_main:app" if 'simple_main' in locals() else "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed:")
        print("pip install -r requirements-simple.txt")
        return False
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
