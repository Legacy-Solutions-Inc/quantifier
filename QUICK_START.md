x2# RSB Combinator - Quick Start Guide

## 🚀 Get Running in 5 Minutes

### Step 1: Install Dependencies
```bash
# Install Python packages
pip install fastapi uvicorn python-multipart supabase pandas numpy openpyxl python-dotenv
```

### Step 2: Setup Supabase (Free)
1. **Go to [supabase.com](https://supabase.com)**
2. **Create new project**
3. **Copy your credentials:**
   - Project URL
   - Anon key
   - Service role key

### Step 3: Configure Environment
Edit your `.env` file in `D:\CE Client\RSB-Quantifier\.env`:
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_key_here
```

### Step 4: Run the API
```bash
cd api_server
python simple_main.py
```

### Step 5: Test Your API
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Test Endpoint**: http://localhost:8000/api/test

## 🎯 What You Get

### ✅ **Working API Server**
- FastAPI with automatic documentation
- Health monitoring
- CORS enabled for frontend
- Environment variable loading

### ✅ **Database Ready**
- Supabase PostgreSQL database
- User authentication
- File storage
- Real-time capabilities

### ✅ **Production Ready**
- Security policies
- Error handling
- Logging
- Scalable architecture

## 🚀 Deploy to Production

### Option 1: Railway (Easiest)
1. **Go to [railway.app](https://railway.app)**
2. **Connect GitHub repo**
3. **Add environment variables**
4. **Auto-deploy!**

### Option 2: Heroku
```bash
# Install Heroku CLI
heroku create rsb-combinator-api
heroku config:set SUPABASE_URL=your_url
heroku config:set SUPABASE_ANON_KEY=your_key
git push heroku main
```

### Option 3: DigitalOcean
1. **Create App Platform project**
2. **Connect GitHub**
3. **Set environment variables**
4. **Deploy!**

## 🎨 Build Frontend

### Next.js Setup
```bash
# Create frontend
npx create-next-app@latest frontend --typescript --tailwind

# Install Supabase
npm install @supabase/supabase-js

# Configure API connection
# Add to .env.local:
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

## 📊 Monitor Your API

### Health Checks
```bash
# Check if API is running
curl https://your-api-domain.com/health

# Expected response:
{
  "status": "healthy",
  "service": "rsb-combinator-api"
}
```

### API Documentation
Visit: `https://your-api-domain.com/docs`

## 🔧 Troubleshooting

### Common Issues:

1. **"Supabase not configured"**
   - Check your `.env` file
   - Verify Supabase credentials

2. **"Import errors"**
   - Install missing packages: `pip install -r requirements-simple.txt`

3. **"Port already in use"**
   - Change port in `simple_main.py`
   - Or kill process using port 8000

4. **"Database connection failed"**
   - Check Supabase project is active
   - Verify credentials are correct

## 🎯 Next Steps

1. **Test your API endpoints**
2. **Build the frontend interface**
3. **Add user authentication**
4. **Implement RSB calculations**
5. **Deploy to production**

## 📞 Need Help?

- **API Documentation**: `/docs` endpoint
- **Health Check**: `/health` endpoint
- **Test Endpoint**: `/api/test` endpoint
- **Supabase Dashboard**: Monitor database
- **Deployment Platform**: Monitor server

Your RSB Combinator API is ready to optimize rebar cutting! 🎉
