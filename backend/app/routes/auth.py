from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timedelta
from app.schemas.auth_schema import UserRegister, UserLogin, TokenResponse, UserResponse
from app.services.supabase_service import supabase_client, DatabaseService
from app.utils.helpers import hash_password, verify_password, create_access_token
from app.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse)
async def register(payload: UserRegister):
    email = payload.email.lower().strip()
    password = payload.password
    
    # 1. Supabase Mode
    if supabase_client:
        try:
            auth_response = supabase_client.auth.sign_up({
                "email": email,
                "password": password
            })
            if auth_response and auth_response.session:
                user = auth_response.user
                session = auth_response.session
                return {
                    "access_token": session.access_token,
                    "token_type": "bearer",
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "created_at": user.created_at
                    }
                }
            else:
                # Registration successful but verification email might be sent
                raise HTTPException(
                    status_code=status.HTTP_201_CREATED,
                    detail="Registration successful. Please check your email for verification."
                )
        except Exception as e:
            # Fall back to check if it's already there or throw error
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
            
    # 2. SQLite Fallback Mode
    existing_user = DatabaseService.get_local_user_by_email(email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
        
    hashed = hash_password(password)
    try:
        user_dict = DatabaseService.create_local_user(email, hashed)
        # Generate token
        token = create_access_token({"sub": user_dict["id"], "email": email})
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": user_dict
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin):
    email = payload.email.lower().strip()
    password = payload.password
    
    # 1. Supabase Mode
    if supabase_client:
        try:
            auth_response = supabase_client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            if auth_response and auth_response.session:
                user = auth_response.user
                session = auth_response.session
                return {
                    "access_token": session.access_token,
                    "token_type": "bearer",
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "created_at": user.created_at
                    }
                }
        except Exception:
            pass
            
    # 2. SQLite Fallback Mode
    user = DatabaseService.get_local_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
        
    if not verify_password(user["hashed_password"], password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
        
    token = create_access_token({"sub": user["id"], "email": email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "created_at": user["created_at"]
        }
    }

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "created_at": datetime.utcnow() # Default fallback value if not stored locally
    }

@router.get("/users")
async def get_users(current_user: dict = Depends(get_current_user)):
    # Verify current user is admin
    if current_user["email"] != "admin@interview.ai":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only system administrator can access user lists."
        )
    try:
        users = DatabaseService.get_all_local_users()
        return users
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch users: {str(e)}"
        )

@router.delete("/users/{user_id}")
async def delete_user(user_id: str, current_user: dict = Depends(get_current_user)):
    # Verify current user is admin
    if current_user["email"] != "admin@interview.ai":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only system administrator can delete users."
        )
        
    # Prevent admin from deleting themselves
    if current_user["id"] == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own admin account."
        )
        
    try:
        success = DatabaseService.delete_local_user(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or deletion failed."
            )
        return {"detail": "User and associated history deleted successfully."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )
