# RSB Combinator API - Complete Deployment Guide

## 🎯 Overview

This guide will walk you through deploying your RSB Combinator API from development to production, including all the necessary setup steps.

## 📋 Prerequisites

Before starting, ensure you have:
- Python 3.8+ installed
- Git installed
- A Supabase account (free tier available)
- Basic understanding of web APIs

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Server    │    │   Supabase      │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (Database)   │
│   Port: 3000    │    │   Port: 8000    │    │   (Auth)        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Step 1: Local Development Setup

### 1.1 Install Dependencies

```bash
# Navigate to your project
cd "D:\CE Client\RSB-Quantifier"

# Install Python dependencies
pip install -r requirements-simple.txt

# Or install individually if needed
pip install fastapi uvicorn python-multipart supabase pandas numpy openpyxl python-dotenv
```

### 1.2 Test Local API

```bash
# Start the API server
cd api_server
python simple_main.py
```

**Test endpoints:**
- `http://localhost:8000/` - Root endpoint
- `http://localhost:8000/docs` - API documentation
- `http://localhost:8000/health` - Health check

## 🗄️ Step 2: Supabase Setup

### 2.1 Create Supabase Project

1. **Go to [supabase.com](https://supabase.com)**
2. **Click "Start your project"**
3. **Sign up/Login with GitHub**
4. **Click "New Project"**
5. **Fill in project details:**
   - Name: `rsb-combinator`
   - Database Password: (choose a strong password)
   - Region: Choose closest to your users
6. **Click "Create new project"**
7. **Wait for setup to complete (2-3 minutes)**

### 2.2 Get Supabase Credentials

1. **Go to Settings → API**
2. **Copy these values:**
   - **Project URL** (looks like: `https://xyz.supabase.co`)
   - **Anon public key** (starts with `eyJ...`)
   - **Service role key** (starts with `eyJ...`)

### 2.3 Update Your .env File

Edit your `.env` file in `D:\CE Client\RSB-Quantifier\.env`:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=True

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,https://your-domain.com
```

### 2.4 Setup Database Tables

1. **Go to Supabase Dashboard → SQL Editor**
2. **Run this SQL to create tables:**

```sql
-- Enable Row Level Security
ALTER TABLE auth.users ENABLE ROW LEVEL SECURITY;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create projects table
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create calculations table
CREATE TABLE IF NOT EXISTS calculations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    status TEXT DEFAULT 'pending',
    input_data JSONB,
    results JSONB,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Create project_files table
CREATE TABLE IF NOT EXISTS project_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    content_type TEXT NOT NULL,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create calculation_results table
CREATE TABLE IF NOT EXISTS calculation_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    calculation_id UUID REFERENCES calculations(id) ON DELETE CASCADE,
    diameter FLOAT NOT NULL,
    quantity INTEGER NOT NULL,
    combination JSONB NOT NULL,
    lengths JSONB NOT NULL,
    combined_length FLOAT NOT NULL,
    target FLOAT NOT NULL,
    waste FLOAT NOT NULL,
    remaining_pieces JSONB NOT NULL
);

-- Create export_history table
CREATE TABLE IF NOT EXISTS export_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    calculation_id UUID REFERENCES calculations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    filename TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    format TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE calculations ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE calculation_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE export_history ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY "Users can view own data" ON users FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own data" ON users FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can view own projects" ON projects FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create projects" ON projects FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own projects" ON projects FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own projects" ON projects FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "Users can view own calculations" ON calculations FOR SELECT USING (
    EXISTS (SELECT 1 FROM projects WHERE projects.id = calculations.project_id AND projects.user_id = auth.uid())
);
CREATE POLICY "Users can create calculations" ON calculations FOR INSERT WITH CHECK (
    EXISTS (SELECT 1 FROM projects WHERE projects.id = calculations.project_id AND projects.user_id = auth.uid())
);
CREATE POLICY "Users can update own calculations" ON calculations FOR UPDATE USING (
    EXISTS (SELECT 1 FROM projects WHERE projects.id = calculations.project_id AND projects.user_id = auth.uid())
);
CREATE POLICY "Users can delete own calculations" ON calculations FOR DELETE USING (
    EXISTS (SELECT 1 FROM projects WHERE projects.id = calculations.project_id AND projects.user_id = auth.uid())
);

-- Similar policies for other tables...
```

### 2.5 Setup Storage Buckets

1. **Go to Storage → Buckets**
2. **Create bucket: `files`**
   - Public: No
   - File size limit: 10MB
3. **Create bucket: `exports`**
   - Public: No
   - File size limit: 50MB

## 🌐 Step 3: Deployment Options

### Option A: Railway (Recommended for beginners)

#### 3.1 Setup Railway Account

1. **Go to [railway.app](https://railway.app)**
2. **Sign up with GitHub**
3. **Connect your GitHub repository**

#### 3.2 Deploy to Railway

1. **Create new project on Railway**
2. **Connect your GitHub repo**
3. **Add environment variables:**
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_ANON_KEY=your_anon_key
   SUPABASE_SERVICE_ROLE_KEY=your_service_key
   ```
4. **Railway will auto-deploy**

#### 3.3 Railway Configuration

Create `railway.json` in your project root:

```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "cd api_server && python simple_main.py",
    "healthcheckPath": "/health"
  }
}
```

### Option B: Heroku

#### 3.1 Setup Heroku

```bash
# Install Heroku CLI
# Download from: https://devcenter.heroku.com/articles/heroku-cli

# Login to Heroku
heroku login

# Create Heroku app
heroku create rsb-combinator-api

# Set environment variables
heroku config:set SUPABASE_URL=your_supabase_url
heroku config:set SUPABASE_ANON_KEY=your_anon_key
heroku config:set SUPABASE_SERVICE_ROLE_KEY=your_service_key
```

#### 3.2 Create Heroku Files

Create `Procfile` in your project root:

```
web: cd api_server && python simple_main.py
```

Create `runtime.txt`:

```
python-3.11.6
```

#### 3.3 Deploy to Heroku

```bash
# Add Heroku remote
git remote add heroku https://git.heroku.com/rsb-combinator-api.git

# Deploy
git push heroku main
```

### Option C: DigitalOcean App Platform

#### 3.1 Setup DigitalOcean

1. **Go to [cloud.digitalocean.com](https://cloud.digitalocean.com)**
2. **Create new App**
3. **Connect GitHub repository**
4. **Configure app settings:**
   - Source: GitHub repo
   - Build command: `pip install -r requirements-simple.txt`
   - Run command: `cd api_server && python simple_main.py`
   - Port: 8000

#### 3.2 Environment Variables

Add these in DigitalOcean dashboard:
```
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_key
```

### Option D: VPS Deployment (Advanced)

#### 3.1 Setup VPS

```bash
# Connect to your VPS
ssh user@your-server-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv nginx -y

# Create project directory
mkdir -p /var/www/rsb-combinator
cd /var/www/rsb-combinator

# Clone your repository
git clone https://github.com/yourusername/rsb-combinator.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements-simple.txt
```

#### 3.2 Setup Systemd Service

Create `/etc/systemd/system/rsb-combinator.service`:

```ini
[Unit]
Description=RSB Combinator API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/rsb-combinator/api_server
Environment=PATH=/var/www/rsb-combinator/venv/bin
ExecStart=/var/www/rsb-combinator/venv/bin/python simple_main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 3.3 Setup Nginx

Create `/etc/nginx/sites-available/rsb-combinator`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 3.4 Enable and Start Services

```bash
# Enable and start service
sudo systemctl enable rsb-combinator
sudo systemctl start rsb-combinator

# Enable and start nginx
sudo systemctl enable nginx
sudo systemctl start nginx

# Enable site
sudo ln -s /etc/nginx/sites-available/rsb-combinator /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🔧 Step 4: Production Configuration

### 4.1 Environment Variables for Production

```bash
# Production .env
SUPABASE_URL=your_production_supabase_url
SUPABASE_ANON_KEY=your_production_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_production_service_key

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=False

# CORS Configuration
CORS_ORIGINS=https://your-frontend-domain.com,https://your-production-domain.com

# Security
JWT_SECRET_KEY=your_very_secure_jwt_secret_key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# File Storage
MAX_FILE_SIZE=10485760
ALLOWED_FILE_TYPES=xlsx,xls,csv

# Export Configuration
EXPORT_EXPIRY_HOURS=24
MAX_EXPORT_SIZE=52428800

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/rsb-combinator/api.log
```

### 4.2 Security Considerations

1. **Use HTTPS in production**
2. **Set up proper CORS origins**
3. **Use strong JWT secrets**
4. **Enable Supabase RLS policies**
5. **Regular security updates**

### 4.3 Monitoring and Logging

```bash
# Install monitoring tools
pip install sentry-sdk

# Add to your main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your_sentry_dsn",
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
)
```

## 🧪 Step 5: Testing Your Deployment

### 5.1 Health Checks

```bash
# Test your deployed API
curl https://your-api-domain.com/health

# Expected response:
{
  "status": "healthy",
  "service": "rsb-combinator-api",
  "environment": "production"
}
```

### 5.2 API Documentation

Visit: `https://your-api-domain.com/docs`

### 5.3 Test Endpoints

```bash
# Test root endpoint
curl https://your-api-domain.com/

# Test calculation endpoint
curl -X POST https://your-api-domain.com/api/calculate \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

## 🚀 Step 6: Frontend Integration

### 6.1 Next.js Frontend Setup

```bash
# Create Next.js app
npx create-next-app@latest frontend --typescript --tailwind --app

# Install Supabase client
npm install @supabase/supabase-js

# Install additional dependencies
npm install @tanstack/react-query zustand
```

### 6.2 Frontend Configuration

Create `frontend/.env.local`:

```bash
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

### 6.3 API Client Setup

Create `frontend/lib/api.ts`:

```typescript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseKey)

export const apiClient = {
  async request(endpoint: string, options: RequestInit = {}) {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    })
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`)
    }
    
    return response.json()
  },
  
  async get(endpoint: string) {
    return this.request(endpoint)
  },
  
  async post(endpoint: string, data: any) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }
}
```

## 📊 Step 7: Monitoring and Maintenance

### 7.1 Health Monitoring

```bash
# Create health check script
#!/bin/bash
# health_check.sh

API_URL="https://your-api-domain.com"

# Check health endpoint
response=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/health")

if [ $response -eq 200 ]; then
    echo "✅ API is healthy"
    exit 0
else
    echo "❌ API is down (HTTP $response)"
    exit 1
fi
```

### 7.2 Log Monitoring

```bash
# View logs (if using systemd)
sudo journalctl -u rsb-combinator -f

# View nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 7.3 Backup Strategy

```bash
# Backup Supabase database
# Go to Supabase Dashboard → Settings → Database
# Click "Download backup" or use pg_dump

# Backup application files
tar -czf rsb-combinator-backup-$(date +%Y%m%d).tar.gz /var/www/rsb-combinator/
```

## 🔄 Step 8: CI/CD Pipeline

### 8.1 GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements-simple.txt
    
    - name: Run tests
      run: |
        python -m pytest tests/
    
    - name: Deploy to Railway
      uses: railway-app/railway-deploy@v1
      with:
        railway-token: ${{ secrets.RAILWAY_TOKEN }}
```

## 🎯 Summary

Your RSB Combinator API is now deployed! Here's what you have:

### ✅ **What's Working:**
- **API Server**: FastAPI with all endpoints
- **Database**: Supabase with proper tables and security
- **Authentication**: Supabase Auth integration
- **File Storage**: Supabase Storage for files
- **Documentation**: Auto-generated API docs
- **Monitoring**: Health checks and logging

### 🚀 **Next Steps:**
1. **Test your deployed API**
2. **Build the Next.js frontend**
3. **Connect frontend to API**
4. **Add more features**
5. **Scale as needed**

### 📞 **Support:**
- **API Docs**: `https://your-domain.com/docs`
- **Health Check**: `https://your-domain.com/health`
- **Supabase Dashboard**: Monitor database and auth
- **Deployment Platform**: Monitor server health

Your RSB Combinator is now a fully functional web service! 🎉
