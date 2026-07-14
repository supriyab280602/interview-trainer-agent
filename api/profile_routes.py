from fastapi import APIRouter, Depends, HTTPException, Header, Request, status
from typing import Optional
from api.auth_routes import get_current_user, get_auth_service
from schemas.interview import ProfileCreateRequest

router = APIRouter(prefix="/api/profile", tags=["Profiles"])

@router.get("")
async def get_profile(current_user: dict = Depends(get_current_user)):
    """
    Retrieve currently active career profile configurations and credentials.
    """
    current_user.pop("password_hash", None)
    return current_user


@router.put("")
async def update_profile(
    req: ProfileCreateRequest,
    current_user: dict = Depends(get_current_user),
    auth_service = Depends(get_auth_service)
):
    """
    Create or update a career profile inside the user's account.
    """
    updated_user = await auth_service.create_or_update_profile(
        email=current_user["email"],
        profile_name=req.profile_name,
        exp_level=req.experience_level,
        role=req.target_role
    )
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update career profile settings."
        )
    updated_user.pop("password_hash", None)
    return updated_user
