#!/usr/bin/env python3
"""
Setup script for RSB Combinator API
Handles dependency installation and environment setup
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing dependencies...")
    
    # Try the main requirements first
    if run_command("pip install -r requirements.txt", "Installing main requirements"):
        return True
    
    # If that fails, try the Python 3.12 specific requirements
    print("🔄 Trying Python 3.12 compatible requirements...")
    if run_command("pip install -r requirements-py312.txt", "Installing Python 3.12 compatible requirements"):
        return True
    
    # If both fail, try installing packages individually
    print("🔄 Installing packages individually...")
    packages = [
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "python-multipart>=0.0.6",
        "supabase>=2.0.0",
        "sqlalchemy>=2.0.0",
        "psycopg2-binary>=2.9.0",
        "pandas>=2.1.0",
        "numpy>=1.26.0",
        "openpyxl>=3.1.0",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.0",
        "python-dotenv>=1.0.0",
        "Pillow>=10.0.0",
        "httpx>=0.25.0"
    ]
    
    for package in packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            print(f"⚠️  Warning: Failed to install {package}")
    
    return True

def create_env_file():
    """Create .env file from template"""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if env_example.exists():
        print("📝 Creating .env file from template...")
        try:
            with open(env_example, 'r') as src, open(env_file, 'w') as dst:
                dst.write(src.read())
            print("✅ .env file created successfully")
            print("⚠️  Please edit .env file with your Supabase credentials")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    else:
        print("⚠️  env.example file not found, creating basic .env file...")
        try:
            with open(env_file, 'w') as f:
                f.write("""# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=True

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,https://your-frontend-domain.com
""")
            print("✅ Basic .env file created")
            print("⚠️  Please edit .env file with your Supabase credentials")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False

def check_api_structure():
    """Check if API structure is correct"""
    required_files = [
        "api_server/main.py",
        "api_server/routers/auth.py",
        "api_server/routers/calculations.py",
        "api_server/routers/projects.py",
        "api_server/routers/files.py",
        "api_server/models/schemas.py",
        "api_server/database/connection.py",
        "api_server/services/combinator_service.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    print("✅ API structure is correct")
    return True

def main():
    """Main setup function"""
    print("🚀 RSB Combinator API Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check API structure
    if not check_api_structure():
        print("\n❌ API structure is incomplete. Please ensure all files are present.")
        return False
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Failed to install dependencies")
        return False
    
    # Create .env file
    create_env_file()
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your Supabase credentials")
    print("2. Setup Supabase project and database")
    print("3. Run the API server: python api_server/main.py")
    print("4. Visit http://localhost:8000/docs for API documentation")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
