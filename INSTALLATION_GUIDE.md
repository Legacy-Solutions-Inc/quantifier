# RSB Combinator API - Installation Guide

## 🚀 Quick Fix for Python 3.12 Compatibility

The error you encountered is due to NumPy compilation issues with Python 3.12. Here are several solutions:

### Option 1: Use Pre-compiled Packages (Recommended)

```bash
# Install using the simple requirements file
pip install -r requirements-simple.txt
```

### Option 2: Install Individual Packages

```bash
# Install core packages one by one
pip install fastapi
pip install uvicorn[standard]
pip install python-multipart
pip install supabase
pip install sqlalchemy
pip install psycopg2-binary
pip install pandas
pip install numpy
pip install openpyxl
pip install python-jose[cryptography]
pip install passlib[bcrypt]
pip install python-dotenv
pip install Pillow
pip install httpx
```

### Option 3: Use Conda (Alternative)

If pip continues to fail, try using conda:

```bash
# Install conda if you don't have it
# Then create a new environment
conda create -n rsb-combinator python=3.11
conda activate rsb-combinator

# Install packages
conda install numpy pandas
pip install fastapi uvicorn supabase sqlalchemy
```

### Option 4: Use Python 3.11 (Most Reliable)

If you're still having issues, consider using Python 3.11:

```bash
# Install Python 3.11
# Then create a virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

## 🔧 Step-by-Step Setup

### 1. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Upgrade pip and setuptools

```bash
pip install --upgrade pip setuptools wheel
```

### 3. Install Dependencies

Try these options in order:

```bash
# Option A: Simple requirements
pip install -r requirements-simple.txt

# Option B: If that fails, install individually
pip install fastapi uvicorn python-multipart
pip install supabase sqlalchemy psycopg2-binary
pip install pandas numpy openpyxl
pip install python-jose[cryptography] passlib[bcrypt]
pip install python-dotenv Pillow httpx

# Option C: Use the setup script
python setup_api.py
```

### 4. Setup Environment Variables

```bash
# Copy environment template
cp env.example .env

# Edit .env file with your Supabase credentials
# You'll need to create a Supabase project first
```

### 5. Test Installation

```bash
# Try importing key packages
python -c "import fastapi, pandas, numpy, supabase; print('All packages installed successfully!')"
```

### 6. Run the API Server

```bash
cd api_server
python main.py
```

## 🐛 Troubleshooting

### Common Issues and Solutions

#### 1. NumPy Compilation Error
```bash
# Solution: Use pre-compiled NumPy
pip install --only-binary=all numpy
```

#### 2. psycopg2 Installation Error
```bash
# Solution: Use psycopg2-binary instead
pip install psycopg2-binary
```

#### 3. OpenPyXL Installation Error
```bash
# Solution: Install without dependencies first
pip install openpyxl --no-deps
pip install et-xmlfile
```

#### 4. Supabase Installation Error
```bash
# Solution: Install with specific version
pip install supabase==2.0.0
```

### Alternative Installation Methods

#### Using pip with --no-build-isolation
```bash
pip install --no-build-isolation -r requirements-simple.txt
```

#### Using pip with --prefer-binary
```bash
pip install --prefer-binary -r requirements-simple.txt
```

#### Using pip with --no-cache-dir
```bash
pip install --no-cache-dir -r requirements-simple.txt
```

## 🎯 Minimal Working Setup

If you want to get started quickly with minimal dependencies:

```bash
# Install only essential packages
pip install fastapi uvicorn python-multipart
pip install supabase
pip install pandas numpy
pip install python-dotenv

# Create a minimal .env file
echo "SUPABASE_URL=your_url_here" > .env
echo "SUPABASE_ANON_KEY=your_key_here" >> .env
echo "SUPABASE_SERVICE_ROLE_KEY=your_service_key_here" >> .env
```

## 🚀 Quick Start After Installation

1. **Setup Supabase:**
   - Go to [supabase.com](https://supabase.com)
   - Create a new project
   - Get your project URL and API keys
   - Update your `.env` file

2. **Run the API:**
   ```bash
   cd api_server
   python main.py
   ```

3. **Test the API:**
   - Visit `http://localhost:8000/docs`
   - Try the health check: `http://localhost:8000/health`

## 📞 Need Help?

If you're still having issues:

1. **Check Python version:** `python --version`
2. **Check pip version:** `pip --version`
3. **Try with Python 3.11:** Often more compatible
4. **Use conda:** Alternative package manager
5. **Check system dependencies:** Some packages need system libraries

The most reliable approach is usually to use Python 3.11 with a fresh virtual environment.
