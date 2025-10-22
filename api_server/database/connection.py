"""
Database connection and configuration for Supabase
"""

import os
from supabase import create_client, Client
from typing import Optional
import asyncio
from contextlib import asynccontextmanager

class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL", "https://placeholder.supabase.co")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY", "placeholder_key")
        self.supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "placeholder_service_key")
        
        # Check if using placeholder values
        if "placeholder" in self.supabase_url or "placeholder" in self.supabase_key:
            print("⚠️  Warning: Supabase credentials not configured. Using placeholder values.")
            print("   Please set SUPABASE_URL and SUPABASE_ANON_KEY in your .env file")
            print("   The API will start but database operations will fail.")
        
        self.client: Optional[Client] = None
        self.service_client: Optional[Client] = None
        
    def get_client(self) -> Client:
        """Get regular Supabase client"""
        if not self.client:
            self.client = create_client(self.supabase_url, self.supabase_key)
        return self.client
    
    def get_service_client(self) -> Client:
        """Get service role Supabase client for admin operations"""
        if not self.service_client:
            if not self.supabase_service_key or "placeholder" in self.supabase_service_key:
                raise ValueError("Service role key required for admin operations")
            self.service_client = create_client(self.supabase_url, self.supabase_service_key)
        return self.service_client

# Global database manager instance
db_manager = DatabaseManager()

def get_db() -> Client:
    """Dependency to get database client"""
    return db_manager.get_client()

def get_service_db() -> Client:
    """Dependency to get service role database client"""
    return db_manager.get_service_client()

# Database initialization
async def init_database():
    """Initialize database tables and relationships"""
    try:
        service_db = get_service_db()
        
        # Check if tables exist and create if needed
        # This would typically be handled by Supabase migrations
        # but we can add some initialization logic here
        
        print("✅ Database connection initialized")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

# Connection health check
async def check_database_health() -> bool:
    """Check if database connection is healthy"""
    try:
        db = get_db()
        # Simple query to test connection
        result = db.table("users").select("id").limit(1).execute()
        return True
    except Exception as e:
        print(f"Database health check failed: {e}")
        return False
