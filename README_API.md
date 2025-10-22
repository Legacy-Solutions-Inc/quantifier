# RSB Combinator Web API

A FastAPI-based web service that provides REST API endpoints for the RSB (Reinforcement Steel Bar) Combinator optimization system.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Supabase account and project
- Node.js 18+ (for Next.js frontend)

### Installation

1. **Clone and setup the repository:**
   ```bash
   git clone <your-repo-url>
   cd RSB-Quantifier
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your Supabase credentials
   ```

4. **Run the API server:**
   ```bash
   cd api_server
   python main.py
   ```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Core Endpoints

#### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user info

#### Projects
- `GET /api/projects/` - List user projects
- `POST /api/projects/` - Create new project
- `GET /api/projects/{id}` - Get project details
- `PUT /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project

#### Calculations
- `POST /api/calculations/` - Create new calculation
- `GET /api/calculations/{id}` - Get calculation results
- `GET /api/calculations/` - List calculations
- `DELETE /api/calculations/{id}` - Delete calculation

#### File Management
- `POST /api/files/upload` - Upload Excel/CSV files
- `POST /api/files/validate` - Validate file structure
- `GET /api/files/{id}/download` - Download file
- `GET /api/files/` - List user files

## 🏗️ Architecture

### Backend Stack
- **FastAPI**: Modern, fast web framework
- **Supabase**: Database, authentication, and storage
- **Pandas/NumPy**: Data processing
- **OpenPyXL**: Excel file handling

### Database Schema

#### Core Tables
- `users` - User accounts
- `projects` - Project organization
- `calculations` - Optimization calculations
- `rebar_data` - Input rebar specifications
- `calculation_results` - Optimization results
- `project_files` - File attachments
- `export_history` - Export tracking

### API Structure
```
api_server/
├── main.py                 # FastAPI application
├── routers/               # API route handlers
│   ├── auth.py           # Authentication endpoints
│   ├── projects.py       # Project management
│   ├── calculations.py   # RSB optimization
│   └── files.py          # File operations
├── services/             # Business logic
│   ├── combinator_service.py    # RSB optimization engine
│   ├── calculation_service.py   # Calculation management
│   ├── project_service.py       # Project operations
│   ├── file_service.py         # File handling
│   └── export_service.py       # Export operations
├── models/               # Data models
│   └── schemas.py        # Pydantic schemas
├── database/             # Database layer
│   ├── connection.py     # Supabase connection
│   └── models.py         # SQLAlchemy models
└── auth/                 # Authentication
    └── supabase_auth.py  # Supabase auth integration
```

## 🔧 Configuration

### Environment Variables

```bash
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=True

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,https://your-frontend-domain.com
```

### Supabase Setup

1. **Create Supabase Project:**
   - Go to [supabase.com](https://supabase.com)
   - Create new project
   - Get your project URL and API keys

2. **Setup Database Tables:**
   ```sql
   -- Run the SQL from database/schema.sql in your Supabase SQL editor
   ```

3. **Configure Storage:**
   - Create storage buckets: `files`, `exports`
   - Set up RLS policies for user access

## 🚀 Deployment

### Development
```bash
cd api_server
python main.py
```

### Production
```bash
# Using Gunicorn
gunicorn api_server.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Using Docker
docker build -t rsb-combinator-api .
docker run -p 8000:8000 rsb-combinator-api
```

## 📊 API Usage Examples

### 1. User Registration
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "name": "John Doe"
  }'
```

### 2. Create Project
```bash
curl -X POST "http://localhost:8000/api/projects/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Building A Rebar Optimization",
    "description": "Optimize rebar cutting for Building A construction"
  }'
```

### 3. Upload File
```bash
curl -X POST "http://localhost:8000/api/files/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@rebar_data.xlsx" \
  -F "project_id=PROJECT_ID"
```

### 4. Run Calculation
```bash
curl -X POST "http://localhost:8000/api/calculations/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "PROJECT_ID",
    "target_lengths": [12, 10.5, 9, 7.5],
    "rebar_data": [
      {
        "length": 12.0,
        "pieces": 100,
        "diameter": 16.0
      }
    ],
    "tolerance": 0.1
  }'
```

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Row Level Security**: Database-level access control
- **File Validation**: Strict file type and content validation
- **Rate Limiting**: API request rate limiting
- **CORS Protection**: Configurable cross-origin policies

## 📈 Performance Features

- **Async Processing**: Non-blocking calculation processing
- **Background Tasks**: Heavy operations run in background
- **File Streaming**: Efficient file upload/download
- **Database Optimization**: Indexed queries and connection pooling
- **Caching**: Redis caching for frequently accessed data

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=api_server

# Run specific test file
pytest tests/test_calculations.py
```

## 📝 API Response Examples

### Successful Calculation Response
```json
{
  "id": "calc_123",
  "project_id": "proj_456",
  "status": "completed",
  "results": {
    "16.0": {
      "diameter": 16.0,
      "results": [
        {
          "quantity": 5,
          "combination": [2, 1, 0],
          "lengths": [6.0, 4.0, 3.0],
          "combined_length": 10.0,
          "target": 10.0,
          "waste": 0.0,
          "remaining_pieces": [90, 95, 100]
        }
      ],
      "total_waste_percentage": 2.5,
      "total_utilized_weight": 1250.5,
      "total_commercial_weight": 1281.8,
      "total_waste_weight": 31.3
    }
  },
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:30:05Z"
}
```

## 🚀 Next Steps

1. **Frontend Integration**: Connect with Next.js frontend
2. **Real-time Updates**: WebSocket support for live calculation updates
3. **Advanced Analytics**: Detailed waste analysis and reporting
4. **Mobile App**: React Native mobile application
5. **Enterprise Features**: Multi-tenant support, advanced permissions

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
