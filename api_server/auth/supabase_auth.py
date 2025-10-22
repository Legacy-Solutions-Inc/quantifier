"""
Supabase authentication integration
"""

import os
from typing import Optional, Dict, Any
from supabase import Client
from fastapi import HTTPException, status
import jwt
from datetime import datetime, timedelta
import asyncio

class SupabaseAuth:
    """Handles Supabase authentication operations"""
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify JWT token and return user information
        
        Args:
            token: JWT token to verify
            
        Returns:
            User information if token is valid, None otherwise
        """
        try:
            # Use Supabase's built-in token verification
            response = self.client.auth.get_user(token)
            
            if response.user:
                return {
                    "id": response.user.id,
                    "email": response.user.email,
                    "name": response.user.user_metadata.get("name"),
                    "created_at": response.user.created_at,
                    "updated_at": response.user.updated_at
                }
            return None
            
        except Exception as e:
            print(f"Token verification failed: {e}")
            return None
    
    async def sign_up(self, email: str, password: str, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Sign up a new user
        
        Args:
            email: User email
            password: User password
            name: Optional user name
            
        Returns:
            User information and session data
        """
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "name": name
                    }
                }
            })
            
            if response.user:
                return {
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "name": response.user.user_metadata.get("name"),
                        "created_at": response.user.created_at
                    },
                    "session": response.session
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create user"
                )
                
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Sign up failed: {str(e)}"
            )
    
    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """
        Sign in an existing user
        
        Args:
            email: User email
            password: User password
            
        Returns:
            User information and session data
        """
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user and response.session:
                return {
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "name": response.user.user_metadata.get("name"),
                        "created_at": response.user.created_at
                    },
                    "session": response.session
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
                
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Sign in failed: {str(e)}"
            )
    
    async def sign_out(self, token: str) -> bool:
        """
        Sign out user
        
        Args:
            token: User session token
            
        Returns:
            True if successful
        """
        try:
            self.client.auth.sign_out()
            return True
        except Exception as e:
            print(f"Sign out failed: {e}")
            return False
    
    async def reset_password(self, email: str) -> bool:
        """
        Send password reset email
        
        Args:
            email: User email
            
        Returns:
            True if email sent successfully
        """
        try:
            self.client.auth.reset_password_email(email)
            return True
        except Exception as e:
            print(f"Password reset failed: {e}")
            return False
    
    async def update_user_profile(self, token: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user profile
        
        Args:
            token: User session token
            updates: Profile updates
            
        Returns:
            Updated user information
        """
        try:
            response = self.client.auth.update_user({
                "data": updates
            })
            
            if response.user:
                return {
                    "id": response.user.id,
                    "email": response.user.email,
                    "name": response.user.user_metadata.get("name"),
                    "updated_at": response.user.updated_at
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to update profile"
                )
                
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Profile update failed: {str(e)}"
            )

# Global auth instance
_auth_instance: Optional[SupabaseAuth] = None

def get_auth() -> SupabaseAuth:
    """Get authentication instance"""
    global _auth_instance
    if not _auth_instance:
        from api_server.database.connection import get_db
        db = get_db()
        _auth_instance = SupabaseAuth(db)
    return _auth_instance

async def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify token and return user info"""
    auth = get_auth()
    return await auth.verify_token(token)
