from fastapi import APIRouter, Depends, HTTPException, Header, Request, status
from typing import Optional
from schemas.auth import SignupRequest, LoginRequest
from services.auth_service import AuthService
from services.cloudant_service import CloudantService
from schemas.interview import ProfileCreateRequest

router = APIRouter(prefix="/api", tags=["Authentication"])

# Dependency providers
def get_auth_service(request: Request) -> AuthService:
    return request.app.state.auth_service

def get_db_service(request: Request) -> CloudantService:
    return request.app.state.db_service

async def get_current_user(x_session_id: Optional[str] = Header(None), auth_service: AuthService = Depends(get_auth_service)):
    """
    Dependency to fetch authenticated user using session header.
    Throws HTTP 401 if validation fails.
    """
    if not x_session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session ID header (X-Session-ID) is missing"
        )
    user = await auth_service.get_user_by_session(x_session_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )
    return user


@router.post("/signup")
async def signup(req: SignupRequest, auth_service: AuthService = Depends(get_auth_service)):
    """
    Endpoint to sign up a new user account.
    """
    result = await auth_service.signup(req)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address already registered"
        )
    return {"message": "Account created successfully", "user": result}


@router.post("/login")
async def login(req: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    """
    Endpoint to log in an existing user and retrieve session ID.
    """
    result = await auth_service.login(req)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    return result


@router.post("/logout")
async def logout(x_session_id: Optional[str] = Header(None), auth_service: AuthService = Depends(get_auth_service)):
    """
    Endpoint to log out the user and destroy the session.
    """
    if not x_session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session ID header missing"
        )
    success = await auth_service.logout(x_session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return {"message": "Logged out successfully"}
# Profile routes have been migrated to api/profile_routes.py
