"""
Authentication router for user management
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, Any

from api_server.models.schemas import (
    LoginRequest, RegisterRequest, UserResponse, BaseResponse, ErrorResponse
)
from api_server.auth.supabase_auth import get_auth
from api_server.database.connection import get_db

router = APIRouter()

@router.post("/register", response_model=Dict[str, Any])
async def register_user(
    request: RegisterRequest,
    db = Depends(get_db)
):
    """
    Register a new user
    
    Creates a new user account with email and password authentication.
    """
    try:
        auth = get_auth()
        
        # Register user with Supabase
        result = await auth.sign_up(
            email=request.email,
            password=request.password,
            name=request.name
        )
        
        return {
            "success": True,
            "message": "User registered successfully",
            "user": result["user"],
            "session": result["session"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=Dict[str, Any])
async def login_user(
    request: LoginRequest,
    db = Depends(get_db)
):
    """
    Login user with email and password
    
    Authenticates user credentials and returns session information.
    """
    try:
        auth = get_auth()
        
        # Sign in user with Supabase
        result = await auth.sign_in(
            email=request.email,
            password=request.password
        )
        
        return {
            "success": True,
            "message": "Login successful",
            "user": result["user"],
            "session": result["session"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/logout", response_model=BaseResponse)
async def logout_user(
    token: str,
    db = Depends(get_db)
):
    """
    Logout current user
    
    Invalidates the current session token.
    """
    try:
        auth = get_auth()
        
        # Sign out user
        success = await auth.sign_out(token)
        
        if success:
            return BaseResponse(message="Logout successful")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Logout failed"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )

@router.post("/reset-password", response_model=BaseResponse)
async def reset_password(
    email: str,
    db = Depends(get_db)
):
    """
    Send password reset email
    
    Sends a password reset email to the specified address.
    """
    try:
        auth = get_auth()
        
        # Send password reset email
        success = await auth.reset_password(email)
        
        if success:
            return BaseResponse(message="Password reset email sent")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to send password reset email"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Password reset failed: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    token: str,
    db = Depends(get_db)
):
    """
    Get current user information
    
    Returns the current authenticated user's profile information.
    """
    try:
        auth = get_auth()
        
        # Verify token and get user info
        user = await auth.verify_token(token)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        
        return UserResponse(**user)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user info: {str(e)}"
        )

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    updates: Dict[str, Any],
    token: str,
    db = Depends(get_db)
):
    """
    Update user profile
    
    Updates the current user's profile information.
    """
    try:
        auth = get_auth()
        
        # Update user profile
        user = await auth.update_user_profile(token, updates)
        
        return UserResponse(**user)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Profile update failed: {str(e)}"
        )

@router.get("/verify-token", response_model=BaseResponse)
async def verify_token(
    token: str,
    db = Depends(get_db)
):
    """
    Verify authentication token
    
    Validates the provided authentication token.
    """
    try:
        auth = get_auth()
        
        # Verify token
        user = await auth.verify_token(token)
        
        if user:
            return BaseResponse(message="Token is valid")
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token verification failed: {str(e)}"
        )
